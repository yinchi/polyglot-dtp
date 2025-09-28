"""Test reading data from infra.yaml, with injected password from .env."""

import logging

import git
import yaml
from dotenv import dotenv_values
from pydantic import PostgresDsn, ValidationError


def test_read_infra_yaml():
    """Test reading data from infra.yaml, with injected password from .env."""
    repo = git.Repo(".", search_parent_directories=True)
    assert not repo.bare and repo.working_tree_dir, "Repository is bare"
    repo_dir = repo.working_tree_dir

    with open(f"{repo_dir}/infra/postgres/infra.yaml", "rb") as f:
        config = yaml.safe_load(f)

    password = dotenv_values().get("POSTGRES_PASSWORD", None)
    assert password is not None, "POSTGRES_PASSWORD not found in .env file"

    try:
        dsn = PostgresDsn(config["urls"]["postgres"]["url"])
        dsn = PostgresDsn.build(scheme=dsn.scheme, **(dsn.hosts()[0] | {"password": password}))
        logging.info("Postgres DSN with injected password: %s", dsn)
    except KeyError as e:
        raise KeyError("Missing key: config['urls']['postgres']['url']") from e
    except ValidationError as e:
        raise ValueError(f"Invalid Postgres DSN: {e}") from e
