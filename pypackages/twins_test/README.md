# Test/template digital twin module

This template module contains a `uv` project representing a dummy digital twin module.

**To launch locally:**
```bash
cd $(git root)
chmod +x pypackages/twins_test/launch.sh 
./pypackages/twins_test/launch.sh 
```

This exposes the FastAPI app at <http://localhost:8000>.  Auto-generated documentation is available at <http://localhost:8000/docs>.

**To launch in Docker:**
```bash
cd $(git root)
docker compose up twins-test -d
```
Use the `-f` and `--env-file` flags to configure Docker Compose if necessary (see `docker compose --help`).

Alternatively, use `just docker-up` to launch the entire Docker Compose stack, starting missing services as needed.

## Using this module as a template

The root `pyproject.toml` for our workspace includes all projects in `pypackages/`, so we don't need to alter it.  Instead, just copy the project:

```bash
rsync -rv --exclude='__pycache__' pypackages/twins_test/ pypackages/twins_testcopy
mv pypackages/twins_testcopy/src/polyglot_dtp/twins/test \
    pypackages/twins_testcopy/src/polyglot_dtp/twins/testcopy
```

**EDIT YOUR FILES** as follows:
- `README.md`: edit this README to describe the new digital twin.
- `pyproject.toml`: Python project metadata used by `uv`.  Needs editing.
- `Dockerfile`: edit this to point Docker to the new Python package and FastAPI entrypoint.
- `compose.include.yaml`: edit this to describe the new Docker Compose service.
- `launch.sh`: launches the FastAPI server locally without using Docker or Kubernetes.

Next, update the `uv` workspace:
```bash
just uv-sync
```

Finally to add your new digital twin to the Docker Compose stack, add the new `compose.include.yaml`, with your edits, to the `include` section of your main `compose.yaml`.

>[!NOTE]
> Kubernetes deployment details to be added.
