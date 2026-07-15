-- Cloudflare D1 schema for Beriklan.co.id SEO Automation
-- Database: beriklan-seo
-- Created: 14 Jul 2026 (Day 1)
-- See plan.md §41.4

-- Tabel untuk keyword pipeline + lifecycle tracking
CREATE TABLE IF NOT EXISTS keyword_queue (
  id TEXT PRIMARY KEY,
  keyword TEXT UNIQUE NOT NULL,
  keyword_normalized TEXT NOT NULL,
  source TEXT,
  seed TEXT,
  discovered_at TEXT,
  status TEXT DEFAULT 'pending',
  priority_score INTEGER DEFAULT 0,
  intent TEXT,
  service TEXT,
  city TEXT,
  estimated_volume INTEGER,
  rank_match_profile TEXT,
  article_slug TEXT,
  article_quality_score REAL,
  published_at TEXT,
  indexed_at TEXT,
  first_rank_at TEXT,
  best_rank INTEGER,
  current_rank INTEGER,
  revenue_30d REAL DEFAULT 0,
  revenue_total REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_q_status ON keyword_queue(status);
CREATE INDEX IF NOT EXISTS idx_q_priority ON keyword_queue(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_q_keyword ON keyword_queue(keyword_normalized);
CREATE INDEX IF NOT EXISTS idx_q_service_city ON keyword_queue(service, city);

-- Tabel untuk articles yang sudah digenerate
CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title TEXT,
  keyword_id TEXT,
  word_count INTEGER,
  h2_count INTEGER,
  h3_count INTEGER,
  faq_count INTEGER,
  keyword_density REAL,
  quality_score REAL,
  status TEXT,
  generated_at TEXT,
  published_at TEXT,
  model_used TEXT,
  prompt_version TEXT,
  FOREIGN KEY (keyword_id) REFERENCES keyword_queue(id)
);
CREATE INDEX IF NOT EXISTS idx_art_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_art_slug ON articles(slug);

-- Tabel untuk GSC rank tracking weekly
CREATE TABLE IF NOT EXISTS rank_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snapshot_date TEXT,
  keyword TEXT,
  url TEXT,
  position INTEGER,
  impressions INTEGER,
  clicks INTEGER,
  ctr REAL,
  change_from_prev INTEGER
);
CREATE INDEX IF NOT EXISTS idx_rank_date ON rank_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_rank_kw ON rank_snapshots(keyword);

-- Tabel untuk IndexNow multi-engine submission log
CREATE TABLE IF NOT EXISTS index_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT,
  engine TEXT,
  submitted_at TEXT,
  status TEXT,
  indexed_at TEXT,
  response_code INTEGER,
  attempts INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_idx_url ON index_log(url);
CREATE INDEX IF NOT EXISTS idx_idx_status ON index_log(status);

-- Tabel untuk trending article pipeline
CREATE TABLE IF NOT EXISTS trending_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_date TEXT,
  topic TEXT,
  rising_rate REAL,
  angle TEXT,
  article_slug TEXT,
  article_url TEXT,
  published_at TEXT,
  indexed_at TEXT,
  impressions_7d INTEGER DEFAULT 0,
  clicks_7d INTEGER DEFAULT 0,
  revenue_7d REAL DEFAULT 0,
  revenue_30d REAL DEFAULT 0
);

-- Tabel untuk audit log (admin actions, key rotations, etc.)
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  actor TEXT,
  action TEXT,
  target TEXT,
  details TEXT
);

-- Tabel untuk GH Actions run tracking
CREATE TABLE IF NOT EXISTS automation_health (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  workflow_name TEXT,
  status TEXT,
  duration_seconds INTEGER,
  output TEXT
);

-- Tabel untuk app settings (toggle, thresholds, thresholds)
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TEXT
);

-- Tabel untuk API key rotation tracking
CREATE TABLE IF NOT EXISTS api_keys (
  name TEXT PRIMARY KEY,
  provider TEXT,
  last_rotated TEXT,
  expires_at TEXT,
  status TEXT
);

-- Tabel untuk conversion tracking (WA click, phone, email, form)
CREATE TABLE IF NOT EXISTS conversion_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  cta_type TEXT,
  cta_location TEXT,
  page TEXT,
  referrer TEXT,
  user_agent TEXT,
  session_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_conv_cta ON conversion_log(cta_type);
CREATE INDEX IF NOT EXISTS idx_conv_page ON conversion_log(page);

-- Tabel untuk manual review (AI fallback exhausted, quality reject)
CREATE TABLE IF NOT EXISTS manual_review (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword_id TEXT,
  reason TEXT,
  attempts INTEGER,
  created_at TEXT,
  resolved_at TEXT,
  resolution TEXT
);

-- Tabel untuk request queue (rate limit handling)
CREATE TABLE IF NOT EXISTS request_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_type TEXT,
  payload TEXT,
  priority INTEGER DEFAULT 5,
  status TEXT DEFAULT 'pending',
  attempts INTEGER DEFAULT 0,
  last_attempt TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_rq_status ON request_queue(status);

-- Tabel untuk blocklist (rejected keywords yang tidak boleh di-mine lagi)
CREATE TABLE IF NOT EXISTS blocklist (
  keyword_pattern TEXT PRIMARY KEY,
  reason TEXT,
  added_at TEXT
);

-- Initial settings
INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES
  ('auto_run', 'true', datetime('now')),
  ('auto_generate', 'true', datetime('now')),
  ('auto_index', 'true', datetime('now')),
  ('trending_auto', 'true', datetime('now')),
  ('articles_per_hour', '10', datetime('now')),
  ('min_quality_score', '70', datetime('now')),
  ('admin_paused', 'false', datetime('now')),
  ('plan_version', '5.0', datetime('now'));
