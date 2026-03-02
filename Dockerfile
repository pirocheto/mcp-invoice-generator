# --------------------
# Builder stage
# --------------------
# Install uv
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# UV_COMPILE_BYTECODE=1 compiles Python bytecode for faster startup
# UV_LINK_MODE=copy ensures dependencies are copied (isolated environment)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-dev --locked --no-install-project --no-editable


COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --locked --no-editable

# --------------------
# Runtime stage
# --------------------
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

# Install necessary system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangoft2-1.0-0 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application securely
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the virtual environment and application code from the builder stage
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    FASTMCP_STATELESS_HTTP=true \
    APP_ENV=production 

USER nonroot

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]