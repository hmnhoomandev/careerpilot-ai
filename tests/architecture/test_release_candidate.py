"""Release metadata and non-deployment safety contracts for Phase 20."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.20.0-rc.1"


@pytest.mark.architecture
def test_release_version_is_consistent_and_explicitly_not_production_go() -> None:
    manifest = json.loads(
        (ROOT / "release/release-manifest.json").read_text(encoding="utf-8")
    )
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == VERSION
    assert manifest["release_version"] == VERSION
    assert manifest["release_kind"] == "local_source_release_candidate"
    assert manifest["production_decision"] == "no_go"
    assert manifest["artifact_publication"] == "not_authorized"
    assert manifest["deployment"] == "not_authorized"
    assert manifest["cost_chf"] == 0
    assert len(manifest["required_production_evidence"]) >= 8


@pytest.mark.architecture
def test_unsigned_candidate_cannot_be_described_as_signed() -> None:
    manifest = json.loads(
        (ROOT / "release/release-manifest.json").read_text(encoding="utf-8")
    )
    signature = manifest["artifact_signature"]
    assert signature == "blocked_pending_trusted_ci_identity_and_registry"
    assert "signed" not in signature


@pytest.mark.architecture
def test_release_workflow_has_readiness_gate_but_no_deploy_or_publish() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "scripts/run_release_readiness.py" in workflow
    forbidden = ("gcloud run deploy", "terraform apply", "tofu apply", "docker push")
    assert all(command not in workflow for command in forbidden)
