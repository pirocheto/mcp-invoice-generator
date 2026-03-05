"""Tests for server-level MCP operations."""

from fastmcp import Client


async def test_ping(mcp_client: Client):
    """Server should respond to ping."""
    assert await mcp_client.ping() is True


async def test_list_tools(mcp_client: Client):
    """Server should expose the expected tools."""
    tools = await mcp_client.list_tools()
    tool_names = {t.name for t in tools}
    assert "get_default_values" in tool_names
    assert "generate_invoice" in tool_names
