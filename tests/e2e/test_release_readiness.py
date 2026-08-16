"""Bounded local load, soak, concurrency, recovery and outage release evidence."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.run_release_readiness import build_report


def test_local_release_profile_passes_without_claiming_production_readiness() -> None:
    policy = json.loads(
        (Path(__file__).parents[1] / "fixtures/release-readiness-v1.json").read_text(
            encoding="utf-8"
        )
    )
    policy["local_profile"] = {
        "concurrency": 4,
        "load_requests": 40,
        "soak_requests": 50,
        "warmup_requests": 5,
    }

    report = build_report(policy)

    assert report["local_gates_passed"] is True
    assert report["production_gates_passed"] is False
    assert report["decision"] == "no_go_production"
    assert "synthetic_data_only" in report["limitations"]
    assert all(
        gate["reason"] == "measurement_missing"
        for gate in report["gates"]
        if gate["required_scope"] == "production"
    )
