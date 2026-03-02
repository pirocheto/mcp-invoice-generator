<div align="center">

# 🧾 MCP Invoice Generator

**Generate PDF invoices via a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server.**

![Python](https://img.shields.io/badge/python-3.14+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-3.0.1-blue.svg?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

</div>

---

## Features

- **PDF invoice generation** — HTML template rendered to PDF via [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/)
- **[MCP server](https://modelcontextprotocol.io/docs/getting-started/intro)** — `generate_invoice` tool accessible by an LLM
- **TOML configuration** — issuers, clients and services defined in `data.toml`
- **[FastMCP](https://github.com/jlowin/fastmcp)** — modern MCP server framework
- **[WeasyPrint](https://weasyprint.org/)** — HTML/CSS to PDF rendering
- **[uv](https://docs.astral.sh/uv/)** — dependency management
- **[dynaconf](https://www.dynaconf.com/)** — TOML configuration loading
- **[ruff](https://docs.astral.sh/ruff/)** — linter & formatter
- **Dockerfile** — multi-stage build ready for production

---

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [WeasyPrint system dependencies](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
- [Docker](https://docs.docker.com/) / [Podman](https://podman.io/) *(only required to build and run the container image)*

---

## Installation

```bash
uv sync
```

---

## Configuration

Copy and fill in the data file:

```bash
cp src/configs/data.toml.example src/configs/data.toml
```

The `src/configs/data.toml` contains:

```toml
[defaults]
issuer = "Jane Doe"
client = "Acme Corp"
service = "consulting"

[[issuers]]
name = "Jane Doe"
address = "12 rue de la Paix"
city = "Lyon"
postal = "69001"
email = "jane.doe@example.com"
siren = "123 456 789"
siret = "123 456 789 00012"
vat_number = "FR 12 123 456 789"
iban = "FR76 ..."
bic = "BNPAFRPPXXX"
tax_rate = 0.2

[[services]]
name = "consulting"
daily_rate = 600
description = "Professional services — consulting"

[[clients]]
name = "Acme Corp"
address = "42 avenue des Champs-Élysées"
city = "Paris"
postal = "75008"
siren = "987 654 321"
vat_number = "FR 98 987 654 321"
```

The `[defaults]` section defines the default values used by the MCP server.

---

## Template

The invoice template is located in `templates/invoice.html` and is written in **HTML + [Jinja2](https://jinja.palletsprojects.com/)**. It receives the `issuer`, `client`, and `service` objects as context variables and is then converted to a PDF by **[WeasyPrint](https://weasyprint.org/)**.

The included template is designed for **French freelancers**: it is based on a daily rate (TJM), computes subtotal, VAT, and total, and formats all monetary values using French locale conventions (e.g. `11 000,00 €`) via [Babel](https://babel.pocoo.org/).

To customise the invoice layout, edit `templates/invoice.html` directly. Any valid HTML/CSS supported by WeasyPrint can be used.

→ [View example invoice](examples/invoice.pdf)

### Template context

**`issuer`**

| Variable          | Type    | Description                        |
|-------------------|---------|------------------------------------|
| `issuer.name`     | `str`   | Full name                          |
| `issuer.address`  | `str`   | Street address                     |
| `issuer.city`     | `str`   | City                               |
| `issuer.postal`   | `str`   | Postal code                        |
| `issuer.email`    | `str`   | Email address                      |
| `issuer.siren`    | `str`   | SIREN number                       |
| `issuer.siret`    | `str`   | SIRET number                       |
| `issuer.vat_number` | `str` | VAT number                         |
| `issuer.iban`     | `str`   | IBAN                               |
| `issuer.bic`      | `str`   | BIC / SWIFT code                   |
| `issuer.tax_rate` | `float` | VAT rate (e.g. `0.2` for 20%)      |

**`client`**

| Variable           | Type  | Description    |
|--------------------|-------|----------------|
| `client.name`      | `str` | Company name   |
| `client.address`   | `str` | Street address |
| `client.city`      | `str` | City           |
| `client.postal`    | `str` | Postal code    |
| `client.siren`     | `str` | SIREN number   |
| `client.vat_number`| `str` | VAT number     |

**`service`**

| Variable              | Type  | Description                  |
|-----------------------|-------|------------------------------|
| `service.name`        | `str` | Service identifier           |
| `service.daily_rate`  | `int` | Daily rate in euros (TJM)    |
| `service.description` | `str` | Description line on invoice  |

Additional variables computed at render time: `days`, `invoice_number`, `invoice_date`, `subtotal`, `tax`, `total`.



---

## MCP Server

### Development

```bash
make dev
```

Starts the server with `--reload` via `dev.fastmcp.json`.

### Available MCP tool

**`generate_invoice`**

| Parameter        | Type    | Default                | Description                   |
|------------------|---------|------------------------|-------------------------------|
| `days`           | `int`   | *(required)*           | Number of days worked         |
| `invoice_number` | `str`   | *(required)*           | Invoice number                |
| `client`         | `str`   | `defaults.client`      | Client name                   |
| `service`        | `str`   | `defaults.service`     | Service name                  |
| `issuer`         | `str`   | `defaults.issuer`      | Issuer name                   |
| `invoice_date`   | `str`   | today                  | ISO 8601 date (optional)      |

Returns the PDF as a file attachment.

---

## Docker

The project includes a multi-stage Dockerfile optimised for production:

- **Builder stage** — installs dependencies with `uv` using layer caching
- **Runtime stage** — minimal `python:3.14-slim` image with only the virtual environment copied over
- Runs as a **non-root user** (`nonroot`, uid 999)
- Installs the system libraries required by WeasyPrint (`libpango`, `libharfbuzz`, `libfontconfig`)
- Exposes the MCP server via `uvicorn` on port `8000`

### Build & run

```bash
# Build the image
make build

# Run the container (mounts data.toml and exposes port 8000)
make start
```

> `src/configs/data.toml` must exist before running the container — it is mounted at runtime and is never baked into the image.

---

## Make Commands

| Command               | Description                                       |
|-----------------------|---------------------------------------------------|
| `make dev`            | Start server in development mode with auto-reload |
| `make test`           | Run tests with coverage report                    |
| `make build`          | Build the Docker image (`podman build`)           |
| `make start`          | Run the container in production (`podman run`)    |
| `make run-inspector`  | Launch the MCP inspector                          |

---

## TODO

- [ ] **Authentication** — add an auth layer to the MCP server (API key, OAuth, or bearer token) before exposing it publicly
- [ ] **Tests** — improve test coverage (invoice generation, template rendering, config loading)
- [ ] **Claude configuration** — add documentation on how to configure Claude Desktop (or other MCP clients) to connect to the server

---

## License

MIT — see [LICENSE](LICENSE).
