# Nanobot gateway Dockerfile
# Multi-stage build with uv
# Build context is the repository root (.)

ARG REGISTRY_PREFIX_DOCKER_HUB

# ---
# Stage 1: Build the application
# ---

FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy root workspace files
COPY pyproject.toml uv.lock ./

# Copy workspace members needed for sync
COPY backend/ /app/backend/
COPY qwen-code-api/ /app/qwen-code-api/
COPY mcp/mcp-lms/ /app/mcp/mcp-lms/
COPY mcp/mcp-obs/ /app/mcp/mcp-obs/
COPY nanobot/ /app/nanobot/
COPY nanobot-websocket-channel/ /app/nanobot-websocket-channel/

# Sync dependencies from root workspace
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: Runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Use root user directly (HOST_UID=0, HOST_GID=0 on VM)
# No need to create new user

# Copy the application from builder
COPY --from=builder /app /app

# Set PATH to include venv
ENV PATH="/app/.venv/bin:$PATH"

# Create workspace directory
RUN mkdir -p /app/nanobot/workspace

WORKDIR /app/nanobot

# Run the entrypoint script
CMD ["python", "/app/nanobot/entrypoint.py"]
