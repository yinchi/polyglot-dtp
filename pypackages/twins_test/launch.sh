#!/usr/bin/env bash

# This script is used to launch the FastAPI application locally for testing purposes.
# Docker or K8s deployments should define their own launch mechanisms, including setting
# environment variables.

set -euo pipefail

# cd to the directory of this script
cd "$(dirname "$0")"

# fastapi dev -e <module>:<app> <source_dir>
uv run --package polyglot-dtp-twins-test fastapi dev \
    -e polyglot_dtp.twins.test:app \
    src/
