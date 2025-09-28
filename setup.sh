#!/usr/bin/env bash
# This script sets up the environment for the project.

set -euo pipefail

echo
echo "Modular Digital Twin Platform - Development Environment Setup"
echo "============================================================="
echo

# Check $PATH for $HOME/.local/bin
# lazydocker and uv are installed here
if ! echo $PATH | tr ':' '\n' | grep -qx "$HOME/.local/bin"; then
    echo "⚠️   Warning: $HOME/.local/bin is not in your PATH.  Appending it to ~/.profile."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
    echo "Please start a new terminal session to apply the changes."
    exit 1
else
    echo "✅  $HOME/.local/bin is in your PATH."
    echo
fi

# Add Neo4j repository (for cypher-shell)
echo "🛠️  Adding Neo4j APT repository for cypher-shell..."
sudo mkdir -p /etc/apt/keyrings
if ! apt-cache search cypher-shell | awk '{print $1}' | grep '^cypher-shell' -q; then
    curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/neo4j.gpg > /dev/null
    echo 'deb [signed-by=/etc/apt/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
    sudo chmod 644 /etc/apt/keyrings/neo4j.gpg
    echo "✅  Added Neo4j repository."
else
    echo "✅  Found cypher-shell in the APT cache, skipping repository addition."
fi
echo

# Update package lists
echo "🛠️  Updating package lists..."
sudo apt-get update -qq
echo

# Install required packages via apt (Canonical packages only)
echo "🛠️  Installing required packages (apt)..."
sudo apt-get install -yqo APT::Get::HideAutoRemove=1 \
    git \
    curl wget \
    just \
    pre-commit \
    python3 python3-click \
    kubecolor \
    jq \
    pgcli cypher-shell
echo

# Check global Git configuration for user.name and user.email
echo "🛠️  Checking Git configuration..."
if ! git config --get user.name &> /dev/null; then
    read -p "Enter your Git user.name: " git_username
    git config user.name "$git_username"
    echo "✅  Git user.name set to '$git_username'."
else
    echo "✅  Git user.name is already set to '$(git config --get user.name)'."
fi
if ! git config --get user.email &> /dev/null; then
    read -p "Enter your Git user.email: " git_useremail
    git config user.email "$git_useremail"
    echo "✅  Git user.email set to '$git_useremail'."
else
    echo "✅  Git user.email is already set to '$(git config --get user.email)'."
fi
echo

# Add Git aliases for convenience
echo "🛠️  Adding Git aliases..."
if ! git config --get alias.root &> /dev/null; then
    git config alias.root 'rev-parse --show-toplevel'
fi
if ! git config --get alias.st &> /dev/null; then
    git config alias.st 'status --short --branch'
fi
if ! git config --get alias.cfg &> /dev/null; then
    git config alias.cfg 'config --list'
fi
echo "✅  Git aliases added."
echo

# Install pre-commit hooks
echo "🛠️  Installing pre-commit hooks..."
pre-commit install -t pre-commit -t pre-push
echo "✅  Pre-commit hooks installed."
echo

# Install required snap packages
echo "🛠️  Installing required packages (snap)..."
sudo snap refresh
sudo snap install yq
sudo snap install --classic kubectl
sudo snap install --classic helm
echo

# Check if Docker is installed, if not, install it (adding the official Docker GPG key and
# repository).  Also checks for Docker Buildx and Docker Compose plugins.
echo "🛠️  Checking for Docker..."
if ! ( \
        docker --version &> /dev/null \
        && docker buildx version &> /dev/null \
        && docker compose version &> /dev/null ); then
    echo "Docker not found, or missing plugins. Installing Docker..."
    source ./scripts/install_docker.sh
    # Add current user to the docker group to run docker without sudo
    sudo usermod -aG docker $USER
    echo "Docker installed. Please log out and log back in to apply group changes, then run this "
    echo "script again."
    exit 1  # Exit to allow user to re-login for Docker group changes
else
    echo "✅  Docker is already installed."
    docker --version
    docker buildx version
    docker compose version
    echo
fi

# Check for lazydocker (a terminal UI for Docker)
echo "🛠️  Installing or upgrading lazydocker..."
curl -fsSL https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
echo "✅  lazydocker installed."
lazydocker --version
echo

# Check if minikube is installed, if not, install it
echo "🛠️  Checking for minikube..."
if ! minikube version &> /dev/null; then
    echo "minikube not found. Installing minikube..."
    curl -fsSL https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb \
        -o minikube_latest_amd64.deb
    sudo dpkg -i minikube_latest_amd64.deb
    rm minikube_latest_amd64.deb
    echo "✅  minikube installed."
else
    echo "✅  minikube is already installed."
fi
minikube version
echo

# Check for k9s (a terminal UI for Kubernetes)
echo "🛠️  Installing or upgrading k9s..."
curl -fsSLO https://github.com/derailed/k9s/releases/latest/download/k9s_linux_amd64.deb
sudo dpkg -i k9s_linux_amd64.deb
rm k9s_linux_amd64.deb
echo "✅  k9s installed."
k9s version --short
echo

# Check for uv (Python package management tool)
echo "🛠️  Checking for uv (Python package management)..."
if ! uv self version &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -fsSL https://astral.sh/uv/install.sh | bash
    echo "✅  uv installed."
else
    echo "✅  uv is already installed."
fi
uv self version
echo
