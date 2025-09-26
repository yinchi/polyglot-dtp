# Pytest modules for the Digtal Twin Platform

## Running a single test, with full output

```bash
cd $(git root)
uv run pytest -s pytests/test_hello.py
```

## Running all tests (summary output only)
The following will work from any directory in the project (automatic `justfile` discovery):
```bash
just pytest
```
