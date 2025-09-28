"""Test reading data from infra.yaml, with injected password from .env."""

from typing import Callable, TypeVar

import git
import yaml
from dotenv import dotenv_values
from pydantic import PostgresDsn, ValidationError

T = TypeVar("T")


def find(fn: Callable[[T], bool], lst: list[T]):
    """Find the first element in lst that satisfies the predicate fn."""
    return next(filter(fn, lst), None)


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
        dsn = PostgresDsn(
            find(lambda s: s["name"] == "postgres", config["services"])["urls"][0]["address"]
        )
        dsn = PostgresDsn.build(scheme=dsn.scheme, **(dsn.hosts()[0] | {"password": password}))
        print("Postgres DSN with injected password: %s", dsn)
    except KeyError as e:
        raise KeyError("Cannot find Postgres service configuration") from e
    except ValidationError as e:
        raise ValueError(f"Invalid Postgres DSN: {e}") from e
