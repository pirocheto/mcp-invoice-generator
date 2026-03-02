from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TypedDict

from babel.numbers import format_decimal
from dynaconf import Dynaconf
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

_settings = Dynaconf(
    root_path=str(Path(__file__).parent),
    settings_files=["configs/data.toml"],
)


class Client(TypedDict):
    """Information about a client."""

    name: str
    address: str
    city: str
    postal: str
    siren: str
    vat_number: str


class Issuer(TypedDict):
    """Information about the invoice issuer."""

    name: str
    address: str
    city: str
    postal: str
    email: str
    siren: str
    siret: str
    vat_number: str
    iban: str
    bic: str
    tax_rate: float


class Service(TypedDict):
    """Default service configuration."""

    name: str
    daily_rate: int
    description: str


defaults: dict = _settings.get("defaults", {})
issuers: dict[str, Issuer] = {
    i["name"]: Issuer(**i) for i in _settings.get("issuers", [])
}
services: dict[str, Service] = {
    s["name"]: Service(**s) for s in _settings.get("services", [])
}
clients: dict[str, Client] = {
    c["name"]: Client(**c) for c in _settings.get("clients", [])
}

DEFAULT_ISSUER_NAME = issuers[defaults.get("issuer")]["name"]
DEFAULT_CLIENT_NAME = clients[defaults.get("client")]["name"]
DEFAULT_SERVICE_NAME = services[defaults.get("service")]["name"]


CLIENTS_CHOICES = list(clients.keys())
SERVICES_CHOICES = list(services.keys())
ISSUERS_CHOICES = list(issuers.keys())


def html2pdf(html: str) -> bytes:
    """Convert HTML to PDF."""

    pdf_buffer = BytesIO()
    HTML(string=html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.read()


def _fr_number(value: float, decimals: int = 2) -> str:
    """Format a number with French conventions using Babel."""
    fmt = f"#,##0.{'0' * decimals}" if decimals else "#,##0"
    return format_decimal(value, format=fmt, locale="fr_FR")


class InvoiceService:
    """Service for generating invoices."""

    def __init__(self) -> None:
        env = Environment(loader=FileSystemLoader("templates"))
        env.filters["fr_number"] = _fr_number
        self.template = env.get_template("invoice.html")

    def generate(
        self,
        days: int,
        invoice_number: str,
        issuer_name: str = DEFAULT_ISSUER_NAME,
        client_name: str = DEFAULT_CLIENT_NAME,
        service_name: str = DEFAULT_SERVICE_NAME,
        invoice_date: datetime | None = None,
    ) -> bytes:
        """Generate an invoice for a client in PDF format."""

        issuer = issuers[issuer_name]
        client = clients[client_name]
        service = services[service_name]

        daily_rate = service["daily_rate"]
        tax_amount = issuer["tax_rate"]

        subtotal = days * daily_rate
        tax = subtotal * tax_amount
        total = subtotal + tax
        invoice_date = invoice_date or datetime.now()

        html = self.template.render(
            invoice_date=invoice_date,
            invoice_number=invoice_number,
            days=days,
            tax_amount=tax_amount * 100,
            subtotal=subtotal,
            tax=tax,
            total=total,
            client=client,
            issuer=issuer,
            service=service,
        )

        return html2pdf(html)


def get_invoice_service() -> InvoiceService:
    """Utility function to get an instance of the InvoiceService via dependency injection."""
    return InvoiceService()
