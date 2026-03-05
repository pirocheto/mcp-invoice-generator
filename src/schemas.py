from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, field_serializer


class MCPInputData(BaseModel):
    invoice_number: str
    invoice_date: Date = datetime.today().date()

    @field_serializer("invoice_date")
    def serialize_date(self, value: Date) -> str:
        return value.strftime("%d/%m/%Y")

    # Issuer fields
    issuer_name: str
    issuer_address: str
    issuer_city: str
    issuer_postal: str
    issuer_email: str
    issuer_siren: str
    issuer_siret: str
    issuer_vat_number: str
    issuer_iban: str
    issuer_bic: str
    issuer_tax_rate: float

    # Service fields
    service_daily_rate: int
    service_description: str
    service_days: int

    # Client fields
    client_name: str
    client_address: str
    client_city: str
    client_postal: str
    client_siren: str
    client_vat_number: str
