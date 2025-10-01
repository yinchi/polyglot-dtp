# PostgreSQL database with TimescaleDB extension

- [Docker Hub entry](https://hub.docker.com/r/timescale/timescaledb)
- [PSQL command reference](https://www.postgresql.org/docs/current/sql-commands.html)
- [TimescaleDB readme](https://github.com/timescale/timescaledb/blob/main/README.md)

Directory structure:

- `compose.include.yaml`: Defines the service to be merged into the main Docker Compose file. Also defines the Docker volume for Postgres data.
- `Dockerfile`: Defines an Apache server with [PhpPgAdmin](https://github.com/phppgadmin/phppgadmin).
- `init/`: Startup scripts executed when initializing the database (first run only)
- `phppgadmin/`: Apache and PHP configuration files for the PhpPgAdmin service.

The `setup.sh` script installs the `pgcli` command-line tool, while `just pgcli` automatically connects `pgcli` to this database.
