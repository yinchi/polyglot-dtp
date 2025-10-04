# Working with Git and PyTest

## `pre-commit`

This repo is configured with [`pre-commit`](https://pre-commit.com/) to set up pre-commit and pre-push hooks.  Hooks are defined in `.pre-commit-config.yaml` in the repo root.

??? note
    The Git hooks are installed as part of `setup.sh`.  To perform this step manually, use:

    ```bash
    pre-commit install -t pre-commit -t pre-push
    ```

Many of the precommit hooks use configuration files; these can be found at the root of the repo.  For example, Ruff (a Python linter and formatter) uses `ruff.toml`, while Markdownlint uses `.markdownlint.json`.

!!! note
    Using VS Code's sidebar UI controls for Git can be handy but can hide details such as outputs which are important when determining why `pre-commit` fails (for example, changes to files made automatically by a code formatter still need to be staged manually).

    For this reason, use of Git's command-line interface is recommended.

## Git aliases

The `setup.sh` script sets a number of useful Git aliases.  These can be inspected using:

```bash
git config -l | grep alias  # all aliases
git config -l --global | grep alias  # globally-defined aliases
git config -l --local | grep alias  # repo-specific aliases
```

In particular:

- `cd $(git root)` becomes a quick way to navigate to the root directory of the repo.
- `git st` shows the repo state.

## PyTest hook

Python-based test suites are included in the `pytests` folder.  To run a single test, use `just pytest <foo>`, which will run all the tests in `test_<foo>.py`.  To run all tests, use `just pytests`.  A pre-push hook is set up to run all tests automatically upon `git push`.

The `logging` Python module is used to generate output logs, which are stored at `pytests/logs` when running Pytest via the `just` recipes.

!!! note
    The test suites may fail, even if all the code is correct, if the associated databases are not available.  Thus PyTest can be used to check the DT platform configuration as well as the code logic for custom container images.

## Manually running hooks

Pre-commit hooks can be manually run on all files with:

```bash
pre-commit run -a [--hook-stage <stage>]
```

where `<stage>` is "pre-commit" by default.
