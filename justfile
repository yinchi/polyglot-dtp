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
## DT platform config files
#################################

# Display all infra.yaml files in the project directory
infra:
    #!/usr/bin/env bash
    yq eval-all '[.] | sort_by(.name)' $(find infra/ -name infra.yaml)

# List all infra.yaml files in the project directory
infra-find:
    #!/usr/bin/env bash
    find infra/ -name infra.yaml

#################################
## Kubernetes
#################################

# Create a new minikube profile 'dtp' if it doesn't already exist, and switch to it
k8s-create:
    #!/usr/bin/env bash
    set -euo pipefail

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
    docker compose -f compose.yaml --env-file .env build --push --no-cache

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

# Clean up unused Docker resources
docker-clean:
    #!/usr/bin/env bash
    docker image prune --filter "dangling=true"
    docker container prune
    docker volume prune --filter "label=com.docker.volume.anonymous=true"
    docker network prune
    docker builder prune

# List published Docker ports
docker-ports:
    #!/usr/bin/env bash
    set -euo pipefail

    # Start output buffer
    output=""

    # Header + underline
    header="CONTAINER_NAME CONTAINER_PORT HOST_MAPPING"
    underline="-------------- -------------- ------------"
    output+="$header"$'\n'
    output+="$underline"$'\n'

    # NOTE: justfile needs 4 braces to escape to 2 braces in the final output, but
    # only for the opening brace pair.

    # Get port mappings for each running container
    while read -r name; do
    while read -r mapping; do
        container_port=$(echo "$mapping" | cut -d' ' -f1)
        host_mapping=$(echo "$mapping" | cut -d' ' -f3)
        output+="$name $container_port $host_mapping"$'\n'
    done < <(docker port "$name")
    done < <(docker ps --format '{{{{.Names}}')

    # Output formatted table; exclude IPv6 mappings
    echo
    echo "$output" | column -t | grep -v --fixed '[::]'

alias dkb := docker-build
alias dkup := docker-up
alias dkdown := docker-down
alias dkrm := docker-rm
alias dkps := docker-ps
alias dklogs := docker-logs
alias dkp := docker-ports

# Find compose files in the project directory
compose-find:
    #!/usr/bin/env bash
    find . -type f -name '*compose*.yaml'

# Find Dockerfiles in the project directory
dockerfile-find:
    #!/usr/bin/env bash
    find . -type f -name '*Dockerfile*'


#################################
## Traefik
#################################

# Show Traefik routing tables
traefik-routes:
    #!/usr/bin/env bash
    set -euo pipefail

    SEGMENTS=(
        '. | filter(.name | contains("@internal") | not)'
        '| sort_by(.priority)'
        '| reverse'
        '| .[]'
        '|= pick(["rule", "entryPoints", "priority", "service", "middlewares"])'
    )
    MYSTRING=$(IFS=' '; echo "${SEGMENTS[*]}")

    echo

    echo "HTTP(S) Routes:"
    curl -fsSL http://localhost:8080/api/http/routers | yq -p=json "$MYSTRING"

    echo

    echo "TCP Routes:"
    curl -fsSL http://localhost:8080/api/tcp/routers | yq -p=json "$MYSTRING"

    echo

    echo "UDP Routes:"
    curl -fsSL http://localhost:8080/api/udp/routers | yq -p=json "$MYSTRING"

alias tfk := traefik-routes


#################################
## Python
#################################

# Sync dependencies for all packages in the uv workspace
uv-sync:
    #!/usr/bin/env bash
    uv sync --all-packages

alias uvs := uv-sync

# Run all tests in the pytests/ directory
pytests:
    #!/usr/bin/env bash
    uv run pytest pytests/

# Run a specific test file in the pytests/ directory, or list (ls) available tests
pytest test_name:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ "{{test_name}}" == "ls" ]]; then
        cd pytests
        ls test_*.py | sed 's/^test_//;s/\.py//'
    else
        uv run pytest -s pytests/test_{{test_name}}.py
    fi

# Format and lint with Ruff
ruff:
    #!/usr/bin/env bash
    echo "🛠️  Formatting .py files..."
    uv run ruff format --config ruff.toml pytests/ pypackages/
    echo "🛠️  Linting .py files..."
    uv run ruff check --config ruff.toml --fix pytests/ pypackages/
    echo "Done!"

# Find all pyproject.toml files
pyprojects:
    #!/usr/bin/env bash
    find . -name 'pyproject.toml' -not -path '*.venv*';


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

# Find all README files
readmes:
    #!/usr/bin/env bash
    find . -type f -iname '*README*' -not -path '*.venv*' -not -path '*cache*'
