"""Policy tests for the optional, render-only GKE reference architecture."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parents[2]
KUSTOMIZATION = ROOT / "infrastructure" / "kubernetes" / "base"
IMAGE_DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
KUBECTL = shutil.which("kubectl")


def _render() -> list[dict[str, Any]]:
    """Render with the repository's kubectl client without contacting a cluster."""
    assert KUBECTL is not None
    # The executable and arguments are locally resolved constants;
    # no untrusted input enters them.
    result = subprocess.run(  # noqa: S603
        [KUBECTL, "kustomize", str(KUSTOMIZATION)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [item for item in yaml.safe_load_all(result.stdout) if item]


def _pod_specs(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        resource["spec"]["template"]["spec"]
        for resource in resources
        if resource["kind"] in {"Deployment", "Job"}
    ]


def test_reference_renders_deterministically_without_secret_values() -> None:
    first = _render()
    second = _render()
    assert first == second
    assert len(first) == 21
    assert not any(resource["kind"] == "Secret" for resource in first)
    assert not any(
        "kubectl apply" in path.read_text(encoding="utf-8")
        for path in KUSTOMIZATION.glob("*.yaml")
    )


def test_workloads_are_digest_pinned_restricted_and_bounded() -> None:
    resources = _render()
    for pod in _pod_specs(resources):
        assert pod["automountServiceAccountToken"] is False
        assert pod["securityContext"]["runAsNonRoot"] is True
        assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
        for container in pod["containers"]:
            assert IMAGE_DIGEST.search(container["image"])
            assert container["resources"]["requests"]
            assert container["resources"]["limits"]
            security = container["securityContext"]
            assert security["allowPrivilegeEscalation"] is False
            assert security["readOnlyRootFilesystem"] is True
            assert security["capabilities"]["drop"] == ["ALL"]


def test_deployments_have_safe_rollout_probes_scaling_and_disruption() -> None:
    resources = _render()
    deployments = {
        item["metadata"]["name"]: item
        for item in resources
        if item["kind"] == "Deployment"
    }
    assert set(deployments) == {"api", "web"}
    for deployment in deployments.values():
        rolling = deployment["spec"]["strategy"]["rollingUpdate"]
        assert rolling == {"maxSurge": 1, "maxUnavailable": 0}
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        assert {"startupProbe", "readinessProbe", "livenessProbe"} <= set(container)

    hpas = [item for item in resources if item["kind"] == "HorizontalPodAutoscaler"]
    pdbs = [item for item in resources if item["kind"] == "PodDisruptionBudget"]
    assert {item["metadata"]["name"] for item in hpas} == {"api", "web"}
    assert all(item["spec"]["minReplicas"] >= 2 for item in hpas)
    assert all(item["spec"]["minAvailable"] == 1 for item in pdbs)


def test_identity_network_and_migration_boundaries_fail_closed() -> None:
    resources = _render()
    accounts = [item for item in resources if item["kind"] == "ServiceAccount"]
    assert {item["metadata"]["name"] for item in accounts} == {
        "api",
        "web",
        "migration",
    }
    for account in accounts:
        annotation = account["metadata"]["annotations"][
            "iam.gke.io/gcp-service-account"
        ]
        assert annotation.endswith("@replace-with-project.iam.gserviceaccount.com")
        assert account["automountServiceAccountToken"] is False

    policies = {
        item["metadata"]["name"]
        for item in resources
        if item["kind"] == "NetworkPolicy"
    }
    assert {
        "default-deny",
        "allow-dns",
        "web-ingress",
        "web-to-api",
        "web-api-egress",
        "monitoring-ingress",
        "api-private-egress",
    } <= policies

    jobs = [item for item in resources if item["kind"] == "Job"]
    assert len(jobs) == 1
    job = jobs[0]
    assert (
        job["metadata"]["annotations"]["careerpilot.dev/release-order"]
        == "before-workload-rollout"
    )
    assert job["spec"]["backoffLimit"] == 0
    assert job["spec"]["template"]["spec"]["containers"][0]["command"] == ["alembic"]
