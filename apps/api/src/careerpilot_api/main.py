"""FastAPI composition root with local identity and layered authorization."""

from __future__ import annotations

import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.contracts import (
    AnalysisCreateRequest,
    AnalysisResponse,
    AuditEventResponse,
    CurrentContextResponse,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    LocalLoginRequest,
    LocalUserResponse,
    MembershipResponse,
    MembershipRoleRequest,
    ProfileCreateRequest,
    ProfileResponse,
    SessionResponse,
    TenantSummary,
)
from careerpilot_api.observability import configure_logging, get_tracer
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_api.security import (
    AuthenticationError,
    InMemoryIdentityAccess,
    LastOwnerError,
    TenantMembershipError,
)
from careerpilot_core import (
    AccessDeniedError,
    AccessPolicy,
    AuditEventDraft,
    AuthorizationContext,
    CareerJourneyService,
    Permission,
    ProfileNotFoundError,
    Role,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from starlette.middleware.base import RequestResponseEndpoint

CORRELATION_HEADER = "X-Correlation-ID"
TENANT_HEADER = "X-CareerPilot-Tenant-ID"


def _correlation_id(request: Request) -> str:
    return str(request.state.correlation_id)


def _validation_fields(error: RequestValidationError) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"] if part != "body")
        fields.setdefault(location or "request", []).append(str(detail["msg"]))
    return fields


def _safe_error(
    request: Request,
    *,
    code: str,
    message: str,
    status_code: int,
    fields: dict[str, list[str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    correlation_id = _correlation_id(request)
    response_headers = {CORRELATION_HEADER: correlation_id, **(headers or {})}
    body = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            correlation_id=correlation_id,
            fields=fields,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers=response_headers,
    )


def create_app(
    service_factory: Callable[[], CareerJourneyService] | None = None,
    environment: str | None = None,
) -> FastAPI:
    """Build one isolated app with process-local identity, data, and audit state."""
    audit_log = InMemoryAuditLog()
    access_policy = AccessPolicy()
    repository = InMemoryProfileRepository()
    selected_environment = (
        environment
        if environment is not None
        else os.environ.get("CAREERPILOT_ENVIRONMENT", "local")
    )
    identity_access = InMemoryIdentityAccess(
        audit_log,
        environment=selected_environment,
    )
    service = (
        service_factory()
        if service_factory
        else CareerJourneyService(repository, access_policy, audit_log)
    )
    logger = configure_logging()
    tracer = get_tracer()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        logger.info("application_started")
        yield
        logger.info("application_stopped")

    app = FastAPI(
        title="CareerPilot API",
        version="0.3.0",
        description="Local multi-tenant security foundation; no production identity.",
        lifespan=lifespan,
        responses={500: {"model": ErrorResponse}},
    )
    app.state.audit_log = audit_log
    app.state.identity_access = identity_access
    app.state.repository = repository
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            CORRELATION_HEADER,
            TENANT_HEADER,
        ],
        expose_headers=[CORRELATION_HEADER],
    )

    @app.middleware("http")
    async def authentication_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        public_paths = {
            "/api/v1/dev/sessions",
            "/api/v1/dev/users",
            "/docs",
            "/health/live",
            "/health/ready",
            "/openapi.json",
        }
        if (
            request.url.path.startswith("/api/v1/")
            and request.url.path not in public_paths
        ):
            authorization = request.headers.get("Authorization", "")
            scheme, _, token = authorization.partition(" ")
            tenant_id = request.headers.get(TENANT_HEADER, "")
            if scheme.casefold() != "bearer" or not token:
                return _safe_error(
                    request,
                    code="authentication_required",
                    message="Sign in with a valid local development session.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            if not tenant_id:
                return _safe_error(
                    request,
                    code="access_denied",
                    message="You do not have permission to perform this action.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            purpose = "personal_career_support"
            if request.url.path == "/api/v1/audit-events":
                purpose = "security_review"
            elif request.url.path.startswith("/api/v1/memberships/"):
                purpose = "tenant_administration"
            try:
                request.state.authorization_context = identity_access.context_for(
                    token,
                    tenant_id,
                    _correlation_id(request),
                    purpose=purpose,
                )
            except AuthenticationError:
                return _safe_error(
                    request,
                    code="authentication_required",
                    message="Sign in with a valid local development session.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except TenantMembershipError:
                return _safe_error(
                    request,
                    code="access_denied",
                    message="You do not have permission to perform this action.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return await call_next(request)

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
        return _safe_error(
            request,
            code="invalid_request",
            message="Please correct the highlighted fields and try again.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            fields=_validation_fields(error),
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error(
        request: Request, _error: AuthenticationError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="authentication_required",
            message="Sign in with a valid local development session.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(TenantMembershipError)
    @app.exception_handler(AccessDeniedError)
    async def authorization_error(request: Request, _error: Exception) -> JSONResponse:
        return _safe_error(
            request,
            code="access_denied",
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(LastOwnerError)
    async def last_owner_error(
        request: Request, _error: LastOwnerError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="role_change_conflict",
            message="A personal workspace must keep at least one owner.",
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _error: Exception) -> JSONResponse:
        logger.error(
            "unexpected_request_error",
            extra={"correlation_id": _correlation_id(request)},
        )
        return _safe_error(
            request,
            code="internal_error",
            message="The request could not be completed. Please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def request_context(request: Request) -> AuthorizationContext:
        context = getattr(request.state, "authorization_context", None)
        if not isinstance(context, AuthorizationContext):
            raise AuthenticationError
        return context

    def audit_policy(
        context: AuthorizationContext,
        permission: Permission,
        *,
        allowed_reason: str,
    ) -> None:
        decision = access_policy.decide(context, permission)
        audit_log.append(
            AuditEventDraft(
                tenant_id=context.tenant_id,
                actor_id=context.actor_id,
                action=permission,
                outcome="allowed" if decision.allowed else "denied",
                reason=allowed_reason if decision.allowed else decision.reason,
                correlation_id=context.correlation_id,
            )
        )
        if not decision.allowed:
            raise AccessDeniedError(permission, decision.reason)

    @app.get("/health/live", response_model=HealthResponse, tags=["health"])
    async def live() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/health/ready", response_model=HealthResponse, tags=["health"])
    async def ready() -> HealthResponse:
        return HealthResponse(status="ready")

    @app.get(
        "/api/v1/dev/users",
        response_model=list[LocalUserResponse],
        tags=["local-auth"],
    )
    async def local_users() -> list[LocalUserResponse]:
        return [
            LocalUserResponse(
                local_user_id=user.login_id,
                display_name=user.actor.display_name,
            )
            for user in identity_access.local_users()
        ]

    @app.post(
        "/api/v1/dev/sessions",
        response_model=SessionResponse,
        responses={401: {"model": ErrorResponse}},
        tags=["local-auth"],
    )
    async def local_login(
        body: LocalLoginRequest, request: Request, response: Response
    ) -> SessionResponse:
        session = identity_access.login(body.local_user_id, _correlation_id(request))
        response.headers["Cache-Control"] = "no-store"
        actor = identity_access.actor(session.actor_id)
        if actor is None:
            raise AuthenticationError
        tenants = []
        for membership in identity_access.memberships_for_actor(actor.actor_id):
            tenant = identity_access.tenant(membership.tenant_id)
            if tenant:
                tenants.append(
                    TenantSummary(
                        tenant_id=tenant.tenant_id,
                        display_name=tenant.display_name,
                        role=membership.role,
                    )
                )
        return SessionResponse(
            access_token=session.token,
            actor_id=actor.actor_id,
            display_name=actor.display_name,
            tenants=tenants,
        )

    @app.get(
        "/api/v1/me",
        response_model=CurrentContextResponse,
        responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
        tags=["identity"],
    )
    async def current_context(request: Request) -> CurrentContextResponse:
        context = request_context(request)
        actor = identity_access.actor(context.actor_id)
        tenant = identity_access.tenant(context.tenant_id)
        if actor is None or tenant is None:
            raise AuthenticationError
        return CurrentContextResponse(
            actor_id=actor.actor_id,
            display_name=actor.display_name,
            tenant_id=tenant.tenant_id,
            tenant_name=tenant.display_name,
            role=context.role,
        )

    @app.post(
        "/api/v1/profiles",
        response_model=ProfileResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
        tags=["journey"],
    )
    async def create_profile(
        body: ProfileCreateRequest, request: Request
    ) -> ProfileResponse:
        context = request_context(request)
        profile = service.create_profile(
            context, body.display_name, body.professional_summary
        )
        return ProfileResponse(
            profile_id=profile.profile_id,
            display_name=profile.display_name,
        )

    @app.post(
        "/api/v1/analyses",
        response_model=AnalysisResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
        tags=["journey"],
    )
    async def create_analysis(
        body: AnalysisCreateRequest, request: Request
    ) -> Response:
        context = request_context(request)
        try:
            analysis = service.analyze_job(
                context, body.profile_id, body.job_description
            )
        except ProfileNotFoundError:
            return _safe_error(
                request,
                code="profile_not_found",
                message="The profile is unavailable. Create it again and retry.",
                status_code=status.HTTP_404_NOT_FOUND,
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

    @app.get(
        "/api/v1/audit-events",
        response_model=list[AuditEventResponse],
        responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
        tags=["audit"],
    )
    async def audit_events(request: Request) -> list[AuditEventResponse]:
        context = request_context(request)
        audit_policy(context, Permission.AUDIT_VIEW, allowed_reason="audit_viewed")
        return [
            AuditEventResponse.model_validate(event, from_attributes=True)
            for event in audit_log.list_for_tenant(context.tenant_id)
        ]

    @app.patch(
        "/api/v1/memberships/{actor_id}",
        response_model=MembershipResponse,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            409: {"model": ErrorResponse},
        },
        tags=["identity"],
    )
    async def change_role(
        actor_id: str, body: MembershipRoleRequest, request: Request
    ) -> MembershipResponse:
        context = request_context(request)
        audit_policy(
            context,
            Permission.MEMBERSHIP_MANAGE,
            allowed_reason="membership_role_change_allowed",
        )
        role = Role(body.role)
        try:
            membership = identity_access.set_role(actor_id, context.tenant_id, role)
        except LastOwnerError:
            audit_log.append(
                AuditEventDraft(
                    tenant_id=context.tenant_id,
                    actor_id=context.actor_id,
                    action="membership.role_changed",
                    outcome="denied",
                    reason="last_owner_required",
                    correlation_id=context.correlation_id,
                    resource_type="membership",
                    resource_id=actor_id,
                )
            )
            raise
        audit_log.append(
            AuditEventDraft(
                tenant_id=context.tenant_id,
                actor_id=context.actor_id,
                action="membership.role_changed",
                outcome="allowed",
                reason=role,
                correlation_id=context.correlation_id,
                resource_type="membership",
                resource_id=actor_id,
            )
        )
        return MembershipResponse(
            actor_id=membership.actor_id,
            tenant_id=membership.tenant_id,
            role=membership.role,
        )

    return app


app = create_app()
