# Package Management

!!! note
    This page is about the management of code; for deployment using containers, see:

    - Docker: (🚧 **TODO**)
    - Self-hosted Kubernetes using Minikube: (🚧 **TODO**)
    - Google Cloud Platform: (🚧 **TODO**)

## Python

The Python package manager of choice for this repo is [`uv`](https://docs.astral.sh/uv/).  To simplify development, the entire repo is a [`uv` workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/), with members as configured in the root `pyproject.toml`.  This means that all `uv` virtual environments created via this workspace (including in Docker containers) share a single lockfile `uv.lock` for consistent package versioning.

One common configuration for initializing a new uv package under the workspace is:

```bash
uv init --app --package
```

This will create a package with a name based on the current directory name ("foo" in this example), create a module at `src/foo`, and create a script in `pyproject.toml` that calls the `main()` function in the `foo` module.  The directory structure should thus look like:

```text
.
├── pyproject.toml
├── README.md
└── src
   └── foo
      └── __init__.py
```

Edit or delete these files as necessary.

### Namespace packages

A Python package may provide part of a namespace.  For example, if a package is to provide the module `polyglot_dtp.test_api`, then its `src` folder should have the structure:

```text
src
└── polyglot_dtp
   └── test_api
      └── __init__.py
```

Note that there is no `__init__.py` at the root of the namespace directory, only in the directory belonging to the module itself.

Additionally, we **must** inform `uv` of the package's name (in `pyproject.toml`) in order to resolve the namespace structure correctly:

```toml
[tool.uv.build-backend]
module-name = "polyglot_dtp.test_api"
```

!!! note
    Failure to specify the module name above will result in `uv` looking for a module named `polyglot_dtp_test_api` in `src/`, thus causing an error.

### Maintaining the shared virtual environment

To add a dependency to a package:

```bash
uv add --package <package> <dependency>  # Add the package
uv add -h  # View all command options
```

The `just uv-sync` recipe (alias `just uvs`) can also be used to manually sync the virtual environment based on the declared dependencies.  However, it does not upgrade existing packages unless required by a new dependency.  To upgrade existing packages, use:

```bash
uv sync --all-packages -U
```

### `uv` and Docker

See [`pypackages/test_api/Dockerfile`](https://github.com/yinchi/polyglot-dtp/blob/main/pypackages/test_api/Dockerfile) for an example of how to set up `uv` in a Docker container.  Note that we do not need to copy over all packages in the workspace; however, any [workspace dependencies](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources) will need to be included.

### Ruff and PyTest

A pre-commit hook for `ruff` is included in `.pre-commit.config.yaml`.  See `ruff.toml` for configuration options.  The `just ruff` recipe can also be used to run `ruff` manually.

A pre-push hook for `pytest` is included in `.pre-commit.config.yaml`.  The `just pytest` and `just pytests` recipies can also be used to run tests manually.

### Standalone packages

Workspace members are defined under `tool.uv.workspace` in the root `pyproject.toml`; thus any package not defined as a workspace member is treated as a standalone package.  However, packages can also be [explicitly excluded](https://docs.astral.sh/uv/concepts/projects/workspaces/#getting-started) from the workspace.

## Node.js (React)

We will use React primarily to build single-page applications (SPAs) for our platform, using the [Vite](https://vite.dev/guide/) build tool.  To initialize a folder as a Vite project, use:

```bash
yarn create vite . --template=react-ts
```

Available commands will then appear in `package.json`:

```json
"scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
},
```

Use `yarn vite` to start the development server, and `yarn build` to compile the project into a static website.

Although the Vite create script installs ESLint, we will instead rely on the [Biome](https://biomejs.dev/) `biome-check` pre-commit hook for formatting and linting.  Configuration is done using the `biome.json` file in the repo root.

### Dependencies and workspaces

Dependencies in yarn can be added using `yarn add`, which also accepts Git- and symlink-based (i.e.local folder) dependencies.

## 🚧 Compiled languages (C/C++, Go, Rust)

TODO
