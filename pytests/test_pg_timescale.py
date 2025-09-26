"""Tests for manipulating and querying a Postgres database with the TimescaleDB extension.

To run this test individually (from the Git root):
    uv run pytest -s pytests/test_pg_timescale.py

To run all tests:
    just pytest
"""

import random
from datetime import datetime, timedelta, timezone
from pprint import pprint
from uuid import UUID, uuid4

import pandas as pd
import psycopg
import tabulate
from dotenv import find_dotenv
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic.networks import PostgresDsn
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for connecting to the PostgreSQL database."""

    host: str = "localhost"
    port: int = 5432
    user: str = "dtp"
    password: SecretStr  # required, no default
    db: str = "dtp"

    @property
    def dsn(self) -> PostgresDsn:
        """Construct the DSN for connecting to the database.

        Since Pydantic's PostgresDsn does not support SecretStr for password,
        do not print this property.
        """
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.db,
        )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="POSTGRES_",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class Signal(BaseModel):
    """A signal in the database."""

    signal_id: UUID = PydanticField(default_factory=uuid4)
    name: str
    unit: str | None = None


class NumericObservation(BaseModel):
    """A numeric observation in the database."""

    signal_id: UUID = PydanticField(default_factory=uuid4)
    ts: datetime = PydanticField(default_factory=lambda: datetime.now(timezone.utc))
    value: float
    source: str = "test_pg_timescale"


def test_timescale():
    """Test connecting to the database, inserting and querying data."""
    # Load settings from .env file
    env_path = find_dotenv(
        filename=".env",
        raise_error_if_not_found=True,
    )
    settings = Settings(
        _env_file=env_path,
    )
    print("Settings:")
    pprint(settings.model_dump(mode="json"), sort_dicts=False)
    print()

    # Connect to the database and check TimescaleDB extension
    with psycopg.connect(str(settings.dsn)) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
            version = cur.fetchone()
            assert version is not None, "TimescaleDB extension not found"
            assert len(version) == 1, "Unexpected result from TimescaleDB version query"
            version = version[0]
            assert isinstance(version, str) and len(version) > 0, "Invalid TimescaleDB version"
            print(f"TimescaleDB version: {version}")

    # Create a new signal
    signal = Signal(
        name="temp_room_1",
        unit="°C",
    )

    # Insert the signal into the database
    with psycopg.connect(str(settings.dsn)) as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                cur.execute(
                    """\
                    INSERT INTO signal (signal_id, name, unit)
                    VALUES (%s, %s, %s);
                    """,
                    (signal.signal_id, signal.name, signal.unit),
                )
                assert cur.rowcount == 1, "Failed to insert the signal"

            # Verify the signal was inserted
            cur.execute(
                "SELECT signal_id, name, unit FROM signal WHERE signal_id = %s;",
                (signal.signal_id,),
            )
            result = cur.fetchone()
            print("Inserted signal:", result)
            assert result is not None and len(result) == 3, "Failed to insert signal"
            assert result[0] == signal.signal_id, "Signal ID mismatch"

    # Insert some observations for the signal
    with psycopg.connect(str(settings.dsn)) as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                _now = datetime.now(timezone.utc).replace(microsecond=0)
                _delta = timedelta(seconds=10)
                observations = [
                    NumericObservation(
                        ts=_now + _delta * i,
                        value=round(random.uniform(20.0, 25.0), 2),
                    )
                    for i in range(4, -1, -1)
                ]
                for obs in observations:
                    obs.signal_id = signal.signal_id
                    cur.execute(
                        """\
                        INSERT INTO observation (signal_id, ts, value_double, source)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (obs.signal_id, obs.ts, obs.value, obs.source),
                    )
                    assert cur.rowcount == 1, "Failed to insert observation"

            # Verify the observations were inserted
            cur.execute(
                """\
                SELECT observation.signal_id as signal_id, ts, name, value_double, unit, source
                FROM observation
                LEFT JOIN signal USING (signal_id)
                WHERE observation.signal_id = %s
                ORDER BY ts DESC;
                """,
                (signal.signal_id,),
            )
            result = cur.fetchall()
            print("Inserted observations (with left join):")
            obs_df = pd.DataFrame(
                result, columns=["signal_id", "ts", "name", "value_double", "unit", "source"]
            )
            print(
                tabulate.tabulate(
                    obs_df, headers="keys", tablefmt="simple_outline", showindex=False
                )
            )
            assert len(result) == 5, "Unexpected number of observations"

    # Cleanup
    with psycopg.connect(str(settings.dsn)) as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                cur.execute(
                    "DELETE FROM observation WHERE signal_id = %s;",
                    (signal.signal_id,),
                )
                print(f"Deleted {cur.rowcount} observations for signal ID: {signal.signal_id}")
                cur.execute(
                    "DELETE FROM signal WHERE signal_id = %s;",
                    (signal.signal_id,),
                )
                assert cur.rowcount == 1, "Failed to delete the signal"
                print(f"Deleted signal with ID: {signal.signal_id}")


if __name__ == "__main__":
    test_timescale()
