-- Migration: add_indexing_log
-- Created: 10 Agustus 2026
-- Purpose: Track URL submission history untuk IndexNow + GSC Indexing API

CREATE TABLE IF NOT EXISTS indexing_log (
  url TEXT NOT NULL,
  channel TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (url, channel)
);

CREATE INDEX IF NOT EXISTS idx_indexing_log_submitted_at ON indexing_log(submitted_at);
CREATE INDEX IF NOT EXISTS idx_indexing_log_channel ON indexing_log(channel);

-- Cleanup old entries (>30 days) — dijalankan via cron terpisah
