# --------------------
# Builder stage
# --------------------
# Install uv
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# UV_COMPILE_BYTECODE=1 compiles Python bytecode for faster startup
# UV_LINK_MODE=copy ensures dependencies are copied (isolated environment)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_SYSTEM_PYTHON=1

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-dev --locked --no-install-project --no-editable

# Copy the project into the image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --locked --no-editable

# --------------------
# Runtime stage
# --------------------
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

# Create a non-root user to run the application
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the environment, but not the source code
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

USER nonroot

# Add the virtual environment's bin directory to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables for FastMCP
ENV MCP_PORT=8080

CMD ["python", "-m", "app.main"]