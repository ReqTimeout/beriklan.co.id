-- Migration 0009: API Keys table
-- P0.3 API Key Rotation Policy (90 days)

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    -- Hash for verification (never store raw key)
    key_hash TEXT NOT NULL,
    -- Key prefix for identification (first 8 chars of raw key)
    key_prefix TEXT NOT NULL,
    -- Last 4 chars for visual ID
    key_suffix TEXT,
    -- Rotation tracking
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_rotated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    -- Status: active, rotated, revoked
    status TEXT NOT NULL DEFAULT 'active',
    -- Last used timestamp (for usage tracking)
    last_used_at TEXT,
    -- Number of times used
    use_count INTEGER DEFAULT 0,
    -- Who created/rotated it
    rotated_by TEXT
);

-- Index for fast lookups by name (active keys)
CREATE INDEX IF NOT EXISTS idx_api_keys_name_status
    ON api_keys (name, status);

-- Index for expiry check queries
CREATE INDEX IF NOT EXISTS idx_api_keys_expires
    ON api_keys (expires_at);

-- Track key usage events (for audit log)
CREATE TABLE IF NOT EXISTS api_key_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    ip TEXT,
    user_agent TEXT,
    status TEXT NOT NULL, -- success, expired, revoked, rate_limited
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_key_usage_name_time
    ON api_key_usage (key_name, timestamp);

CREATE INDEX IF NOT EXISTS idx_api_key_usage_timestamp
    ON api_key_usage (timestamp);