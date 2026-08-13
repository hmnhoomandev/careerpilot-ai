"""Run the read-only MCP allowlist over stdio with synthetic local identity."""

from __future__ import annotations

from careerpilot_api.main import create_app
from careerpilot_api.mcp_server import create_mcp_server


def main() -> None:
    """Compose an isolated local MCP server without cloud or model access."""
    app = create_app(environment="local")
    identity = app.state.identity_access
    session = identity.login("ada", "local-mcp-startup")
    context = identity.context_for(
        session.token,
        "tenant-ada",
        "local-mcp-request",
        purpose="personal_career_support",
    )
    server = create_mcp_server(app.state.tool_executor, lambda: context)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
