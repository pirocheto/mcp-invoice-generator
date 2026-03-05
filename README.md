<div align="center">

# 🧾 MCP Invoice Generator

**Generate PDF invoices via a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server.**

![Python](https://img.shields.io/badge/python-3.13-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-3.0.1-blue.svg?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

</div>

This server is primarily designed for **local use via stdio**. It generates PDF invoices directly on your machine, saving them to a configurable output directory. Billing data (issuers, clients, services) is loaded from a local TOML file, making it easy to manage without any external service or database.

---

## Features

- **PDF invoice generation** — [Typst](https://typst.app/) template compiled to PDF
- **[MCP server](https://modelcontextprotocol.io/docs/getting-started/intro)** — `generate_invoice` and `get_default_values` tools accessible by an LLM
- **TOML configuration** — issuers, clients and services defined in `data/billing.toml`
- **[FastMCP](https://github.com/jlowin/fastmcp)** — modern MCP server framework
- **[Typst](https://typst.app/)** — typesetting system for PDF rendering
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — application settings management
- **[dynaconf](https://www.dynaconf.com/)** — TOML billing data loading
- **[uv](https://docs.astral.sh/uv/)** — dependency management
- **[ruff](https://docs.astral.sh/ruff/)** — linter & formatter
- **Dockerfile** — multi-stage build ready for production

---

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/) / [Podman](https://podman.io/) _(only required to build and run the container image)_

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pirocheto/mcp-invoice-generator
cd mcp-invoice-generator
```

### 2. Billing data

Copy and fill in the data file:

```bash
cp data/billing.toml.example data/billing.toml
```

This file is the **core data source** for invoice generation. It defines the people, companies, and services that can appear on your invoices. The `get_default_values` tool reads directly from this file, and `generate_invoice` uses the provided data to populate the PDF.

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

### 3. Environment variables

The application is configured via environment variables (prefixed with `APP_`) or a `.env` file at the project root.

| Variable             | Default                     | Description                                 |
| -------------------- | --------------------------- | ------------------------------------------- |
| `APP_SERVICE_NAME`   | `Invoice Generator Service` | Name of the MCP server                      |
| `APP_ENV`            | `development`               | Environment (`development` or `production`) |
| `APP_OUTPUT_DIR`     | `outputs`                   | Directory where generated PDFs are saved    |
| `APP_TEMPLATE_DIR`   | `templates`                 | Directory containing Typst invoice templates|
| `APP_DATA_FILE`      | `data/billing.toml`         | Path to the billing data TOML file          |

Relative paths are resolved from the project root. Absolute paths are used as-is.

---

## Installation

### Local (stdio)

Install the project in your MCP servers directory:

```bash
mkdir -p ~/.local/share/mcp
rsync -a --exclude='.git' . ~/.local/share/mcp/mcp-invoice-generator
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
- **Runtime stage** — minimal `python:3.13-slim` image with only the virtual environment copied over
- Runs as a **non-root user** (`nonroot`, uid 999)
- Installs system font libraries (`libpango`, `libharfbuzz`, `libfontconfig`)
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

**`get_default_values`** — Returns all default billing data from `billing.toml`, including available issuers, services, and clients.

**`generate_invoice`** — Generates a PDF invoice from flat input fields.

| Parameter             | Type    | Default | Description                         |
| --------------------- | ------- | ------- | ----------------------------------- |
| `invoice_number`      | `str`   | —       | Invoice number                      |
| `invoice_date`        | `date`  | today   | Invoice date (ISO 8601)             |
| `issuer_name`         | `str`   | —       | Issuer full name                    |
| `issuer_address`      | `str`   | —       | Issuer street address               |
| `issuer_city`         | `str`   | —       | Issuer city                         |
| `issuer_postal`       | `str`   | —       | Issuer postal code                  |
| `issuer_email`        | `str`   | —       | Issuer email address                |
| `issuer_siren`        | `str`   | —       | Issuer SIREN number                 |
| `issuer_siret`        | `str`   | —       | Issuer SIRET number                 |
| `issuer_vat_number`   | `str`   | —       | Issuer VAT number                   |
| `issuer_iban`         | `str`   | —       | Issuer IBAN                         |
| `issuer_bic`          | `str`   | —       | Issuer BIC / SWIFT code             |
| `issuer_tax_rate`     | `float` | —       | VAT rate (e.g. `0.2` for 20%)       |
| `service_daily_rate`  | `int`   | —       | Daily rate in euros (TJM)           |
| `service_description` | `str`   | —       | Service description line on invoice |
| `service_days`        | `int`   | —       | Number of days worked               |
| `client_name`         | `str`   | —       | Client company name                 |
| `client_address`      | `str`   | —       | Client street address               |
| `client_city`         | `str`   | —       | Client city                         |
| `client_postal`       | `str`   | —       | Client postal code                  |
| `client_siren`        | `str`   | —       | Client SIREN number                 |
| `client_vat_number`   | `str`   | —       | Client VAT number                   |

Returns the path to the generated PDF file.

---

## Template

The invoice template is located in `templates/invoice.typ` and is written in **[Typst](https://typst.app/)**, a modern typesetting language. It receives all invoice fields as named parameters and is compiled to PDF by the `typst` Python package.

The included template is designed for **French freelancers**: it is based on a daily rate (TJM), computes subtotal, VAT, and total, and formats all monetary values using French conventions (e.g. `3 000,00 €`).

To customise the invoice layout, edit `templates/invoice.typ` directly.

→ [View example invoice](examples/invoice.pdf)

### Template parameters

All parameters are passed as flat named arguments to the Typst template function.

**Issuer**

| Parameter           | Type    | Description                   |
| ------------------- | ------- | ----------------------------- |
| `issuer_name`       | `str`   | Full name                     |
| `issuer_address`    | `str`   | Street address                |
| `issuer_city`       | `str`   | City                          |
| `issuer_postal`     | `str`   | Postal code                   |
| `issuer_email`      | `str`   | Email address                 |
| `issuer_siren`      | `str`   | SIREN number                  |
| `issuer_siret`      | `str`   | SIRET number                  |
| `issuer_vat_number` | `str`   | VAT number                    |
| `issuer_iban`       | `str`   | IBAN                          |
| `issuer_bic`        | `str`   | BIC / SWIFT code              |
| `issuer_tax_rate`   | `float` | VAT rate (e.g. `0.2` for 20%) |

**Client**

| Parameter           | Type  | Description    |
| ------------------- | ----- | -------------- |
| `client_name`       | `str` | Company name   |
| `client_address`    | `str` | Street address |
| `client_city`       | `str` | City           |
| `client_postal`     | `str` | Postal code    |
| `client_siren`      | `str` | SIREN number   |
| `client_vat_number` | `str` | VAT number     |

**Service**

| Parameter             | Type  | Description                 |
| --------------------- | ----- | --------------------------- |
| `service_daily_rate`  | `int` | Daily rate in euros (TJM)   |
| `service_description` | `str` | Description line on invoice |
| `service_days`        | `int` | Number of days worked       |

**Invoice**

| Parameter        | Type  | Description               |
| ---------------- | ----- | ------------------------- |
| `invoice_number` | `str` | Invoice number            |
| `invoice_date`   | `str` | Invoice date (DD/MM/YYYY) |

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
