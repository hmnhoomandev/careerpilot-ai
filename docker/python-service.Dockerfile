# syntax=docker/dockerfile:1.7
ARG PYTHON_IMAGE=python:3.13.11-slim-trixie@sha256:2b9c9803c6a287cafa0a8c917211dddd23dcd2016f049690ee5219f5d3f1636e
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.29@sha256:eb2843a1e56fd9e30c7276ce1a52cba86e64c7b385f5e3279a0e08e02dd058fc

FROM ${UV_IMAGE} AS uv
FROM ${PYTHON_IMAGE} AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /workspace
COPY pyproject.toml uv.lock README.md ./
COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY packages/core/pyproject.toml packages/core/pyproject.toml
COPY services/google-adk/pyproject.toml services/google-adk/pyproject.toml
COPY services/openai-agents/pyproject.toml services/openai-agents/pyproject.toml
COPY services/temporal-worker/pyproject.toml services/temporal-worker/pyproject.toml
COPY apps/api/src apps/api/src
COPY packages/core/src packages/core/src
COPY services/google-adk/src services/google-adk/src
COPY services/openai-agents/src services/openai-agents/src
COPY services/temporal-worker/src services/temporal-worker/src
RUN uv sync --frozen --no-dev --all-packages --no-editable

FROM ${PYTHON_IMAGE} AS runtime
ARG VCS_REF=unknown
LABEL org.opencontainers.image.source="https://github.com/careerpilot-ai/careerpilot-ai" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.licenses="Apache-2.0"
ENV PATH=/opt/venv/bin:$PATH PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 CAREERPILOT_ENVIRONMENT=local
RUN apt-get update \
    && apt-get upgrade --yes \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 careerpilot \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin careerpilot \
    && mkdir -p /app/.data/documents \
    && chown -R 10001:10001 /app
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY --chown=10001:10001 alembic.ini /app/alembic.ini
COPY --chown=10001:10001 migrations /app/migrations
USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "careerpilot_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080", "--no-server-header"]
