############################################################
# Justfile for Polyglot DTP
#
# Just is like Make, but targets scripts instead of builds.
# No more .PHONY targets!
# Just reference: https://just.systems/man/en/
############################################################

# Default task: show available tasks
default:
    just --list


#################################
## Kubernetes
#################################

# Create a new minikube profile 'dtp' if it doesn't already exist, and switch to it
k8s-create:
    #!/usr/bin/env bash
    echo "🛠️  Checking for minikube profile 'dtp'..."
    if ! minikube profile list -o json | jq .valid[].Name | grep '^"dtp"$' &> /dev/null; then
        echo "Creating new minikube profile 'dtp'..."
        minikube start -p dtp --cpus=4 --memory=8g --disk-size=50g
        echo "✅  minikube profile 'dtp' created."
    else
        echo "⚠️   minikube profile 'dtp' already exists."
    fi
    minikube profile dtp && kubectl config use-context dtp
    minikube profile list
    echo

# Delete the minikube profile 'dtp' if it exists, and all associated resources
k8s-delete:
    #!/usr/bin/env bash
    minikube delete -p dtp


#################################
## Docker
#################################

# Build containers
docker-build:
    #!/usr/bin/env bash
    docker compose -f compose.yaml --env-file .env build

# Start all services defined in compose.yaml
docker-up:
    #!/usr/bin/env bash
    docker compose -f compose.yaml --env-file .env up \
        -d --remove-orphans --wait --wait-timeout 60

# Remove all services defined in compose.yaml
docker-down:
    #!/usr/bin/env bash
    docker compose -p polyglot-dtp down --remove-orphans --timeout 10

# Remove all services defined in compose.yaml and all associated volumes
docker-rm:
    #!/usr/bin/env bash
    docker compose -p polyglot-dtp down --remove-orphans --timeout 10 --volumes

# Show Docker container status
docker-ps:
    #!/usr/bin/env bash
    docker compose -p polyglot-dtp ps

# Watch logs of all services defined in compose.yaml
docker-logs:
    #!/usr/bin/env bash
    docker compose -p polyglot-dtp logs -f -t --tail=100

alias dkb := docker-build
alias dkup := docker-up
alias dkdown := docker-down
alias dkrm := docker-rm
alias dkps := docker-ps
alias dklogs := docker-logs


#################################
## Python
#################################

# Sync dependencies for all packages in the uv workspace
uv-sync:
    #!/usr/bin/env bash
    uv sync --all-packages

alias uvs := uv-sync

# Python tests
pytest:
    #!/usr/bin/env bash
    uv run pytest pytests/

# Format and lint with Ruff
ruff:
    #!/usr/bin/env bash
    echo "🛠️  Formatting .py files..."
    uv run ruff format --config ruff.toml pytests/ pypackages/
    echo "🛠️  Linting .py files..."
    uv run ruff check --config ruff.toml --fix pytests/ pypackages/
    echo "Done!"


#################################
## Databases
#################################

# Command-line interface to PostgreSQL
pgcli:
    #!/usr/bin/env bash
    set -euo pipefail
    source .env
    echo "✅  Loaded environment variables from .env."

    # Set default values if variables are not set
    export PGUSER=${POSTGRES_USER:-dtp}
    export PGPASSWORD=${POSTGRES_PASSWORD:-dtpsecret1}
    export PGHOST=${POSTGRES_HOST:-localhost}
    export PGPORT=${POSTGRES_PORT:-5432}
    export PGDATABASE=${POSTGRES_DB:-dtp}

    # Connect to PostgreSQL using pgcli
    echo "🛠️  Connecting to PostgreSQL at $PGHOST:$PGPORT as user $PGUSER..."
    pgcli postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE

alias pg := pgcli


#################################
## Miscellaneous
#################################

# Generate a random password
gen-pass:
    #!/usr/bin/env bash
    openssl rand -base64 18 | tr '+/' '-_'
