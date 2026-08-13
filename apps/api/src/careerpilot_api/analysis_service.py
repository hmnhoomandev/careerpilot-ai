"""Tenant-scoped application service around the compiled LangGraph workflow."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, cast

from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    Permission,
    ResourceAttributes,
)

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langgraph.graph.state import CompiledStateGraph

    from careerpilot_api.analysis_graph import AnalysisGraphState


class AnalysisRunNotFoundError(LookupError):
    """Hide absent and foreign run identifiers behind one safe result."""


class AnalysisGraphService:
    """Authorize graph start/read/cancel and retain local run snapshots."""

    def __init__(
        self, graph: CompiledStateGraph[Any, Any, Any, Any], policy: AccessPolicy
    ) -> None:
        self._graph = graph
        self._policy = policy
        self._runs: dict[tuple[str, str], AnalysisGraphState] = {}

    async def start(
        self, context: AuthorizationContext, profile_id: str, job_description: str
    ) -> AnalysisGraphState:
        self._require(context)
        run_id = str(uuid.uuid4())
        initial: AnalysisGraphState = {
            "run_id": run_id,
            "profile_id": profile_id,
            "job_description": job_description,
            "actor_id": context.actor_id,
            "tenant_id": context.tenant_id,
            "role": context.role.value,
            "purpose": context.purpose,
            "correlation_id": context.correlation_id,
            "cancelled": False,
            "status": "running",
            "events": [],
        }
        config: RunnableConfig = {
            "configurable": {"thread_id": self._thread_id(context, run_id)}
        }
        try:
            result = cast(
                "AnalysisGraphState", await self._graph.ainvoke(initial, config=config)
            )
        except Exception as error:
            result = {
                **initial,
                "status": "failed",
                "error": {
                    "code": "graph_execution_failed",
                    "message": "Analysis could not be completed.",
                },
            }
            self._runs[(context.tenant_id, run_id)] = result
            raise RuntimeError("graph_execution_failed") from error
        self._runs[(context.tenant_id, run_id)] = result
        return result

    def get(self, context: AuthorizationContext, run_id: str) -> AnalysisGraphState:
        self._require(context)
        result = self._runs.get((context.tenant_id, run_id))
        if result is None or result["actor_id"] != context.actor_id:
            raise AnalysisRunNotFoundError(run_id)
        return result

    def cancel(self, context: AuthorizationContext, run_id: str) -> AnalysisGraphState:
        current = self.get(context, run_id)
        if current.get("status") == "completed":
            return current
        updated = cast(
            "AnalysisGraphState", {**current, "cancelled": True, "status": "cancelled"}
        )
        self._runs[(context.tenant_id, run_id)] = updated
        return updated

    def _require(self, context: AuthorizationContext) -> None:
        self._policy.require(
            context,
            Permission.ANALYSIS_RUN,
            ResourceAttributes(context.tenant_id, context.actor_id),
        )

    @staticmethod
    def _thread_id(context: AuthorizationContext, run_id: str) -> str:
        return f"{context.tenant_id}:{context.actor_id}:{run_id}"
