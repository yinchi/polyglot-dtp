# Dockerfile for a mock sensor service.  Loads the `mock_sensor` (this) package and runs
# `run.py`.
#
# Two-stage build to create a final image without uv.
# Source: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=pypackages/mock_sensor/pyproject.toml,target=/app/pypackages/mock_sensor/pyproject.toml \
    uv sync --frozen --package mock_sensor --no-install-project --no-dev
COPY ./pyproject.toml ./README.md ./uv.lock /app/

# Install the actual application
COPY ./pypackages/mock_sensor/ /app/pypackages/mock_sensor/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package mock_sensor --no-dev

# Then, use a final image without uv
FROM python:3.13-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

RUN apt-get update && apt-get install -y \
    curl

# Setup a non-root user
RUN groupadd --system --gid 999 fastapi \
 && useradd --system --gid 999 --uid 999 --create-home mocksensor

# Copy the application from the builder
COPY --from=builder --chown=mocksensor:mocksensor /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

USER mocksensor
WORKDIR /app/pypackages/mock_sensor/

# Run the sensor application by default
ENTRYPOINT [ "python", "run.py" ]
CMD [ "--config", "/app/sensor.yaml" ]
