FROM python:3.14-bookworm

WORKDIR /app

COPY pyproject.toml .
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync

COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY payments/ ./payments/

EXPOSE 8080

ENTRYPOINT [".venv/bin/python", "-m"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "payments.app:app"]
