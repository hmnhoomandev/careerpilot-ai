"""Narrow independently runnable HTTP surface for the ADK specialist."""

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from careerpilot_google_adk.config import build_service
from careerpilot_google_adk.errors import SpecialistError
from careerpilot_google_adk.models import ResearchRequest, ResearchResult
from careerpilot_google_adk.service import ResearchService


def create_app(service: ResearchService | None = None) -> FastAPI:
    app = FastAPI(title="CareerPilot Google ADK Specialist", version="0.9.0")
    selected = service or build_service()

    @app.exception_handler(SpecialistError)
    async def specialist_error_handler(
        _request: Request, error: SpecialistError
    ) -> JSONResponse:
        status = {
            "specialist_unavailable": 503,
            "provider_outage": 503,
            "provider_timeout": 504,
            "provider_quota_exceeded": 429,
        }.get(error.code, 422)
        return JSONResponse(status_code=status, content={"detail": error.code})

    @app.post("/v1/research", response_model=ResearchResult)
    async def research(
        payload: ResearchRequest,
        x_careerpilot_service: str = Header(),
    ) -> ResearchResult:
        if x_careerpilot_service != "careerpilot-main-api":
            raise HTTPException(status_code=403, detail="service_identity_denied")
        return await selected.research(payload)

    return app


app = create_app()
