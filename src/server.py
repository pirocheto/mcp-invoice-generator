from dataclasses import field
from datetime import datetime
from io import BytesIO
from pathlib import Path

from babel.numbers import format_decimal
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from jinja2 import Environment, FileSystemLoader
from starlette.requests import Request
from starlette.responses import JSONResponse
from weasyprint import HTML

from src.config import get_settings
from src.data import get_data
from src.schemas import ClientData, IssuerData, ServiceData

settings = get_settings()


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
def get_issuers(data: dict = Depends(get_data)) -> list[dict]:
    """Get the list of available invoice issuers."""
    return data["issuers"]


@mcp.tool
def get_services(data: dict = Depends(get_data)) -> list[dict]:
    """Get the list of available services."""
    return data["services"]


@mcp.tool
def get_clients(data: dict = Depends(get_data)) -> list[dict]:
    """Get the list of available clients."""
    return data["clients"]


@mcp.tool
def get_templates(data: dict = Depends(get_data)) -> list[str]:
    """Get the list of available invoice templates."""
    return data["templates"]


@mcp.tool
def generate_invoice(
    days: int,
    invoice_number: str,
    client: ClientData,
    service: ServiceData,
    issuer: IssuerData,
    invoice_date: datetime = field(default_factory=datetime.now),
    template_name: str = "default",
) -> dict:
    """Generate an invoice for a client in PDF format.
    The invoice is saved to the user's Downloads folder and the path is returned.
    """

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

    pdf_bytes = _html2pdf(html)

    output_dir = Path(settings.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"invoice_{invoice_number}.pdf"
    output_path.write_bytes(pdf_bytes)

    return {
        "message": f"Invoice generated successfully and saved to {output_path}",
        "path": str(output_path),
        "format": "pdf",
        "name": f"invoice_{invoice_number}.pdf",
    }


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# Run in ASGI mode in production
if settings.env == "production":
    app = mcp.http_app()
