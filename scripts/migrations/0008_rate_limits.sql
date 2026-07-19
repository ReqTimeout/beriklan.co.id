-- Migration 0008: Rate limits table
-- P0.5 Rate Limit per-IP

CREATE TABLE IF NOT EXISTS rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip, endpoint, window_start)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint
    ON rate_limits (ip, endpoint, window_start);

-- Index for cleanup queries (old windows)
CREATE INDEX IF NOT EXISTS idx_rate_limits_window
    ON rate_limits (window_start);