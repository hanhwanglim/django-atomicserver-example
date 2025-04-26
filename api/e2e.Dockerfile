# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.1
FROM python:${PYTHON_VERSION}-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Indicate a CI/CD environment (can be used by tools/scripts)
ENV CI=true
# Disable Django debug mode
ENV DEBUG=false

# Install curl for healthchecks
RUN apk add --no-cache curl

# Copy the uv binary from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* /app/

RUN uv sync --locked

COPY . /app

# Run Django database migrations
RUN uv run manage.py migrate

# Command to run the Django development server using atomicserver
CMD ["uv", "run", "manage.py", "atomicserver", "--addrport", "0.0.0.0:8000"]
