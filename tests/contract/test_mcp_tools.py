"""Official MCP SDK smoke tests for discovery, calls, and exposure allowlisting."""

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.document_processing import (
    BoundedDocumentParser,
    DeterministicHashEmbedder,
    InMemoryDocumentStorage,
    LocalDocumentScanner,
)
from careerpilot_api.mcp_server import create_mcp_server
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_api.retrieval_repository import InMemoryDocumentRepository
from careerpilot_api.tool_catalog import build_tool_registry
from careerpilot_api.tool_runtime import ToolExecutor
from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    CareerJourneyService,
    RagService,
    Role,
)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mcp_lists_allowlist_and_calls_read_only_tool() -> None:
    context = AuthorizationContext(
        actor_id="actor-mcp",
        tenant_id="tenant-mcp",
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="mcp-smoke",
    )
    audit = InMemoryAuditLog()
    profiles = InMemoryProfileRepository()
    journey = CareerJourneyService(profiles, AccessPolicy(), audit)
    rag = RagService(
        profiles,
        InMemoryDocumentRepository(),
        InMemoryDocumentStorage(),
        LocalDocumentScanner(),
        BoundedDocumentParser(),
        DeterministicHashEmbedder(),
        AccessPolicy(),
        audit,
    )
    executor = ToolExecutor(
        build_tool_registry(journey, rag, audit), AccessPolicy(), audit
    )
    with pytest.warns(
        Warning,
        match="Field 'lifespan' has an incomplete definition",
    ):
        server = create_mcp_server(executor, lambda: context)

    async with create_connected_server_and_client_session(server) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
        names = {tool.name for tool in tools}
        assert names == {
            "cost.estimate",
            "evidence.retrieve",
            "profile.lookup",
            "skill.taxonomy",
        }
        assert "approval.request" not in names
        schemas = {tool.name: tool.inputSchema for tool in tools}
        assert schemas["profile.lookup"]["required"] == ["profile_id"]
        assert set(schemas["cost.estimate"]["properties"]) == {"workflow", "units"}
        result = await session.call_tool(
            "cost.estimate", {"workflow": "retrieval", "units": 2}
        )
        assert result.isError is False
        assert result.structuredContent is not None
        assert result.structuredContent["estimated_chf"] == 0
