"""Graph path, retry, cancellation, and role-policy evidence."""

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from careerpilot_api.analysis_graph import AnalysisGraphState, build_analysis_graph
from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.document_processing import (
    BoundedDocumentParser,
    DeterministicHashEmbedder,
    InMemoryDocumentStorage,
    LocalDocumentScanner,
)
from careerpilot_api.model_providers import GeminiAnalysisModelProvider
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_api.retrieval_repository import InMemoryDocumentRepository
from careerpilot_api.tool_catalog import build_tool_registry
from careerpilot_api.tool_runtime import ToolExecutor
from careerpilot_core import (
    PHASE_7_ROLES,
    AccessPolicy,
    CareerJourneyService,
    JobRequirements,
    RagService,
    Role,
    RouteDecision,
)


class FlakyProvider:
    name = "flaky-fake"

    def __init__(self) -> None:
        self.attempts = 0

    async def route(self, _job_description: str) -> RouteDecision:
        return RouteDecision.ANALYZE

    async def extract_requirements(self, _job_description: str) -> JobRequirements:
        self.attempts += 1
        if self.attempts == 1:
            raise SyntheticConnectionError
        return JobRequirements("Synthetic role", (), ("Build synthetic systems",))


class SyntheticConnectionError(ConnectionError):
    """Transient failure used to exercise graph retry policy."""


class FakeToolResult:
    def __init__(self, output: dict[str, object]) -> None:
        self.output = output


class FakeToolExecutor:
    async def execute(
        self,
        name: str,
        _context: object,
        _arguments: dict[str, object],
    ) -> FakeToolResult:
        outputs: dict[str, dict[str, object]] = {
            "evidence.retrieve": {"passages": []},
            "candidate.match": {"supported_terms": [], "score_percent": 0},
            "evidence.verify": {
                "status": "unsupported",
                "citations": [],
                "suggestion_requires_confirmation": True,
            },
        }
        return FakeToolResult(outputs[name])


def _executor() -> ToolExecutor:
    audit = InMemoryAuditLog()
    policy = AccessPolicy()
    profiles = InMemoryProfileRepository()
    journey = CareerJourneyService(profiles, policy, audit)
    rag = RagService(
        profiles,
        InMemoryDocumentRepository(),
        InMemoryDocumentStorage(),
        LocalDocumentScanner(),
        BoundedDocumentParser(),
        DeterministicHashEmbedder(),
        policy,
        audit,
    )
    return ToolExecutor(build_tool_registry(journey, rag, audit), policy, audit)


@pytest.mark.asyncio
async def test_cancelled_graph_stops_after_intake_without_model_call() -> None:
    provider = FlakyProvider()
    graph = build_analysis_graph(_executor(), provider, InMemorySaver())
    state: AnalysisGraphState = {
        "run_id": "run-cancel",
        "profile_id": "profile-synthetic",
        "job_description": (
            "A sufficiently long synthetic job description that should never "
            "be processed."
        ),
        "actor_id": "actor-ada",
        "tenant_id": "tenant-ada",
        "role": Role.OWNER.value,
        "purpose": "personal_career_support",
        "correlation_id": "graph-cancel",
        "cancelled": True,
        "events": [],
    }
    result = await graph.ainvoke(
        state, config={"configurable": {"thread_id": "cancelled"}}
    )
    assert result["status"] == "cancelled"
    assert provider.attempts == 0
    assert [event["node"] for event in result["events"]] == ["intake"]


def test_role_dossiers_have_unique_ownership_and_safe_boundaries() -> None:
    assert len(PHASE_7_ROLES) == 8
    owned = [field for role in PHASE_7_ROLES for field in role.owns_state]
    assert len(owned) == len(set(owned))
    assert all(
        role.timeout_seconds > 0 and role.max_attempts > 0 for role in PHASE_7_ROLES
    )


def test_gemini_adapter_refuses_unapproved_external_transfer() -> None:
    with pytest.raises(PermissionError, match="external_model_transfer_not_authorized"):
        GeminiAnalysisModelProvider(
            object(),  # type: ignore[arg-type]
            model="gemini-live-disabled",
            external_transfer_authorized=False,
        )


@pytest.mark.asyncio
async def test_transient_model_failure_retries_and_checkpoint_replays_safely() -> None:
    provider = FlakyProvider()
    graph = build_analysis_graph(FakeToolExecutor(), provider, InMemorySaver())
    state: AnalysisGraphState = {
        "run_id": "run-retry",
        "profile_id": "profile-synthetic",
        "job_description": (
            "A sufficiently long synthetic job description for deterministic "
            "routing and retry verification."
        ),
        "actor_id": "actor-ada",
        "tenant_id": "tenant-ada",
        "role": Role.OWNER.value,
        "purpose": "personal_career_support",
        "correlation_id": "graph-retry",
        "cancelled": False,
        "events": [],
    }
    config = {"configurable": {"thread_id": "retry-checkpoint"}}
    first = await graph.ainvoke(state, config=config)
    resumed = await graph.ainvoke(None, config=config)
    assert provider.attempts == 2
    assert first["status"] == resumed["status"] == "completed"
    assert first["events"] == resumed["events"]
