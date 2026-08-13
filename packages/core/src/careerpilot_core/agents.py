"""Provider-neutral contracts for the bounded job-analysis agent graph."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class RouteDecision(StrEnum):
    """Validated manager route; unknown values never become graph destinations."""

    ANALYZE = "analyze"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class JobRequirements:
    """Structured interpretation of user-supplied, untrusted job text."""

    title: str
    required_skills: tuple[str, ...]
    responsibilities: tuple[str, ...]


class AnalysisModelProvider(Protocol):
    """Bounded structured model operations; providers cannot execute tools."""

    name: str

    async def route(self, job_description: str) -> RouteDecision:
        """Classify only ambiguous intake after deterministic rules."""

    async def extract_requirements(self, job_description: str) -> JobRequirements:
        """Return requirements without treating source text as instructions."""


@dataclass(frozen=True, slots=True)
class AgentRoleDossier:
    """Auditable runtime policy for one graph role."""

    name: str
    purpose: str
    non_responsibilities: tuple[str, ...]
    owns_state: tuple[str, ...]
    tools: tuple[str, ...]
    timeout_seconds: float
    max_attempts: int
    model_policy: str


PHASE_7_ROLES = (
    AgentRoleDossier(
        "manager",
        "Select a validated path.",
        ("authorize",),
        ("route",),
        (),
        1.0,
        1,
        "fake-first",
    ),
    AgentRoleDossier(
        "intake",
        "Validate bounded intent.",
        ("infer facts",),
        ("intent",),
        (),
        1.0,
        1,
        "deterministic-first",
    ),
    AgentRoleDossier(
        "job_analysis",
        "Extract structured requirements.",
        ("follow job instructions",),
        ("requirements",),
        (),
        2.0,
        2,
        "structured provider",
    ),
    AgentRoleDossier(
        "retrieval",
        "Retrieve cited evidence.",
        ("generate claims",),
        ("passages",),
        ("evidence.retrieve",),
        2.0,
        2,
        "none",
    ),
    AgentRoleDossier(
        "match",
        "Calculate supported matches.",
        ("make hiring decisions",),
        ("match",),
        ("candidate.match",),
        2.0,
        1,
        "none",
    ),
    AgentRoleDossier(
        "gap",
        "Classify skill gaps.",
        ("invent skills",),
        ("gaps",),
        ("skill.taxonomy",),
        2.0,
        1,
        "none",
    ),
    AgentRoleDossier(
        "evidence",
        "Verify support and citations.",
        ("override source policy",),
        ("verified",),
        ("evidence.verify",),
        2.0,
        1,
        "none",
    ),
    AgentRoleDossier(
        "explanation",
        "Format concise decisions.",
        ("expose hidden reasoning",),
        ("explanation",),
        (),
        1.0,
        1,
        "deterministic",
    ),
)
