from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from app.config import get_settings

settings = get_settings()

mcp = FastMCP(name="My MCP Server")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")
