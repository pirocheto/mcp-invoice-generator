<div align="center">

# 🧾 MCP Invoice Generator

**Generate PDF invoices via a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server.**

![Python](https://img.shields.io/badge/python-3.14+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-3.0.1-blue.svg?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

</div>

This server is primarily designed for **local use via stdio**. It generates PDF invoices directly on your machine, saving them to a configurable output directory. Billing data (issuers, clients, services) is loaded from a local TOML file, making it easy to manage without any external service or database.

---

## Features

- **PDF invoice generation** — HTML template rendered to PDF via [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/)
- **[MCP server](https://modelcontextprotocol.io/docs/getting-started/intro)** — `generate_invoice` tool accessible by an LLM
- **TOML configuration** — issuers, clients and services defined in `data/billing.toml`
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
- [Docker](https://docs.docker.com/) / [Podman](https://podman.io/) _(only required to build and run the container image)_

---

## Setup

### 1. Billing data

Copy and fill in the data file:

```bash
cp data/billing.toml.example data/billing.toml
```

This file is the **core data source** for invoice generation. It defines the people, companies, and services that can appear on your invoices. The MCP tools (`get_issuers`, `get_clients`, `get_services`) read directly from this file, and `generate_invoice` uses it to populate the PDF.

You can define **multiple entries** in each section — simply repeat the `[[issuers]]`, `[[services]]`, or `[[clients]]` block.

```toml
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

### 2. Environment variables

The application is configured via environment variables (prefixed with `APP_`) or a `.env` file at the project root.

| Variable           | Default                     | Description                                 |
| ------------------ | --------------------------- | ------------------------------------------- |
| `APP_SERVICE_NAME` | `Invoice Generator Service` | Name of the MCP server                      |
| `APP_ENV`          | `development`               | Environment (`development` or `production`) |
| `APP_OUTPUT_DIR`   | `outputs`                   | Directory where generated PDFs are saved    |
| `APP_DATA_FILE`    | `data/billing.toml`         | Path to the billing data TOML file          |

Relative paths are resolved from the project root. Absolute paths are used as-is.

---

## Installation

### Local (stdio)

Clone the repository and install it in your MCP servers directory:

```bash
git clone https://github.com/pirocheto/mcp-invoice-generator
mkdir -p ~/.local/share/mcp
rsync -a --exclude='.git' mcp-invoice-generator/ ~/.local/share/mcp/mcp-invoice-generator
```

Point your MCP client (e.g. Claude Desktop) to the installed server:

```json
{
  "mcpServers": {
    "invoice-generator": {
      "type": "stdio",
      "env": {
        "APP_DATA_FILE": "./data/billing.toml",
        "APP_OUTPUT_DIR": "./outputs"
      },
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/<username>/.local/share/mcp-invoice-generator",
        "--",
        "fastmcp",
        "run"
      ]
    }
  }
}
```

> Replace `<username>` in the path above with your actual Linux username (e.g. `/home/johndoe/...`). You can get it by running `echo $USER` in a terminal.

### Docker

The project includes a multi-stage Dockerfile optimised for production:

- **Builder stage** — installs dependencies with `uv` using layer caching
- **Runtime stage** — minimal `python:3.14-slim` image with only the virtual environment copied over
- Runs as a **non-root user** (`nonroot`, uid 999)
- Installs the system libraries required by WeasyPrint (`libpango`, `libharfbuzz`, `libfontconfig`)
- Exposes the MCP server via `uvicorn` on port `8000`

```bash
# Build the image
make build

# Run the container (mounts data/ and outputs/, exposes port 8000)
make start
```

> `data/billing.toml` must exist before running the container — it is mounted at runtime and is never baked into the image.

---

## MCP Tools

**`get_issuers`** — Returns the list of available invoice issuers from `billing.toml`.

**`get_services`** — Returns the list of available services and their daily rates.

**`get_clients`** — Returns the list of available clients.

**`get_templates`** — Returns the list of available invoice templates.

**`generate_invoice`**

| Parameter        | Type          | Default      | Description                   |
| ---------------- | ------------- | ------------ | ----------------------------- |
| `days`           | `int`         | _(required)_ | Number of days worked         |
| `invoice_number` | `str`         | _(required)_ | Invoice number                |
| `client`         | `ClientData`  | _(required)_ | Client details                |
| `service`        | `ServiceData` | _(required)_ | Service details               |
| `issuer`         | `IssuerData`  | _(required)_ | Issuer details                |
| `invoice_date`   | `datetime`    | today        | Invoice date (ISO 8601)       |
| `template_name`  | `str`         | `default`    | Template to use for rendering |

Returns the path to the generated PDF file.

---

## Template

The invoice template is located in `templates/invoice.html` and is written in **HTML + [Jinja2](https://jinja.palletsprojects.com/)**. It receives the `issuer`, `client`, and `service` objects as context variables and is then converted to a PDF by **[WeasyPrint](https://weasyprint.org/)**.

The included template is designed for **French freelancers**: it is based on a daily rate (TJM), computes subtotal, VAT, and total, and formats all monetary values using French locale conventions (e.g. `11 000,00 €`) via [Babel](https://babel.pocoo.org/).

To customise the invoice layout, edit `templates/invoice.html` directly. Any valid HTML/CSS supported by WeasyPrint can be used.

→ [View example invoice](examples/invoice.pdf)

### Template context

**`issuer`**

| Variable            | Type    | Description                   |
| ------------------- | ------- | ----------------------------- |
| `issuer.name`       | `str`   | Full name                     |
| `issuer.address`    | `str`   | Street address                |
| `issuer.city`       | `str`   | City                          |
| `issuer.postal`     | `str`   | Postal code                   |
| `issuer.email`      | `str`   | Email address                 |
| `issuer.siren`      | `str`   | SIREN number                  |
| `issuer.siret`      | `str`   | SIRET number                  |
| `issuer.vat_number` | `str`   | VAT number                    |
| `issuer.iban`       | `str`   | IBAN                          |
| `issuer.bic`        | `str`   | BIC / SWIFT code              |
| `issuer.tax_rate`   | `float` | VAT rate (e.g. `0.2` for 20%) |

**`client`**

| Variable            | Type  | Description    |
| ------------------- | ----- | -------------- |
| `client.name`       | `str` | Company name   |
| `client.address`    | `str` | Street address |
| `client.city`       | `str` | City           |
| `client.postal`     | `str` | Postal code    |
| `client.siren`      | `str` | SIREN number   |
| `client.vat_number` | `str` | VAT number     |

**`service`**

| Variable              | Type  | Description                 |
| --------------------- | ----- | --------------------------- |
| `service.name`        | `str` | Service identifier          |
| `service.daily_rate`  | `int` | Daily rate in euros (TJM)   |
| `service.description` | `str` | Description line on invoice |

Additional variables computed at render time: `days`, `invoice_number`, `invoice_date`, `subtotal`, `tax`, `total`.

---

## Development

```bash
make dev
```

Starts the server with `--reload` via `dev.fastmcp.json`.

### Make Commands

| Command              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `make dev`           | Start server in development mode with auto-reload |
| `make test`          | Run tests with coverage report                    |
| `make build`         | Build the Docker image                            |
| `make start`         | Run the container in production                   |
| `make run-inspector` | Launch the MCP inspector                          |

---

## License

MIT — see [LICENSE](LICENSE).
