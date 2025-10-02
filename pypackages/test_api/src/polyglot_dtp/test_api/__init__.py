"""Polyglot DTP: Test module."""

import logging
import sys
import tomllib
from base64 import b64decode
from typing import Awaitable, Callable

import dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

# Endpoints that should not produce access log entries
ROOT_PATH = "/twins/test"  # Match the `--root_path` in the launch command
SILENT_ENDPOINTS = ("/health",)
SILENT_ENDPOINTS = {f"{ROOT_PATH}{ep}" for ep in SILENT_ENDPOINTS}


class LogFilter(logging.Filter):
    """Filter out log messages from silent endpoints.

    See: https://dev.to/mukulsharma/taming-fastapi-access-logs-3idi
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Returns False if the record should not be logged, True otherwise."""
        if hasattr(record, "args") and len(record.args) > 2:
            path = record.args[2]
            return path not in SILENT_ENDPOINTS
        return True


logging.getLogger("uvicorn.access").addFilter(LogFilter())


class Settings(BaseSettings):
    """Settings for connecting to the PostgreSQL database."""

    foo: str = "default_value"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="TEST_API_",
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


@app.middleware("http")
async def authorize_user(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Authorize user using HTTP BasicAuth.

    Note if the BasicAuth configuration in Traefik is changed, this middleware will
    also need to be updated accordingly.  For example, we will want to upgrade to ForwardAuth
    in the future.
    """
    logger.debug("[middleware] requested URL: %s", request.url)
    if request.url.path.endswith("/health"):
        return await call_next(request)  # Skip auth for health check

    auth_header = request.headers.get("Authorization")
    logger.debug("[middleware] auth header: %s", auth_header)
    if auth_header:
        # Header format: Basic <base64("user:password")>
        try:
            tokens = auth_header.split(" ")
            assert len(tokens) == 2, "Invalid Authorization header format"
            assert tokens[0] == "Basic", "Unsupported Authorization scheme, expected 'Basic'."
            if tokens[1]:
                credentials = b64decode(tokens[1]).decode("utf-8")
                cred_tokens = credentials.split(":")
                assert len(cred_tokens) == 2, "Invalid Basic Auth credentials format."
                username, password = cred_tokens
            else:
                return PlainTextResponse(
                    "Unauthorized: Missing credentials.", status_code=status.HTTP_401_UNAUTHORIZED
                )
            assert username and password, "Username and password cannot be empty."
        except AssertionError as e:
            logger.warning("Authorization failed for user %s: %s", username, e)
            return PlainTextResponse(f"Unauthorized: {e}", status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.warning("Authorization failed for user %s: %s", username, e)
            # As we did not set the error string ourselves, don't show it to the client
            return PlainTextResponse("Bad Request", status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return PlainTextResponse(
            "Unauthorized: Missing Authorization header.", status_code=status.HTTP_401_UNAUTHORIZED
        )

    # For demonstration purposes, we don't actually verify the username and password, but
    # simply check they are not empty.
    logger.debug("[middleware] User: %s, URL: %s", username, request.url)

    # TODO: Implement proper user authentication and authorization here.
    # if not check_auth(username or "nobody", password or "nobody", request.url.path):
    #     raise HTTPException(status_code=403, detail="Forbidden")

    request.state.username = username
    logger.debug("[middleware] Authenticated.")
    return await call_next(request)


@app.get(
    "/",
    response_class=PlainTextResponse,
    response_model=str,
    summary="Greet the user",
    responses={200: {"content": {"text/plain": {"example": "Hello, user1!"}}}},
)
async def greet_user(request: Request):
    """Greet the user."""
    username = request.state.username or "nobody"
    return PlainTextResponse(f"Hello, {username}!")


@app.get(
    "/foo",
    response_class=PlainTextResponse,
    response_model=str,
    summary="Get the value of `foo`",
    responses={200: {"content": {"text/plain": {"example": "Hello, World!"}}}},
)
async def get_foo():
    """Get the value of `foo`, which is loaded from environment variables or the .env file.

    The order of precedence for loading the value is:
    1. `TEST_API_FOO` environment variable
    2. `TEST_API_FOO` variable in the .env file
    3. Default value defined in the code (`default_value`)
    """
    return PlainTextResponse(settings.foo)


@app.get(
    "/health",
    response_class=PlainTextResponse,
    response_model=str,
    summary="Health check",
    responses={200: {"content": {"text/plain": {"example": "OK"}}}},
)
async def health():
    """Health check endpoint."""
    return PlainTextResponse("OK")
