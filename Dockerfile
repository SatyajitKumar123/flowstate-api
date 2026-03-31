FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy

RUN uv pip install --system .

FROM python:3.13-alpine AS runtime

RUN apk add --no-cache libpq

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:$PATH"

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN adduser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]