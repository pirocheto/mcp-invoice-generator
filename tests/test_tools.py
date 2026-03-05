"""Tests for the MCP tools."""

import json

from fastmcp import Client
from mcp.types import TextContent


async def test_get_default_values(mcp_client: Client):
    """get_default_values should return a dict with ISSUERS, SERVICES, and CLIENTS."""
    result = await mcp_client.call_tool("get_default_values", {})
    assert isinstance(result.content[0], TextContent)

    data = json.loads(result.content[0].text)
    assert isinstance(data, dict)
    assert "ISSUERS" in data
    assert "SERVICES" in data
    assert "CLIENTS" in data
    assert len(data["ISSUERS"]) > 0
    assert len(data["SERVICES"]) > 0
    assert len(data["CLIENTS"]) > 0


async def test_generate_invoice(mcp_client: Client, tmp_path):
    """generate_invoice should produce a PDF file."""
    import os

    os.environ["APP_OUTPUT_DIR"] = str(tmp_path)

    result = await mcp_client.call_tool(
        "generate_invoice",
        {
            "data": {
                "invoice_number": "TEST-001",
                "invoice_date": "2026-03-05",
                "issuer_name": "Jane Doe",
                "issuer_address": "12 rue de la Paix",
                "issuer_city": "Lyon",
                "issuer_postal": "69001",
                "issuer_email": "jane@example.com",
                "issuer_siren": "123 456 789",
                "issuer_siret": "123 456 789 00012",
                "issuer_vat_number": "FR 12 123 456 789",
                "issuer_iban": "FR76 1234 5678 9012 3456 7890 123",
                "issuer_bic": "BNPAFRPPXXX",
                "issuer_tax_rate": 0.2,
                "service_daily_rate": 600,
                "service_description": "Prestation de services",
                "service_days": 3,
                "client_name": "Acme Corp",
                "client_address": "42 avenue des Champs-Élysées",
                "client_city": "Paris",
                "client_postal": "75008",
                "client_siren": "987 654 321",
                "client_vat_number": "FR 98 987 654 321",
            }
        },
    )
    assert isinstance(result.content[0], TextContent)
    data = json.loads(result.content[0].text)
    assert data["format"] == "pdf"
    assert data["name"] == "invoice_TEST-001.pdf"
    assert "path" in data
