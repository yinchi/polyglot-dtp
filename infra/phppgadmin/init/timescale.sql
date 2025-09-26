CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Signal metadata table
-- -------------------------------------------------------------------------------------------------
-- A signal represents a sensor or measurement point, identified by a unique signal_id (UUID).
-- Each signal has a name (e.g. "temp_room_1") and an optional unit.
-- In general, `unit` should be non-null only if its associated observations are numeric.
-- -------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS signal(
    signal_id UUID PRIMARY KEY,
    name TEXT NOT NULL, -- e.g. "temp_room_1"
    unit TEXT -- e.g. "°C", "kPa", "m/s", "ppm", etc.
);

-- Observations table
-- -------------------------------------------------------------------------------------------------
-- An observation is a time-series data point associated with a signal (identified by signal_id).
-- An observation may have a numeric value (value_double), a text value (value_text), or a
-- complex value (quality, JSONB).  If more than one of these fields are non-null, the
-- interpretation is up to the application.
-- -------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS observation(
    signal_id UUID NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    value_double DOUBLE PRECISION,
    value_text TEXT,
    quality JSONB NOT NULL DEFAULT '{}'::JSONB,
    source TEXT, -- e.g. "twin/service-id"
    PRIMARY KEY(signal_id, ts),
    FOREIGN KEY (signal_id) REFERENCES signal(signal_id)
);
SELECT create_hypertable('observation', 'ts', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_observation_ts ON observation(ts DESC);
