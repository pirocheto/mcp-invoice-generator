"""Shared fixtures for the test suite."""

import pytest
from fastmcp import Client

from app.mcp.config import Settings
from app.mcp.server import mcp


@pytest.fixture
async def mcp_client():
    """Open an in-memory Client connected to the server for the duration of a test."""
    async with Client(mcp) as client:
        yield client