"""FastAPI composition root for the deterministic walking skeleton."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from careerpilot_api.contracts import (
    AnalysisCreateRequest,
    AnalysisResponse,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    ProfileCreateRequest,
    ProfileResponse,
)
from careerpilot_api.observability import configure_logging, get_tracer
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_core import CareerJourneyService, ProfileNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from starlette.middleware.base import RequestResponseEndpoint

CORRELATION_HEADER = "X-Correlation-ID"


def _correlation_id(request: Request) -> str:
    return str(request.state.correlation_id)


def _validation_fields(error: RequestValidationError) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"] if part != "body")
        fields.setdefault(location or "request", []).append(str(detail["msg"]))
    return fields


def create_app(
    service_factory: Callable[[], CareerJourneyService] | None = None,
) -> FastAPI:
    """Build an isolated app instance so tests control temporary state."""
    repository = InMemoryProfileRepository()
    service = service_factory() if service_factory else CareerJourneyService(repository)
    logger = configure_logging()
    tracer = get_tracer()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        logger.info("application_started")
        yield
        logger.info("application_stopped")

    app = FastAPI(
        title="CareerPilot API",
        version="0.2.0",
        description="Deterministic local walking skeleton; no model calls.",
        lifespan=lifespan,
        responses={500: {"model": ErrorResponse}},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", CORRELATION_HEADER],
        expose_headers=[CORRELATION_HEADER],
    )

    @app.middleware("http")
    async def correlation_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        supplied = request.headers.get(CORRELATION_HEADER, "")
        try:
            correlation_id = str(uuid.UUID(supplied)) if supplied else str(uuid.uuid4())
        except ValueError:
            correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        started = time.perf_counter()
        with tracer.start_as_current_span("http.request") as span:
            span.set_attribute("careerpilot.correlation_id", correlation_id)
            span.set_attribute("http.request.method", request.method)
            response = await call_next(request)
            span.set_attribute("http.response.status_code", response.status_code)
        response.headers[CORRELATION_HEADER] = correlation_id
        logger.info(
            "request_completed",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(
                code="invalid_request",
                message="Please correct the highlighted fields and try again.",
                correlation_id=_correlation_id(request),
                fields=_validation_fields(error),
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _error: Exception) -> JSONResponse:
        correlation_id = _correlation_id(request)
        logger.error(
            "unexpected_request_error", extra={"correlation_id": correlation_id}
        )
        body = ErrorResponse(
            error=ErrorDetail(
                code="internal_error",
                message="The request could not be completed. Please try again.",
                correlation_id=correlation_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=body.model_dump(),
            headers={CORRELATION_HEADER: correlation_id},
        )

    @app.get("/health/live", response_model=HealthResponse, tags=["health"])
    async def live() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/health/ready", response_model=HealthResponse, tags=["health"])
    async def ready() -> HealthResponse:
        return HealthResponse(status="ready")

    @app.post(
        "/api/v1/profiles",
        response_model=ProfileResponse,
        status_code=status.HTTP_201_CREATED,
        responses={422: {"model": ErrorResponse}},
        tags=["journey"],
    )
    async def create_profile(
        body: ProfileCreateRequest,
    ) -> ProfileResponse:
        profile = service.create_profile(body.display_name, body.professional_summary)
        return ProfileResponse(
            profile_id=profile.profile_id,
            display_name=profile.display_name,
        )

    @app.post(
        "/api/v1/analyses",
        response_model=AnalysisResponse,
        status_code=status.HTTP_201_CREATED,
        responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
        tags=["journey"],
    )
    async def create_analysis(
        body: AnalysisCreateRequest,
        request: Request,
    ) -> Response:
        try:
            analysis = service.analyze_job(body.profile_id, body.job_description)
        except ProfileNotFoundError:
            error = ErrorResponse(
                error=ErrorDetail(
                    code="profile_not_found",
                    message="The profile is unavailable. Create it again and retry.",
                    correlation_id=_correlation_id(request),
                )
            )
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error.model_dump(),
            )
        response = AnalysisResponse(
            analysis_id=analysis.analysis_id,
            profile_id=analysis.profile_id,
            headline=analysis.headline,
            summary=analysis.summary,
            shared_terms=list(analysis.shared_terms),
            disclaimer=analysis.disclaimer,
            correlation_id=_correlation_id(request),
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.model_dump(),
        )

    return app


app = create_app()
