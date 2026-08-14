"""Session, guardrail, provider, and redacted trace boundary."""

from careerpilot_openai_agents.errors import (
    ExternalTransferDeniedError,
    InterviewUnavailableError,
)
from careerpilot_openai_agents.guardrails import guard_input, guard_output
from careerpilot_openai_agents.models import InterviewRequest, InterviewResult
from careerpilot_openai_agents.provider import InterviewProvider
from careerpilot_openai_agents.telemetry import TraceEvent, TraceSink


class InterviewService:
    def __init__(
        self,
        provider: InterviewProvider,
        *,
        enabled: bool = True,
        live_provider: bool = False,
        traces: TraceSink | None = None,
    ) -> None:
        self._provider = provider
        self._enabled = enabled
        self._live_provider = live_provider
        self._traces = traces or TraceSink()
        self._sessions: dict[str, InterviewResult] = {}

    @staticmethod
    def _key(request: InterviewRequest) -> str:
        return f"{request.tenant_id}:{request.actor_id}:{request.session_id}"

    async def run(self, request: InterviewRequest) -> InterviewResult:
        if not self._enabled:
            raise InterviewUnavailableError
        if self._live_provider and not (
            request.consent_recorded and request.external_transfer_authorized
        ):
            raise ExternalTransferDeniedError
        guard_input(request.candidate_answer)
        result = await self._provider.run(request)
        guard_output(result.feedback)
        self._sessions[self._key(request)] = result
        self._traces.record(
            TraceEvent(
                request.tenant_id,
                request.actor_id,
                request.session_id,
                self._provider.name,
                request.mode,
                "success",
            )
        )
        return result

    def session_result(self, request: InterviewRequest) -> InterviewResult | None:
        return self._sessions.get(self._key(request))
