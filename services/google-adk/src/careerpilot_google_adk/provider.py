"""Fake-first provider port plus explicitly selected Google ADK execution."""

import json
from typing import Protocol

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from careerpilot_google_adk.agent import build_app
from careerpilot_google_adk.errors import MalformedProviderOutputError
from careerpilot_google_adk.models import Finding, ResearchRequest, ResearchResult


class ResearchProvider(Protocol):
    name: str

    async def research(self, request: ResearchRequest) -> ResearchResult: ...


class FakeResearchProvider:
    """Create cited output without model, credentials, network, or cost."""

    name = "fake-adk-research-v1"

    async def research(self, request: ResearchRequest) -> ResearchResult:
        findings = tuple(
            Finding(
                statement=source.content.split(".", maxsplit=1)[0].strip() + ".",
                source_ids=(source.source_id,),
            )
            for source in request.sources
        )
        return ResearchResult(
            summary=(
                f"Reviewed {len(request.sources)} approved source(s) for: "
                f"{request.question}"
            ),
            findings=findings,
            questions_to_verify=(
                "Verify time-sensitive details before relying on them.",
            ),
        )


class AdkGeminiResearchProvider:
    """Run Gemini through ADK; construction and imports make no provider call."""

    name = "google-adk-gemini"

    def __init__(self, *, model: str) -> None:
        self._model = model
        # ADK 2.5 omits a typed constructor despite shipping typed async methods.
        self._sessions = InMemorySessionService()  # type: ignore[no-untyped-call]

    async def research(self, request: ResearchRequest) -> ResearchResult:
        app = build_app(sources=request.sources, model=self._model)
        user_id = f"{request.tenant_id}:{request.actor_id}"
        await self._sessions.create_session(
            app_name=app.name,
            user_id=user_id,
            session_id=request.session_id,
        )
        runner = Runner(app=app, session_service=self._sessions)
        message = types.Content(
            role="user", parts=[types.Part.from_text(text=request.question)]
        )
        final_text: str | None = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=request.session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = "".join(part.text or "" for part in event.content.parts)
        if not final_text:
            raise MalformedProviderOutputError("missing_final_response")
        try:
            return ResearchResult.model_validate(json.loads(final_text))
        except (json.JSONDecodeError, ValueError) as error:
            raise MalformedProviderOutputError("invalid_structured_output") from error
