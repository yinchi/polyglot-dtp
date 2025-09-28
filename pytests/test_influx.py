"""Tests for InfluxDB operations.

To run this test individually (from the Git root):
    uv run pytest -s pytests/test_pg_timescale.py

To run all tests:
    just pytest
"""

import logging
from datetime import datetime, timezone

import influxdb_client_3 as influx
import tabulate
from dotenv import dotenv_values


def test_influxdb():
    """Test reading and writing to InfluxDB."""
    token = dotenv_values()["INFLUXDB3_AUTH_TOKEN"]

    client = influx.InfluxDBClient3(
        host="http://localhost:8181",
        token=token,
        database="dtp",
    )

    ts = int(datetime.now(timezone.utc).timestamp() * 1_000_000_000)  # timestamp in nanoseconds
    line = f"test val=1 {ts}"
    logging.info(line)

    client.write(
        record=line,
        precision="s",
    )

    # Since we just wrote to the database, this should never be empty
    table = client.query(
        "SELECT time, val FROM test "
        "WHERE time >= now() - interval '1 minute' "
        "ORDER BY time DESC "
        "LIMIT 1"
    )
    df = table.to_pandas()
    for line in tabulate.tabulate(
        df, headers="keys", tablefmt="simple_outline", showindex=False
    ).splitlines():
        logging.info("%s", line)

    assert not df.empty
