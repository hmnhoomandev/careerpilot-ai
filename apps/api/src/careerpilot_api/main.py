"""FastAPI composition root with local identity and layered authorization."""

from __future__ import annotations

import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from careerpilot_api.analysis_contracts import (
    AnalysisGraphRequest,
    AnalysisGraphResponse,
)
from careerpilot_api.analysis_graph import build_analysis_graph
from careerpilot_api.analysis_service import (
    AnalysisGraphService,
    AnalysisRunNotFoundError,
)
from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.contracts import (
    AnalysisCreateRequest,
    AnalysisResponse,
    AuditEventResponse,
    CitationResponse,
    CurrentContextResponse,
    DocumentDeletionRequest,
    DocumentResponse,
    EducationContract,
    ErrorDetail,
    ErrorResponse,
    EvidenceCreateRequest,
    EvidenceResponse,
    ExperienceContract,
    HealthResponse,
    LocalLoginRequest,
    LocalUserResponse,
    MembershipResponse,
    MembershipRoleRequest,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievedPassageResponse,
    SessionResponse,
    TenantSummary,
)
from careerpilot_api.database import PostgresProfileRepository, create_postgres_engine
from careerpilot_api.document_processing import (
    BoundedDocumentParser,
    DeterministicHashEmbedder,
    InMemoryDocumentStorage,
    LocalDocumentScanner,
    LocalFilesystemDocumentStorage,
)
from careerpilot_api.model_providers import FakeAnalysisModelProvider
from careerpilot_api.observability import configure_logging, get_tracer
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_api.retrieval_repository import (
    InMemoryDocumentRepository,
    PostgresDocumentRepository,
)
from careerpilot_api.security import (
    AuthenticationError,
    InMemoryIdentityAccess,
    LastOwnerError,
    TenantMembershipError,
)
from careerpilot_api.tool_catalog import build_tool_registry
from careerpilot_api.tool_contracts import (
    ToolCapabilityResponse,
    ToolInvokeRequest,
    ToolInvokeResponse,
)
from careerpilot_api.tool_runtime import ToolExecutor
from careerpilot_core import (
    AccessDeniedError,
    AccessPolicy,
    AuditEventDraft,
    AuthorizationContext,
    CareerJourneyService,
    DeletionConfirmationError,
    DocumentNotFoundError,
    DocumentValidationError,
    Education,
    EvidenceValidationError,
    Experience,
    Permission,
    ProfileConflictError,
    ProfileNotFoundError,
    ProfileValidationError,
    RagService,
    ResourceAttributes,
    Role,
    ToolErrorCode,
    ToolExecutionError,
)
from careerpilot_core.rag_service import MAX_UPLOAD_BYTES

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
    """Build an app with local identity/audit and configured profile persistence."""
    audit_log = InMemoryAuditLog()
    access_policy = AccessPolicy()
    database_url = os.environ.get("CAREERPILOT_DATABASE_URL")
    engine = create_postgres_engine(database_url) if database_url else None
    repository = (
        PostgresProfileRepository(engine) if engine else InMemoryProfileRepository()
    )
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
    document_storage = (
        LocalFilesystemDocumentStorage(
            Path(os.environ.get("CAREERPILOT_DOCUMENT_ROOT", ".data/documents"))
        )
        if engine
        else InMemoryDocumentStorage()
    )
    document_repository = (
        PostgresDocumentRepository(engine) if engine else InMemoryDocumentRepository()
    )
    rag_service = RagService(
        repository,
        document_repository,
        document_storage,
        LocalDocumentScanner(),
        BoundedDocumentParser(),
        DeterministicHashEmbedder(),
        access_policy,
        audit_log,
    )
    tool_registry = build_tool_registry(service, rag_service, audit_log)
    tool_executor = ToolExecutor(tool_registry, access_policy, audit_log)
    analysis_provider = FakeAnalysisModelProvider()
    analysis_graph = build_analysis_graph(tool_executor, analysis_provider)
    analysis_graph_service = AnalysisGraphService(analysis_graph, access_policy)
    logger = configure_logging()
    tracer = get_tracer()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        logger.info("application_started")
        yield
        if engine:
            engine.dispose()
        logger.info("application_stopped")

    app = FastAPI(
        title="CareerPilot API",
        version="0.7.0",
        description="Tenant-safe evidence and checkpointed job-analysis graphs.",
        lifespan=lifespan,
        responses={500: {"model": ErrorResponse}},
    )
    app.state.audit_log = audit_log
    app.state.identity_access = identity_access
    app.state.repository = repository
    app.state.document_repository = document_repository
    app.state.document_storage = document_storage
    app.state.tool_registry = tool_registry
    app.state.tool_executor = tool_executor
    app.state.analysis_graph = analysis_graph
    app.state.analysis_graph_service = analysis_graph_service
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

    @app.exception_handler(ProfileConflictError)
    async def profile_conflict(
        request: Request, _error: ProfileConflictError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="profile_version_conflict",
            message="This profile changed since you opened it. Refresh and try again.",
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(ProfileNotFoundError)
    async def profile_not_found(
        request: Request, _error: ProfileNotFoundError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="profile_not_found",
            message="The profile is unavailable.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(EvidenceValidationError)
    async def evidence_validation(
        request: Request, error: EvidenceValidationError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="evidence_not_accepted",
            message="The evidence metadata did not meet the upload security policy.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            fields={error.field: [error.reason]},
        )

    @app.exception_handler(DocumentValidationError)
    async def document_validation(
        request: Request, error: DocumentValidationError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="document_not_accepted",
            message="The document did not meet the ingestion or retrieval policy.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            fields={error.field: [error.reason]},
        )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found(
        request: Request, _error: DocumentNotFoundError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="document_not_found",
            message="The document is unavailable.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(DeletionConfirmationError)
    async def deletion_confirmation(
        request: Request, _error: DeletionConfirmationError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="confirmation_required",
            message="Explicit human confirmation is required before deletion.",
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(ToolExecutionError)
    async def tool_execution_error(
        request: Request, error: ToolExecutionError
    ) -> JSONResponse:
        status_by_code = {
            ToolErrorCode.INVALID_INPUT: status.HTTP_422_UNPROCESSABLE_CONTENT,
            ToolErrorCode.UNAUTHORIZED: status.HTTP_403_FORBIDDEN,
            ToolErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ToolErrorCode.TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
            ToolErrorCode.RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
            ToolErrorCode.IDEMPOTENCY_CONFLICT: status.HTTP_409_CONFLICT,
            ToolErrorCode.INTERNAL: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        return _safe_error(
            request,
            code=error.code,
            message=error.message,
            status_code=status_by_code[error.code],
        )

    @app.exception_handler(AnalysisRunNotFoundError)
    async def analysis_run_not_found(
        request: Request, _error: AnalysisRunNotFoundError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="analysis_run_not_found",
            message="The analysis run is unavailable.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(ProfileValidationError)
    async def profile_validation(
        request: Request, error: ProfileValidationError
    ) -> JSONResponse:
        return _safe_error(
            request,
            code="profile_not_accepted",
            message="The profile did not meet the data quality policy.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            fields={error.field: [error.reason]},
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
            professional_summary=profile.professional_summary,
            version=profile.version,
            skills=[skill.name for skill in profile.skills],
            experiences=[],
            education=[],
        )

    @app.get(
        "/api/v1/profiles/{profile_id}",
        response_model=ProfileResponse,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
        },
        tags=["profiles"],
    )
    async def get_profile(profile_id: str, request: Request) -> Response:
        context = request_context(request)
        try:
            profile = service.get_profile(context, profile_id)
        except ProfileNotFoundError:
            return _safe_error(
                request,
                code="profile_not_found",
                message="The profile is unavailable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(
            content=ProfileResponse(
                profile_id=profile.profile_id,
                display_name=profile.display_name,
                professional_summary=profile.professional_summary,
                version=profile.version,
                skills=[skill.name for skill in profile.skills],
                experiences=[
                    ExperienceContract.model_validate(item, from_attributes=True)
                    for item in profile.experiences
                ],
                education=[
                    EducationContract.model_validate(item, from_attributes=True)
                    for item in profile.education
                ],
            ).model_dump()
        )

    @app.patch(
        "/api/v1/profiles/{profile_id}",
        response_model=ProfileResponse,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            409: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
        tags=["profiles"],
    )
    async def update_profile(
        profile_id: str, body: ProfileUpdateRequest, request: Request
    ) -> Response:
        context = request_context(request)
        try:
            profile = service.update_profile(
                context,
                profile_id,
                display_name=body.display_name,
                professional_summary=body.professional_summary,
                skill_names=tuple(body.skills),
                expected_version=body.expected_version,
                experiences=tuple(
                    Experience(
                        title=item.title,
                        organization=item.organization,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        description=item.description,
                    )
                    for item in body.experiences
                ),
                education=tuple(
                    Education(
                        institution=item.institution,
                        qualification=item.qualification,
                        start_date=item.start_date,
                        end_date=item.end_date,
                    )
                    for item in body.education
                ),
            )
        except ProfileNotFoundError:
            return _safe_error(
                request,
                code="profile_not_found",
                message="The profile is unavailable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(
            content=ProfileResponse(
                profile_id=profile.profile_id,
                display_name=profile.display_name,
                professional_summary=profile.professional_summary,
                version=profile.version,
                skills=[skill.name for skill in profile.skills],
                experiences=[
                    ExperienceContract.model_validate(item, from_attributes=True)
                    for item in profile.experiences
                ],
                education=[
                    EducationContract.model_validate(item, from_attributes=True)
                    for item in profile.education
                ],
            ).model_dump()
        )

    @app.post(
        "/api/v1/evidence",
        response_model=EvidenceResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
        tags=["evidence"],
    )
    async def add_evidence(
        body: EvidenceCreateRequest, request: Request
    ) -> EvidenceResponse:
        item = service.add_evidence(
            request_context(request),
            body.profile_id,
            title=body.title,
            filename=body.filename,
            media_type=body.media_type,
            size_bytes=body.size_bytes,
        )
        return EvidenceResponse(
            evidence_id=item.evidence_id,
            profile_id=item.profile_id,
            title=item.title,
            filename=item.filename,
            media_type=item.media_type,
            size_bytes=item.size_bytes,
            state=item.state,
            version=item.version,
        )

    @app.get(
        "/api/v1/profiles/{profile_id}/evidence",
        response_model=list[EvidenceResponse],
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
        },
        tags=["evidence"],
    )
    async def list_evidence(
        profile_id: str, request: Request
    ) -> list[EvidenceResponse]:
        return [
            EvidenceResponse(
                evidence_id=item.evidence_id,
                profile_id=item.profile_id,
                title=item.title,
                filename=item.filename,
                media_type=item.media_type,
                size_bytes=item.size_bytes,
                state=item.state,
                version=item.version,
            )
            for item in service.list_evidence(request_context(request), profile_id)
        ]

    def document_response(document: object) -> DocumentResponse:
        return DocumentResponse.model_validate(document, from_attributes=True)

    @app.post(
        "/api/v1/documents",
        response_model=DocumentResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["documents"],
    )
    async def upload_document(
        request: Request,
        profile_id: Annotated[str, Form()],
        title: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
    ) -> DocumentResponse:
        filename = file.filename or ""
        media_type = file.content_type or "application/octet-stream"
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        await file.close()
        document = rag_service.ingest(
            request_context(request),
            profile_id,
            title=title,
            filename=filename,
            media_type=media_type,
            content=content,
        )
        return document_response(document)

    @app.post(
        "/api/v1/retrieval/search",
        response_model=RetrievalSearchResponse,
        tags=["retrieval"],
    )
    async def search_documents(
        body: RetrievalSearchRequest, request: Request
    ) -> RetrievalSearchResponse:
        result = rag_service.search(
            request_context(request), body.query, limit=body.limit
        )
        return RetrievalSearchResponse(
            query=result.query,
            passages=[
                RetrievedPassageResponse(
                    content=passage.content,
                    score=passage.score,
                    injection_risk=passage.injection_risk,
                    citation=CitationResponse.model_validate(
                        passage.citation, from_attributes=True
                    ),
                )
                for passage in result.passages
            ],
            context=result.context,
            disclaimer=result.disclaimer,
        )

    @app.post(
        "/api/v1/documents/{document_id}/reindex",
        response_model=DocumentResponse,
        tags=["documents"],
    )
    async def reindex_document(document_id: str, request: Request) -> DocumentResponse:
        return document_response(
            rag_service.reindex(request_context(request), document_id)
        )

    @app.post(
        "/api/v1/documents/{document_id}/deletion",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["documents"],
    )
    async def delete_document(
        document_id: str, body: DocumentDeletionRequest, request: Request
    ) -> Response:
        rag_service.delete(
            request_context(request), document_id, confirmed=body.confirmed
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.get(
        "/api/v1/tools",
        response_model=list[ToolCapabilityResponse],
        tags=["tools"],
    )
    async def list_tools(request: Request) -> list[ToolCapabilityResponse]:
        context = request_context(request)
        access_policy.require(
            context,
            Permission.TOOL_INVOKE,
            ResourceAttributes(context.tenant_id, context.actor_id),
        )
        return [
            ToolCapabilityResponse(
                name=definition.capability.name,
                version=definition.capability.version,
                description=definition.capability.description,
                permission=definition.capability.permission,
                risk=definition.capability.risk,
                side_effects=definition.capability.side_effects,
                approval_required=definition.capability.approval_required,
                timeout_seconds=definition.capability.timeout_seconds,
                max_retries=definition.capability.max_retries,
                idempotency_required=definition.capability.idempotency_required,
                rate_limit=definition.capability.rate_limit,
                rate_window_seconds=definition.capability.rate_window_seconds,
                audit_action=definition.capability.audit_action,
                mcp_exposed=definition.capability.mcp_exposed,
                error_codes=[code.value for code in ToolErrorCode],
                input_schema=definition.input_model.model_json_schema(),
                output_schema=definition.output_model.model_json_schema(),
            )
            for definition in tool_registry.definitions()
        ]

    @app.post(
        "/api/v1/tools/{tool_name}/invoke",
        response_model=ToolInvokeResponse,
        tags=["tools"],
    )
    async def invoke_tool(
        tool_name: str, body: ToolInvokeRequest, request: Request
    ) -> ToolInvokeResponse:
        result = await tool_executor.execute(
            tool_name,
            request_context(request),
            body.arguments,
            body.idempotency_key,
        )
        return ToolInvokeResponse(
            tool_name=result.capability.name,
            tool_version=result.capability.version,
            correlation_id=_correlation_id(request),
            idempotent_replay=result.idempotent_replay,
            output=result.output,
        )

    def graph_response(state: dict[str, object]) -> AnalysisGraphResponse:
        return AnalysisGraphResponse(
            run_id=str(state["run_id"]),
            profile_id=str(state["profile_id"]),
            status=str(state.get("status", "unknown")),
            provider=analysis_provider.name,
            correlation_id=str(state["correlation_id"]),
            requirements=state.get("requirements"),  # type: ignore[arg-type]
            passages=state.get("passages", []),  # type: ignore[arg-type]
            match=state.get("match"),  # type: ignore[arg-type]
            gaps=state.get("gaps"),  # type: ignore[arg-type]
            verified=state.get("verified", []),  # type: ignore[arg-type]
            explanation=state.get("explanation"),  # type: ignore[arg-type]
            events=state.get("events", []),  # type: ignore[arg-type]
            error=state.get("error"),  # type: ignore[arg-type]
        )

    @app.post(
        "/api/v1/agent-runs",
        response_model=AnalysisGraphResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["agents"],
    )
    async def start_agent_run(
        body: AnalysisGraphRequest, request: Request
    ) -> AnalysisGraphResponse:
        state = await analysis_graph_service.start(
            request_context(request), body.profile_id, body.job_description
        )
        return graph_response(dict(state))

    @app.get(
        "/api/v1/agent-runs/{run_id}",
        response_model=AnalysisGraphResponse,
        tags=["agents"],
    )
    async def get_agent_run(run_id: str, request: Request) -> AnalysisGraphResponse:
        return graph_response(
            dict(analysis_graph_service.get(request_context(request), run_id))
        )

    @app.post(
        "/api/v1/agent-runs/{run_id}/cancel",
        response_model=AnalysisGraphResponse,
        tags=["agents"],
    )
    async def cancel_agent_run(run_id: str, request: Request) -> AnalysisGraphResponse:
        return graph_response(
            dict(analysis_graph_service.cancel(request_context(request), run_id))
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
