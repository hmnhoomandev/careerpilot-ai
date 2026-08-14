"""Narrow internal API for the interview orchestration laboratory."""

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from careerpilot_openai_agents.approval import ApprovalCoordinator
from careerpilot_openai_agents.config import build_service
from careerpilot_openai_agents.errors import InterviewError
from careerpilot_openai_agents.guardrails import guard_tool
from careerpilot_openai_agents.models import (
    ApprovalDecision,
    ApprovalState,
    InterviewRequest,
    InterviewResult,
)
from careerpilot_openai_agents.service import InterviewService


def create_app(service: InterviewService | None = None) -> FastAPI:
    app = FastAPI(title="CareerPilot OpenAI Agents Laboratory", version="0.10.0")
    selected = service or build_service()
    approvals = ApprovalCoordinator()

    def authorize(service_identity: str) -> None:
        if service_identity != "careerpilot-main-api":
            raise HTTPException(status_code=403, detail="service_identity_denied")

    @app.exception_handler(InterviewError)
    async def error_handler(_request: Request, error: InterviewError) -> JSONResponse:
        status = 503 if error.code == "interview_unavailable" else 422
        return JSONResponse(status_code=status, content={"detail": error.code})

    @app.post("/v1/interviews", response_model=InterviewResult)
    async def interview(
        payload: InterviewRequest,
        x_careerpilot_service: str = Header(),
    ) -> InterviewResult:
        authorize(x_careerpilot_service)
        return await selected.run(payload)

    @app.post("/v1/feedback-approvals", response_model=ApprovalState)
    async def pause_feedback(
        payload: InterviewRequest,
        x_careerpilot_service: str = Header(),
    ) -> ApprovalState:
        authorize(x_careerpilot_service)
        guard_tool("prepare_feedback_for_review")
        return approvals.pause(payload)

    @app.post(
        "/v1/feedback-approvals/{approval_id}/decision",
        response_model=ApprovalState,
    )
    async def resume_feedback(
        approval_id: str,
        payload: ApprovalDecision,
        x_careerpilot_service: str = Header(),
    ) -> ApprovalState:
        authorize(x_careerpilot_service)
        return approvals.resume(
            approval_id,
            approve=payload.approve,
            expected_revision=payload.expected_revision,
            expected_action_hash=payload.expected_action_hash,
        )

    return app


app = create_app()
