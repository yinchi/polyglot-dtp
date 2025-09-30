-- A simple event log database table that does not rely on the TimescaleDB extension.
CREATE TABLE IF NOT EXISTS event_log(
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity INT NOT NULL DEFAULT 0, -- 0: info, 1: warning, 2: error, 3: critical
    source TEXT, -- e.g. "twin/service-id"
    body JSONB NOT NULL DEFAULT '{}'::JSONB
);
CREATE INDEX IF NOT EXISTS idx_event_log_ts ON event_log(ts DESC);
