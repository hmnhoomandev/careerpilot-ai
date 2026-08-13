"""Bounded execution, session isolation, timeout, policy, and telemetry."""

import asyncio

from careerpilot_google_adk.errors import (
    MalformedProviderOutputError,
    ProviderOutageError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    SpecialistUnavailableError,
    TransferNotAuthorizedError,
)
from careerpilot_google_adk.models import ResearchRequest, ResearchResult
from careerpilot_google_adk.provider import ResearchProvider
from careerpilot_google_adk.safety import inspect_request, validate_citations
from careerpilot_google_adk.telemetry import MetricSink, ResearchMetric


class ResearchService:
    def __init__(
        self,
        provider: ResearchProvider,
        *,
        enabled: bool = True,
        live_provider: bool = False,
        timeout_seconds: float = 20,
        metrics: MetricSink | None = None,
    ) -> None:
        self._provider = provider
        self._enabled = enabled
        self._live_provider = live_provider
        self._timeout = timeout_seconds
        self._metrics = metrics or MetricSink()
        self._sessions: dict[str, ResearchResult] = {}

    @staticmethod
    def _key(request: ResearchRequest) -> str:
        return f"{request.tenant_id}:{request.actor_id}:{request.session_id}"

    async def research(self, request: ResearchRequest) -> ResearchResult:
        if not self._enabled:
            raise SpecialistUnavailableError
        if self._live_provider and not (
            request.external_transfer_authorized and request.consent_recorded
        ):
            raise TransferNotAuthorizedError
        inspect_request(request)
        try:
            result = await asyncio.wait_for(
                self._provider.research(request), timeout=self._timeout
            )
        except TimeoutError as error:
            self._record(request, "timeout")
            raise ProviderTimeoutError from error
        except (MalformedProviderOutputError, TransferNotAuthorizedError):
            raise
        except Exception as error:
            if (
                "quota" in str(error).casefold()
                or "resource_exhausted" in str(error).casefold()
            ):
                self._record(request, "quota")
                raise ProviderQuotaExceededError from error
            self._record(request, "outage")
            raise ProviderOutageError from error
        validate_citations(request, result)
        self._sessions[self._key(request)] = result
        self._record(request, "success")
        return result

    def session_result(self, request: ResearchRequest) -> ResearchResult | None:
        return self._sessions.get(self._key(request))

    def _record(self, request: ResearchRequest, outcome: str) -> None:
        self._metrics.record(
            ResearchMetric(
                tenant_id=request.tenant_id,
                actor_id=request.actor_id,
                session_id=request.session_id,
                provider=self._provider.name,
                outcome=outcome,
                source_count=len(request.sources),
            )
        )
