"""Polyglot DTP: Test module."""

import logging
import sys
import tomllib

import dotenv
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for connecting to the PostgreSQL database."""

    foo: str = "default_value"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="TWIN_TEST_",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Load environment variables from .env file if it exists, else
# load from system environment variables only.  Environment
# variables always override .env file variables.
env_path = dotenv.find_dotenv()
settings = Settings(**({"_env_file": env_path} if env_path else {}))

toml_path = dotenv.find_dotenv(filename="pyproject.toml", raise_error_if_not_found=True)
with open(toml_path, "rb") as fp:
    pyproject = tomllib.load(fp)

logger = logging.getLogger("twins.test")
logger.handlers = [
    logging.StreamHandler(sys.stdout),
]
logger.handlers[0].setFormatter(
    logging.Formatter(
        "%(levelname)10s   %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
logger.propagate = False

logger.setLevel(logging.INFO)

logger.info("---------------------------PYPROJECT----------------------------------")
logger.info("name: %s", pyproject["project"]["name"])
logger.info("version: %s", project_version := pyproject["project"]["version"])
logger.info("authors: %s", project_authors := pyproject["project"]["authors"])
logger.info("----------------------------------------------------------------------")

app = FastAPI(
    title="Polyglot Digital Twin Platform - Test Module",
    description=f"""\
A test digital twin module for the Polyglot Digital Twin Platform (Polyglot-DTP).  For instructions
on how to use this module as a template for your own digital twin module, please refer to
`README.md` in the source repository.

**Authors:**

{"\n".join(f"- {v['name']}: <{v['email']}>" for v in project_authors)}
""",
    version=project_version,
    license_info={
        "name": "GNU General Public License v3.0",
        "identifier": "GPL-3.0-or-later",
    },
)


@app.get(
    "/",
    response_class=PlainTextResponse,
    response_model=str,
    summary="Get the value of `foo`",
    responses={200: {"content": {"text/plain": {"example": "hello world"}}}},
)
async def read_root():
    """Get the value of `foo`, which is loaded from environment variables or the .env file.

    The order of precedence for loading the value is:
    1. `TWIN_TEST_FOO` environment variable
    2. `TWIN_TEST_FOO` variable in the .env file
    3. Default value defined in the code (`default_value`)
    """
    return PlainTextResponse(settings.foo)
