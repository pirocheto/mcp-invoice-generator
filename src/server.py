import tempfile
from pathlib import Path

import typst
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import get_settings
from src.data import get_default_data
from src.schemas import MCPInputData

settings = get_settings()


templates_dir = Path(settings.template_dir).resolve()
tmp_dir = templates_dir / "tmp"
tmp_dir.mkdir(exist_ok=True)


mcp = FastMCP(
    name=settings.service_name,
    version="0.1.0",
    instructions="""
This service generates PDF invoices for clients based on provided data and templates.

Features:
- Generate PDF invoices with customizable templates
- Retrieve default values and client information
- Generate professional invoices in PDF format
- Save invoices to the outputs directory
- Access invoice templates and settings
""",
)


@mcp.tool
def get_default_values(data: dict = Depends(get_default_data)) -> dict:
    """Get the default values for invoices, including available issuers, services, and clients."""
    return data


@mcp.tool
def generate_invoice(data: MCPInputData) -> dict:
    """Generate an invoice for a client in PDF format.
    The invoice is saved to the outputs directory and the path is returned.
    """

    output_path = Path(settings.output_dir) / f"invoice_{data.invoice_number}.pdf"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", dir=tmp_dir, prefix="answers_", delete=True
    ) as tmp_file:
        tmp_file.write(data.model_dump_json())
        tmp_file.flush()

        # typst json data must be relative to the templates directory
        tmp_rel = Path(tmp_file.name).relative_to(templates_dir)
        typst.compile(
            f'#import "invoice.typ": invoice\n#show: invoice(..json("{tmp_rel}"))'.encode(),
            output=output_path,
            root=str(templates_dir),
        )

    return {
        "message": f"Invoice generated successfully and saved to {output_path}",
        "path": str(output_path),
        "format": "pdf",
        "name": f"invoice_{data.invoice_number}.pdf",
    }


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# Run in ASGI mode in production
if settings.env == "production":
    app = mcp.http_app()
