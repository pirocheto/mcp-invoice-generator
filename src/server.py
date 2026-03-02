from datetime import datetime

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.types import File
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import get_settings
from src.service import (
    DEFAULT_CLIENT_NAME,
    DEFAULT_ISSUER_NAME,
    DEFAULT_SERVICE_NAME,
    InvoiceService,
    get_invoice_service,
)

settings = get_settings()

mcp = FastMCP(name=settings.service_name)


@mcp.tool
def generate_invoice(
    days: int,
    invoice_number: str,
    invoice_date: datetime | None = None,
    client: str = DEFAULT_CLIENT_NAME,
    service: str = DEFAULT_SERVICE_NAME,
    issuer: str = DEFAULT_ISSUER_NAME,
    invoice_service: InvoiceService = Depends(get_invoice_service),
) -> File:
    """Generate an invoice for a client in PDF format."""

    pdf_bytes = invoice_service.generate(
        days=days,
        invoice_number=invoice_number,
        client_name=client,
        service_name=service,
        issuer_name=issuer,
        invoice_date=invoice_date,
    )
    return File(data=pdf_bytes, format="pdf", name=f"invoice_{invoice_number}")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# Run in ASGI mode in production
if settings.env == "production":
    app = mcp.http_app()
