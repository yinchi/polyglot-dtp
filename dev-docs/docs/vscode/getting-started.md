# Getting started

This project assumes you have a Linux environment with with `apt` package manager, e.g. Ubuntu.  For Windows users, see [these instructions for installing WSL](https://learn.microsoft.com/en-gb/windows/wsl/install).

## Setup script

Run `setup.sh` to install Linux packages for software development.  The script will (not necessarily in the order shown below):

1. Ensure `$HOME/.local/bin` is in the user's `$PATH` variable
2. Add the Neo4j APT repository, so that [`cypher-shell`](https://neo4j.com/docs/operations-manual/current/cypher-shell/), a command-line tool for the Neo4j graph database engine, can be installed.
3. Adds the Docker APT repository if necessary.
    - Also adds the user to the `docker` group, enabling the user to run Docker commands without `sudo`.
4. Updates the APT cache and refreshes existing snaps.
    - Ubuntu enables snaps by default; Debian users may need to enable them manually with `sudo apt install snapd`.
5. Installs missing packages via APT, Snap, and manual downloads if necessary.

    ??? note
        Use `apt info <package>` or `snap info <package>` to read details on each package in the install list.

6. Sets up Git:

    - Ensures `user.name` and `user.email` are set
    - Adds a few Git aliases (ensuring that they are not already defined)
    - Sets up pre-commit and pre-push hooks for formatting, linting, and PyTest (see `.pre-commit-config.yaml`)

!!! todo
    Define a minimal package list for the project and a way to pick and choose optional packages.

## The justfile

[Just](https://just.systems/man/en/) is a `make`-like program for organizing scripts.  Type `just` in a terminal to find the list of available `just` recipes.  For example, `just readmes` prints a list of all `README` files in the project.

??? note
    The actual command is:

    ```bash
    find . -type f -iname '*README*' -not -path '*.venv*' -not -path '*cache*'
    ```

    Note that in rare cases, `just` recipes can accept arguments, which is why it is recommended to always run a single recipe per line in a script to avoid ambiguity.

## .env and other secret files

1. Copy `.example.env` to `.env` and change the values marked as `changeme`.

    - A tool that can generate random passwords is `just gen-pass`.

2. Generate `infra/influx/secret/admin_token.json`, which the InfluxDB container uses to set the initial admin token.  Use `just influx-token` for this.  Copy the generated token (`apiv3_...`) into the `.env` file.

    !!! warning
        Since the admin token can be set in other ways, we do **not** copy our generated token here into `.env` automatically.  The token in `admin_token.json` is used **only** if an admin token does not already exist in the running InfluxDB instance.

3. Copy `pypackages/mock_sensor/mqtt.example.env` to `twins/mock-sensor-1/mqtt.env` and change its contents as needed.
