from dataclasses import field
from datetime import datetime
from io import BytesIO
from pathlib import Path

from babel.numbers import format_decimal
from dynaconf import Dynaconf
from fastmcp import FastMCP
from fastmcp.utilities.types import File
from jinja2 import Environment, FileSystemLoader
from starlette.requests import Request
from starlette.responses import JSONResponse
from weasyprint import HTML

from src.config import get_settings
from src.schemas import ClientData, DataModel, IssuerData, ServiceData

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# TODO: allow providing the config file path via an environment variable
# (e.g. APP_CONFIG_FILE=/path/to/data.toml) instead of hardcoding it

_raw_data = Dynaconf(
    root_path=str(Path(__file__).parent),
    settings_files=["configs/data.toml"],
)


data = DataModel.model_validate(_raw_data.as_dict())

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _html2pdf(html: str) -> bytes:
    pdf_buffer = BytesIO()
    HTML(string=html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.read()


def _fr_number(value: float, decimals: int = 2) -> str:
    fmt = f"#,##0.{'0' * decimals}" if decimals else "#,##0"
    return format_decimal(value, format=fmt, locale="fr_FR")


_jinja_env = Environment(loader=FileSystemLoader("templates"))
_jinja_env.filters["fr_number"] = _fr_number

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

settings = get_settings()
mcp = FastMCP(
    name=settings.service_name,
    version="0.1.0",
    instructions="""
This service generates PDF invoices for clients based on provided data and templates.

Features:
- Generate PDF invoices with customizable templates
- Access client information
- View available services and billing rates
- Retrieve issuer details
- Retrieve default invoice settings
""",
)


@mcp.tool
def get_issuers() -> list[dict]:
    """Get the list of available invoice issuers."""
    return [issuer.model_dump() for issuer in data.issuers]


@mcp.tool
def get_services() -> list[dict]:
    """Get the list of available services."""
    return [service.model_dump() for service in data.services]


@mcp.tool
def get_clients() -> list[dict]:
    """Get the list of available clients."""
    return [client.model_dump() for client in data.clients]


@mcp.tool
def get_templates() -> list[str]:
    """Get the list of available invoice templates."""
    return [f.stem for f in Path("templates").glob("*.html")]


@mcp.tool
def generate_invoice(
    days: int,
    invoice_number: str,
    client: ClientData,
    service: ServiceData,
    issuer: IssuerData,
    invoice_date: datetime = field(default_factory=datetime.now),
    template_name: str = "default",
) -> File:
    """Generate an invoice for a client in PDF format."""

    subtotal = days * service.daily_rate
    tax = subtotal * issuer.tax_rate
    total = subtotal + tax

    html = _jinja_env.get_template(f"{template_name}.html").render(
        invoice_date=invoice_date,
        invoice_number=invoice_number,
        days=days,
        tax_amount=issuer.tax_rate * 100,
        subtotal=subtotal,
        tax=tax,
        total=total,
        client=client,
        issuer=issuer,
        service=service,
    )

    pdf_bytes: bytes = _html2pdf(html)
    return File(data=pdf_bytes, format="pdf", name=f"invoice_{invoice_number}")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# Run in ASGI mode in production
if settings.env == "production":
    app = mcp.http_app()
