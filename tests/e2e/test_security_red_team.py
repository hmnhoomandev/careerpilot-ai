"""Versioned deterministic adversarial corpus across activated security controls."""

from __future__ import annotations

import json
from pathlib import Path

from careerpilot_api.document_processing import LocalDocumentScanner
from careerpilot_api.security_hardening import (
    UnsafeDestinationError,
    validate_outbound_destination,
)
from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    BudgetLedger,
    InjectionRisk,
    Permission,
    RagService,
    Role,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "agent-red-team-corpus-v1.json"


def test_security_red_team_corpus_has_all_required_categories_and_passes() -> None:
    fixture = json.loads(FIXTURE.read_text())
    assert fixture["version"] == "agent-red-team-corpus-v1"
    cases = fixture["cases"]
    assert {item["category"] for item in cases} >= {
        "direct_prompt_injection",
        "indirect_prompt_injection",
        "exfiltration",
        "tool_abuse",
        "authorization_bypass",
        "ssrf_exfiltration",
        "malicious_file",
        "denial_of_wallet",
    }
    for item in cases:
        assert _decision(item["control"], item["payload"]) == item["expected"], item[
            "id"
        ]


def _decision(control: str, payload: str) -> str:
    if control == "injection_detector":
        risk = RagService._risk_for(payload)  # noqa: SLF001 - evaluation probes policy
        return "blocked" if risk is InjectionRisk.SUSPECTED else "allowed"
    if control == "data_rights_permission":
        context = AuthorizationContext(
            "actor-sam", "tenant-ada", Role.MEMBER, "personal_career_support", "corr"
        )
        decision = AccessPolicy().decide(context, Permission.DATA_RIGHTS_MANAGE)
        return "allowed" if decision.allowed else "blocked"
    if control == "ssrf_policy":
        try:
            validate_outbound_destination(
                payload,
                resolved_addresses=("169.254.169.254",),
                allowed_hosts=frozenset({"169.254.169.254"}),
            )
        except UnsafeDestinationError:
            return "blocked"
        return "allowed"
    if control == "upload_scanner":
        result = LocalDocumentScanner().scan(
            "attack.pdf", "application/pdf", payload.encode()
        )
        return "allowed" if result.clean else "blocked"
    if control == "budget_ledger":
        return (
            "blocked"
            if BudgetLedger({"tenant-ada": 0}).remaining("tenant-ada") == 0
            else "allowed"
        )
    raise AssertionError(control)
