from pydantic import BaseModel, ConfigDict


class DefaultConfig(BaseModel):
    issuer: str
    client: str
    service: str


class IssuerData(BaseModel):
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


class ServiceData(BaseModel):
    name: str
    daily_rate: int
    description: str


class ClientData(BaseModel):
    name: str
    address: str
    city: str
    postal: str
    siren: str
    vat_number: str


class DataModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=str.upper,
        populate_by_name=True,
    )

    issuers: list[IssuerData]
    services: list[ServiceData]
    clients: list[ClientData]
