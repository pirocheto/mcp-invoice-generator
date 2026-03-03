"""Tests for the MCP tools."""

import json

from fastmcp import Client
from mcp.types import TextContent


async def test_get_issuers(mcp_client: Client):
    """get_issuers should return a non-empty list of issuers."""
    result = await mcp_client.call_tool("get_issuers", {})
    assert isinstance(result.content[0], TextContent)

    issuers = json.loads(result.content[0].text)
    assert isinstance(issuers, list)
    assert len(issuers) > 0
    assert "name" in issuers[0]
    assert "siren" in issuers[0]


async def test_get_services(mcp_client: Client):
    """get_services should return a non-empty list of services."""
    result = await mcp_client.call_tool("get_services", {})

    assert isinstance(result.content[0], TextContent)
    services = json.loads(result.content[0].text)

    assert isinstance(services, list)
    assert len(services) > 0
    assert "name" in services[0]
    assert "daily_rate" in services[0]


async def test_get_clients(mcp_client: Client):
    """get_clients should return a non-empty list of clients."""
    result = await mcp_client.call_tool("get_clients", {})
    assert isinstance(result.content[0], TextContent)

    clients = json.loads(result.content[0].text)
    assert isinstance(clients, list)
    assert len(clients) > 0
    assert "name" in clients[0]
    assert "address" in clients[0]


async def test_get_templates(mcp_client: Client):
    """get_templates should return at least the default template."""
    result = await mcp_client.call_tool("get_templates", {})
    assert isinstance(result.content[0], TextContent)

    templates = json.loads(result.content[0].text)
    assert isinstance(templates, list)
    assert "default" in templates


async def test_generate_invoice(mcp_client: Client, tmp_path):
    """generate_invoice should produce a PDF file."""
    import os

    os.environ["APP_OUTPUT_DIR"] = str(tmp_path)

    result = await mcp_client.call_tool(
        "generate_invoice",
        {
            "days": 3,
            "invoice_number": "TEST-001",
            "client": {
                "name": "Acme Corp",
                "address": "42 avenue des Champs-Élysées",
                "city": "Paris",
                "postal": "75008",
                "siren": "987 654 321",
                "vat_number": "FR 98 987 654 321",
            },
            "service": {
                "name": "consulting",
                "daily_rate": 600,
                "description": "Prestation de services",
            },
            "issuer": {
                "name": "Jane Doe",
                "address": "12 rue de la Paix",
                "city": "Lyon",
                "postal": "69001",
                "email": "jane@example.com",
                "siren": "123 456 789",
                "siret": "123 456 789 00012",
                "vat_number": "FR 12 123 456 789",
                "iban": "FR76 1234 5678 9012 3456 7890 123",
                "bic": "BNPAFRPPXXX",
                "tax_rate": 0.2,
            },
        },
    )
    assert isinstance(result.content[0], TextContent)
    data = json.loads(result.content[0].text)
    assert data["format"] == "pdf"
    assert data["name"] == "invoice_TEST-001.pdf"
    assert "path" in data
