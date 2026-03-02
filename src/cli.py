"""CLI to generate a PDF invoice."""

from datetime import datetime
from pathlib import Path

import click

from src.service import (
    CLIENTS_CHOICES,
    DEFAULT_CLIENT_NAME,
    DEFAULT_ISSUER_NAME,
    DEFAULT_SERVICE_NAME,
    ISSUERS_CHOICES,
    SERVICES_CHOICES,
    get_invoice_service,
)


def _validate_invoice_number(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    if not value or not value.strip():
        raise click.BadParameter("must contain at least 1 character")
    return value.strip()


@click.command()
@click.option(
    "--invoice-number",
    required=True,
    callback=_validate_invoice_number,
    help="Invoice number (e.g. INV-2026-001)",
)
@click.option(
    "--days", required=True, type=click.IntRange(min=1), help="Number of days worked"
)
@click.option(
    "--client",
    default=DEFAULT_CLIENT_NAME,
    show_default=True,
    type=click.Choice(CLIENTS_CHOICES),
    help="Client name",
)
@click.option(
    "--service",
    default=DEFAULT_SERVICE_NAME,
    show_default=True,
    type=click.Choice(SERVICES_CHOICES),
    help="Service name",
)
@click.option(
    "--issuer",
    default=DEFAULT_ISSUER_NAME,
    show_default=True,
    type=click.Choice(ISSUERS_CHOICES),
    help="Issuer name",
)
@click.option(
    "--date",
    default=None,
    help="Invoice date in ISO 8601 format (default: today, e.g. 2026-03-01)",
)
@click.option(
    "-o",
    "--output",
    default=None,
    type=click.Path(),
    help="Output PDF file path (default: invoice_<number>.pdf)",
)
def main(
    invoice_number: str,
    days: int,
    client: str,
    service: str,
    issuer: str,
    date: str | None,
    output: str | None,
) -> None:
    """Generate a PDF invoice."""
    invoice_date = datetime.fromisoformat(date) if date else datetime.now()
    output_path = Path(output) if output else Path(f"invoice_{invoice_number}.pdf")

    click.echo(f"Generating invoice {invoice_number}...")

    invoice_service = get_invoice_service()
    result = invoice_service.generate(
        days=days,
        invoice_number=invoice_number,
        client_name=client,
        service_name=service,
        issuer_name=issuer,
        invoice_date=invoice_date,
    )

    output_path.write_bytes(result)
    click.secho(f"✓ Invoice generated: {output_path.resolve()}", fg="green")


if __name__ == "__main__":
    main()
