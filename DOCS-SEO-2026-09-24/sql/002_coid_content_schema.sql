-- 002_coid_content_schema.sql
-- Fase 0.13 (tracker TASKTRACKER-SEO-MASTER) — skema Postgres untuk migrasi konten beriklan.co.id
-- Target: database `seopipe` (container vonbh1dpbrfzlrm26lwvdain), schema `coid`
--
-- PRINSIP:
--   * 100% ADITIF. Semua CREATE TABLE / CREATE INDEX pakai IF NOT EXISTS.
--   * ALTER TABLE hanya ADD COLUMN IF NOT EXISTS -> tidak ada data yang hilang/berubah.
--   * Tidak ada DROP, tidak ada TRUNCATE, tidak ada DELETE.
--   * Kolom diturunkan dari skema D1 `beriklan-seo` (backup/beriklan-seo-20260924.sql),
--     bukan dikarang. Tipe SQLite -> PostgreSQL:
--       TEXT -> TEXT | INTEGER -> INTEGER | REAL -> DOUBLE PRECISION
--       INTEGER PRIMARY KEY AUTOINCREMENT -> BIGSERIAL PRIMARY KEY
--       kolom waktu yang di D1 bertipe TEXT tetap TEXT (format campur: 'YYYY-MM-DD HH:MM:SS' dan ISO 'Z')
--   * `coid.keyword_queue` dan `coid.publish_outbox` SUDAH ADA (dipakai app seo-pipeline yang hidup)
--     -> hanya diperlebar, tidak diganti.
--
-- Dijalankan dengan: psql -U seopipe -d seopipe -v ON_ERROR_STOP=1 -f 002_coid_content_schema.sql

BEGIN;

-- =====================================================================
-- 1. posts_meta  (D1: 16.686 baris) — metadata artikel, PK slug
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.posts_meta (
  slug                TEXT PRIMARY KEY,
  title               TEXT,
  excerpt             TEXT,
  date                TEXT,
  iso_date            TEXT,
  category            TEXT,
  "readTime"          TEXT,
  tags                TEXT,                      -- JSON array sebagai TEXT (sama seperti D1)
  service             TEXT,
  city                TEXT,
  featured            INTEGER DEFAULT 0,
  generated           INTEGER DEFAULT 0,
  iso_updated         TEXT,
  seo_title           TEXT,
  seo_description     TEXT,
  enriched_at         TEXT,
  ctr_fixed_at        TEXT,
  refreshed_at        TEXT,
  last_distributed_at TEXT,
  synced_from_d1_at   TIMESTAMPTZ                -- jejak backfill (tidak ada di D1)
);

-- Index yang sama dengan D1 + index komposit hasil insiden kuota 2 Sep 2026
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_iso        ON coid.posts_meta (iso_date DESC);
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_service    ON coid.posts_meta (service);
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_city       ON coid.posts_meta (city);
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_svc_iso    ON coid.posts_meta (service, iso_date DESC);
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_city_iso   ON coid.posts_meta (city, iso_date DESC);
CREATE INDEX IF NOT EXISTS idx_coid_posts_meta_category   ON coid.posts_meta (category);

-- =====================================================================
-- 2. posts_content  (D1: 16.686 baris) — HTML artikel, PK slug, FK cascade
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.posts_content (
  slug              TEXT PRIMARY KEY,
  content           TEXT,
  synced_from_d1_at TIMESTAMPTZ
);

-- FK dibuat terpisah supaya idempotent (ALTER ... ADD CONSTRAINT tidak punya IF NOT EXISTS)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'posts_content_slug_fkey'
      AND conrelid = 'coid.posts_content'::regclass
  ) THEN
    ALTER TABLE coid.posts_content
      ADD CONSTRAINT posts_content_slug_fkey
      FOREIGN KEY (slug) REFERENCES coid.posts_meta (slug) ON DELETE CASCADE;
  END IF;
END
$$;

-- =====================================================================
-- 3. generated_drafts  (D1: 15.352 baris) — draft/committed dari pipeline generate
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.generated_drafts (
  id             BIGSERIAL PRIMARY KEY,
  slug           TEXT UNIQUE NOT NULL,
  title          TEXT NOT NULL,
  content        TEXT NOT NULL,
  service        TEXT,
  city           TEXT,
  source         TEXT,
  status         TEXT DEFAULT 'pending',
  created_at     TEXT DEFAULT (now()::text),
  committed_at   TEXT,
  intent         TEXT,
  priority_score INTEGER DEFAULT 50,
  synced_from_d1_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_coid_gd_status  ON coid.generated_drafts (status);
CREATE INDEX IF NOT EXISTS idx_coid_gd_service ON coid.generated_drafts (service);

-- =====================================================================
-- 4. pending_indexing  (D1: 17.026 baris) — antrian submit GSC/IndexNow
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.pending_indexing (
  id               BIGSERIAL PRIMARY KEY,
  url              TEXT NOT NULL UNIQUE,
  source           TEXT DEFAULT 'manual',
  status           TEXT DEFAULT 'pending',
  error            TEXT,
  created_at       TIMESTAMPTZ DEFAULT now(),
  submitted_at     TIMESTAMPTZ,
  gsc_submitted_at TEXT,
  indexnow_at      TEXT,
  index_state      TEXT,
  index_checked_at TEXT,
  resubmit_count   INTEGER DEFAULT 0,
  synced_from_d1_at TIMESTAMPTZ
);

-- Index status = Fix 1.4a versi Postgres (hindari full scan seperti insiden D1)
CREATE INDEX IF NOT EXISTS idx_coid_pi_status        ON coid.pending_indexing (status);
CREATE INDEX IF NOT EXISTS idx_coid_pi_status_id     ON coid.pending_indexing (status, id);
CREATE INDEX IF NOT EXISTS idx_coid_pi_indexnow_at   ON coid.pending_indexing (indexnow_at);

-- =====================================================================
-- 5. keyword_ranks  (D1: 12.001 baris) — snapshot posisi dari GSC
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.keyword_ranks (
  id          BIGSERIAL PRIMARY KEY,
  keyword     TEXT NOT NULL,
  page_url    TEXT NOT NULL,
  position    DOUBLE PRECISION NOT NULL,
  clicks      INTEGER DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  ctr         DOUBLE PRECISION DEFAULT 0,
  date        TEXT NOT NULL,
  created_at  TEXT DEFAULT (now()::text),
  synced_from_d1_at TIMESTAMPTZ,
  CONSTRAINT uq_coid_keyword_ranks UNIQUE (keyword, page_url, date)
);

CREATE INDEX IF NOT EXISTS idx_coid_kr_keyword  ON coid.keyword_ranks (keyword);
CREATE INDEX IF NOT EXISTS idx_coid_kr_date    ON coid.keyword_ranks (date);
CREATE INDEX IF NOT EXISTS idx_coid_kr_position ON coid.keyword_ranks (position);

-- =====================================================================
-- 6. growth_log  — audit trail growth loop (enrich/ctr-fix/freshness)
-- =====================================================================
CREATE TABLE IF NOT EXISTS coid.growth_log (
  id          BIGSERIAL PRIMARY KEY,
  action      TEXT NOT NULL,
  slug        TEXT,
  keyword     TEXT,
  position    DOUBLE PRECISION,
  ctr         DOUBLE PRECISION,
  impressions INTEGER,
  static_page INTEGER DEFAULT 0,
  before_json TEXT,
  after_json  TEXT,
  ai_model    TEXT,
  error       TEXT,
  created_at  TEXT DEFAULT (now()::text),
  synced_from_d1_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_coid_gl_action     ON coid.growth_log (action);
CREATE INDEX IF NOT EXISTS idx_coid_gl_slug       ON coid.growth_log (slug);
CREATE INDEX IF NOT EXISTS idx_coid_gl_created_at ON coid.growth_log (created_at);

-- =====================================================================
-- 7. keyword_queue — tabel SUDAH ADA (dipakai app seo-pipeline).
--    Diperlebar agar backfill dari D1 tidak kehilangan kolom.
--    D1 punya 22 kolom; PG existing punya 13. Yang ditambah di bawah.
--    `d1_id` menyimpan PRIMARY KEY TEXT asli D1 (mis. 'kw_situs_web_1').
-- =====================================================================
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS d1_id               TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS seed                TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS discovered_at       TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS estimated_volume    INTEGER;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS rank_match_profile  TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS article_quality_score DOUBLE PRECISION;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS indexed_at          TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS first_rank_at       TEXT;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS best_rank           INTEGER;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS current_rank        INTEGER;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS revenue_30d         DOUBLE PRECISION DEFAULT 0;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS revenue_total       DOUBLE PRECISION DEFAULT 0;
ALTER TABLE coid.keyword_queue ADD COLUMN IF NOT EXISTS synced_from_d1_at   TIMESTAMPTZ;

-- UNIQUE pada d1_id dibuat hanya bila belum ada (idempotent lewat DO block)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'uq_coid_keyword_queue_d1_id'
      AND conrelid = 'coid.keyword_queue'::regclass
  ) THEN
    ALTER TABLE coid.keyword_queue ADD CONSTRAINT uq_coid_keyword_queue_d1_id UNIQUE (d1_id);
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_coid_kq_status         ON coid.keyword_queue (status);
CREATE INDEX IF NOT EXISTS idx_coid_kq_priority       ON coid.keyword_queue (priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_coid_kq_keyword_norm   ON coid.keyword_queue (keyword_normalized);
CREATE INDEX IF NOT EXISTS idx_coid_kq_service_city   ON coid.keyword_queue (service, city);

-- =====================================================================
-- 8. geo_probes — sudah ada sebagai shared.geo_mentions (jangan diduplikasi).
--    Hanya dipastikan eksis; dipakai Fase 7 (GEO keyless).
-- =====================================================================
CREATE TABLE IF NOT EXISTS shared.geo_mentions (
  id          BIGSERIAL PRIMARY KEY,
  probe_date  TEXT,
  engine      TEXT,
  query       TEXT,
  domain      TEXT,
  cited       TEXT,
  position    INTEGER,
  raw_json    TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

COMMIT;
