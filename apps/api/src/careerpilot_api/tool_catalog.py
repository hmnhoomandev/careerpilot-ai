"""CareerPilot capability catalog backed by existing deterministic services."""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

from careerpilot_api.tool_contracts import (
    ApprovalRequestInput,
    ApprovalRequestOutput,
    AuditLookupInput,
    AuditLookupOutput,
    CandidateMatchInput,
    CandidateMatchOutput,
    CostEstimateInput,
    CostEstimateOutput,
    EvidenceRetrievalInput,
    EvidenceRetrievalOutput,
    EvidenceVerificationInput,
    EvidenceVerificationOutput,
    JobIngestionInput,
    JobIngestionOutput,
    ProfileLookupInput,
    ProfileLookupOutput,
    SkillTaxonomyInput,
    SkillTaxonomyOutput,
    ToolAuditEvent,
    ToolCitation,
    ToolPassage,
)
from careerpilot_api.tool_runtime import ToolDefinition, ToolRegistry
from careerpilot_core import (
    Permission,
    ToolCapability,
    ToolRisk,
)

if TYPE_CHECKING:
    from careerpilot_api.audit import InMemoryAuditLog
    from careerpilot_core import AuthorizationContext, CareerJourneyService, RagService

TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9+#.-]{1,}")
SYNTHETIC_SKILLS = (
    "Accessibility",
    "FastAPI",
    "Google Cloud",
    "PostgreSQL",
    "Python",
    "React",
    "Security",
    "SQL",
    "TypeScript",
)
MIN_CLAIM_TERM_COVERAGE = 0.5


def build_tool_registry(
    journey: CareerJourneyService,
    rag: RagService,
    audit_log: InMemoryAuditLog,
) -> ToolRegistry:
    """Register the complete Phase 6 catalog in one auditable location."""
    registry = ToolRegistry()

    async def profile_lookup(
        context: AuthorizationContext, payload: ProfileLookupInput
    ) -> ProfileLookupOutput:
        profile = journey.get_profile(context, payload.profile_id)
        return ProfileLookupOutput(
            profile_id=profile.profile_id,
            display_name=profile.display_name,
            professional_summary=profile.professional_summary,
            skills=[skill.name for skill in profile.skills],
            version=profile.version,
        )

    async def evidence_retrieval(
        context: AuthorizationContext, payload: EvidenceRetrievalInput
    ) -> EvidenceRetrievalOutput:
        result = rag.search(context, payload.query, payload.limit)
        return EvidenceRetrievalOutput(
            passages=[
                ToolPassage(
                    content=passage.content,
                    injection_risk=passage.injection_risk,
                    citation=_citation(passage.citation),
                )
                for passage in result.passages
            ]
        )

    async def job_ingestion(
        context: AuthorizationContext, payload: JobIngestionInput
    ) -> JobIngestionOutput:
        analysis = journey.analyze_job(
            context, payload.profile_id, payload.job_description
        )
        return JobIngestionOutput(
            analysis_id=analysis.analysis_id,
            profile_id=analysis.profile_id,
            headline=analysis.headline,
            shared_terms=list(analysis.shared_terms),
            disclaimer=analysis.disclaimer,
        )

    async def skill_taxonomy(
        _context: AuthorizationContext, payload: SkillTaxonomyInput
    ) -> SkillTaxonomyOutput:
        query_terms = set(TOKEN_PATTERN.findall(payload.query.casefold()))
        ranked = sorted(
            SYNTHETIC_SKILLS,
            key=lambda skill: (
                not bool(query_terms & set(TOKEN_PATTERN.findall(skill.casefold()))),
                skill,
            ),
        )
        matched = [
            skill
            for skill in ranked
            if query_terms & set(TOKEN_PATTERN.findall(skill.casefold()))
        ]
        return SkillTaxonomyOutput(canonical_skills=matched[: payload.limit])

    async def candidate_match(
        context: AuthorizationContext, payload: CandidateMatchInput
    ) -> CandidateMatchOutput:
        analysis = journey.analyze_job(
            context, payload.profile_id, payload.job_description
        )
        job_terms = set(TOKEN_PATTERN.findall(payload.job_description.casefold()))
        supported = list(analysis.shared_terms)
        score = round(100 * len(supported) / max(len(job_terms), 1))
        return CandidateMatchOutput(
            supported_terms=supported,
            score_percent=min(score, 100),
            explanation=(
                "Deterministic exact-term overlap only; no qualification or hiring "
                "decision is inferred."
            ),
        )

    async def evidence_verification(
        context: AuthorizationContext, payload: EvidenceVerificationInput
    ) -> EvidenceVerificationOutput:
        result = rag.search(context, payload.claim, 5)
        claim_terms = set(TOKEN_PATTERN.findall(payload.claim.casefold()))
        supported = [
            passage
            for passage in result.passages
            if claim_terms
            and len(
                claim_terms & set(TOKEN_PATTERN.findall(passage.content.casefold()))
            )
            / len(claim_terms)
            >= MIN_CLAIM_TERM_COVERAGE
        ]
        citations = [_citation(passage.citation) for passage in supported]
        return EvidenceVerificationOutput(
            status="supported" if citations else "unsupported",
            citations=citations,
            suggestion_requires_confirmation=not bool(citations),
        )

    async def approval_request(
        _context: AuthorizationContext, _payload: ApprovalRequestInput
    ) -> ApprovalRequestOutput:
        return ApprovalRequestOutput(approval_id=str(uuid.uuid4()))

    async def audit_lookup(
        context: AuthorizationContext, payload: AuditLookupInput
    ) -> AuditLookupOutput:
        events = audit_log.list_for_tenant(context.tenant_id)[-payload.limit :]
        return AuditLookupOutput(
            events=[
                ToolAuditEvent(
                    event_id=event.event_id,
                    occurred_at=event.occurred_at,
                    action=event.action,
                    outcome=event.outcome,
                    reason=event.reason,
                    correlation_id=event.correlation_id,
                )
                for event in events
            ]
        )

    async def cost_estimate(
        _context: AuthorizationContext, payload: CostEstimateInput
    ) -> CostEstimateOutput:
        return CostEstimateOutput(
            note=(
                f"{payload.units} {payload.workflow} unit(s) use only local "
                "deterministic components; this estimate does not authorize spending."
            )
        )

    definitions = (
        ToolDefinition(
            _capability(
                "profile.lookup",
                "Read one authorized profile.",
                Permission.PROFILE_READ,
                mcp=True,
            ),
            ProfileLookupInput,
            ProfileLookupOutput,
            profile_lookup,
        ),
        ToolDefinition(
            _capability(
                "evidence.retrieve",
                "Return authorized cited passages.",
                Permission.DOCUMENT_READ,
                mcp=True,
            ),
            EvidenceRetrievalInput,
            EvidenceRetrievalOutput,
            evidence_retrieval,
        ),
        ToolDefinition(
            _capability(
                "job.ingest",
                "Validate and analyze user-supplied job text.",
                Permission.ANALYSIS_RUN,
                side_effects=True,
                idempotent=True,
            ),
            JobIngestionInput,
            JobIngestionOutput,
            job_ingestion,
        ),
        ToolDefinition(
            _capability(
                "skill.taxonomy",
                "Map exact terms to the local synthetic taxonomy.",
                Permission.TOOL_INVOKE,
                mcp=True,
            ),
            SkillTaxonomyInput,
            SkillTaxonomyOutput,
            skill_taxonomy,
        ),
        ToolDefinition(
            _capability(
                "candidate.match",
                "Compute deterministic profile/job term overlap.",
                Permission.ANALYSIS_RUN,
            ),
            CandidateMatchInput,
            CandidateMatchOutput,
            candidate_match,
        ),
        ToolDefinition(
            _capability(
                "evidence.verify",
                "Check whether retrieved evidence supports a claim.",
                Permission.DOCUMENT_READ,
            ),
            EvidenceVerificationInput,
            EvidenceVerificationOutput,
            evidence_verification,
        ),
        ToolDefinition(
            _capability(
                "approval.request",
                "Create a pending request without executing its action.",
                Permission.TOOL_INVOKE,
                risk=ToolRisk.HIGH,
                side_effects=True,
                idempotent=True,
                rate_limit=5,
            ),
            ApprovalRequestInput,
            ApprovalRequestOutput,
            approval_request,
        ),
        ToolDefinition(
            _capability(
                "audit.lookup",
                "Read minimized tenant audit facts.",
                Permission.AUDIT_VIEW,
            ),
            AuditLookupInput,
            AuditLookupOutput,
            audit_lookup,
        ),
        ToolDefinition(
            _capability(
                "cost.estimate",
                "Estimate current local workflow cost without authorizing spend.",
                Permission.TOOL_INVOKE,
                mcp=True,
            ),
            CostEstimateInput,
            CostEstimateOutput,
            cost_estimate,
        ),
    )
    for definition in definitions:
        registry.register(definition)
    return registry


def _capability(
    name: str,
    description: str,
    permission: Permission,
    *,
    risk: ToolRisk = ToolRisk.READ_ONLY,
    side_effects: bool = False,
    idempotent: bool = False,
    rate_limit: int = 30,
    mcp: bool = False,
) -> ToolCapability:
    return ToolCapability(
        name=name,
        version="1.0.0",
        description=description,
        permission=permission,
        risk=risk,
        side_effects=side_effects,
        approval_required=False,
        timeout_seconds=2.0,
        max_retries=0 if side_effects else 1,
        idempotency_required=idempotent,
        rate_limit=rate_limit,
        rate_window_seconds=60,
        audit_action=f"tool.{name}",
        mcp_exposed=mcp,
    )


def _citation(citation: object) -> ToolCitation:
    return ToolCitation.model_validate(citation, from_attributes=True)
