<div align="center">

# ⚡ FastMCP Template

**A production-ready template for building [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers with [FastMCP](https://github.com/jlowin/fastmcp).**

![Python](https://img.shields.io/badge/python-3.14+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-3.0.1-blue.svg?style=for-the-badge)

</div>

---

## Features

- **[FastMCP](https://github.com/jlowin/fastmcp)** — Framework for building MCP servers
- **[uv](https://docs.astral.sh/uv/)** — Modern Python package and dependency manager
- **[ty](https://github.com/tjdevries/ty)** — Static type checker
- **[ruff](https://docs.astral.sh/ruff/)** — Fast Python linter & formatter
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — Configuration management from environment variables
- **Testing with coverage** — pytest + pytest-asyncio with code coverage reports
- **Production-ready Dockerfile** — Multi-stage build with non-root user, bytecode compilation, and minimal base image
- **Copilot MCP integration** — Pre-configured `.vscode/mcp.json` for accessing FastMCP documentation via MCP

---

## Requirements

- [uv](https://docs.astral.sh/uv/) (package manager)

---

## Getting Started

### 1. Install dependencies

```bash
uv sync
```

### 2. Run the server (development)

```bash
make dev
```

This starts the server with `--reload` on `http://0.0.0.0:8000`.

Override port:

```bash
make dev MCP_PORT=9000
```

### 3. Run manually

```bash
python -m app.main
```

---

## Configuration

Settings are loaded from environment variables (prefix `MCP_`) or a `.env` file.

| Variable        | Default  | Description                                      |
|-----------------|----------|--------------------------------------------------|
| `MCP_PORT`      | `8000`   | Port for the HTTP server                         |

**Example `.env`:**

```env
MCP_PORT=8080
```

---

## Available Commands

| Command       | Description                                    |
|---------------|------------------------------------------------|
| `make dev`    | Start server in dev mode with auto-reload      |
| `make test`   | Run the test suite with coverage report        |
| `make build`  | Build the Docker image (`podman build`)        |
| `make start`  | Run the container in production (`podman run`) |

---



## Adding Tools

Register new tools in [app/mcp/server.py](app/mcp/server.py):

```python
@mcp.tool
def my_tool(param: str) -> str:
    """Description shown to the LLM."""
    return param.upper()
```
