# Modular Digital Twin Platform

## Setup

All instructions for this repo assume a Ubuntu or Debian-based environment with `bash` and `apt` installed.  Seriously, don't try to use another OS.  Avoid the compatibility nightmare.

0. If you are using Windows, obtain an Ubuntu environment using [WSL](https://code.visualstudio.com/docs/remote/wsl).  Open a WSL terminal and proceed as if you are using Ubuntu natively.

1. Run
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
   This will check your development environment and install missing software packages as needed.

2. Run
    ```bash
    cp .example.env .env
    ```
   and edit `.env` as desired.  You can use `just gen-pass` to generate random passwords/keys.

3. Run
    ```bash
    just docker-up
    ```
   To launch the Docker Compose stack.

>[!NOTE]
> Kubernetes-based deployment is forthcoming.

## Visual Studio Code settings

`.vscode/extensions.json` contains a list of recommendend VS Code extensions. To view these, open your command palette (default `Ctrl+Shift+P`) and enter: "Extensions: Show Recommended Extensions".  To add an extension to the recommendations, right click it in the Extensions panel and select "Add to Workspace Recommendations".

`.vscode/settings.json` contains a list of VS Code settings for the workspace.  Edit directly or using the GUI (default `Ctrl+,`).

## The `justfile`

Scripts can be run by defining them in the `justfile`.  A list of available scripts can be displayed using just `just`, which defaults to `just --list`.  For more information on `just`, see the [official manual](https://just.systems/man/en/).

For example, to launch the Docker Compose stack, use `just docker-up` or its alias `just dkup`.

## Python

`uv` has been selected as the Python package manager for this repo; see the root `pyproject.toml`.  The repo is set up as a [`uv` workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/):

- Use `just uv-sync` to sync the virtual environment, including all packages in the workspace.
- Use `just ruff` to format and lint the Python code.  Only `pytests/` and `pypackages/` will be checked.

## Docker images

The project is set up to push images to Docker Hub.  Use `docker login` to login to Docker Hub
if necessary.  The images for this project can be found at <https://hub.docker.com/u/yinchi>.
