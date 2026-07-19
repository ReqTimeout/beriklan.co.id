-- P0.7 Backup Tier 3: mirror posts.json + city-content.json + keyword-to-posts.json in D1
-- Each row is one entry; metadata + content split for ergonomics

CREATE TABLE IF NOT EXISTS posts_meta (
  slug        TEXT PRIMARY KEY,
  title       TEXT,
  excerpt     TEXT,
  date        TEXT,
  iso_date    TEXT,
  category    TEXT,
  readTime    TEXT,
  tags        TEXT,  -- JSON array
  service     TEXT,
  city        TEXT,
  featured    INTEGER DEFAULT 0,
  generated   INTEGER DEFAULT 0,
  iso_updated TEXT
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS posts_content (
  slug     TEXT PRIMARY KEY,
  content  TEXT,  -- HTML (may exceed 1MB; SQLite TEXT has no limit)
  FOREIGN KEY (slug) REFERENCES posts_meta(slug) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_posts_meta_iso ON posts_meta(iso_date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_meta_service ON posts_meta(service);
CREATE INDEX IF NOT EXISTS idx_posts_meta_city ON posts_meta(city);

CREATE TABLE IF NOT EXISTS city_pages (
  route        TEXT PRIMARY KEY,  -- e.g. 'jasa-iklan-facebook/bandung/'
  service      TEXT,
  city         TEXT,
  html_content TEXT,
  iso_updated  TEXT
);
CREATE INDEX IF NOT EXISTS idx_city_pages_service ON city_pages(service);

CREATE TABLE IF NOT EXISTS keyword_map (
  keyword  TEXT PRIMARY KEY,  -- the slugified keyword
  posts    TEXT,  -- JSON array of post slugs
  intent   TEXT,
  service  TEXT,
  city     TEXT,
  iso_updated TEXT
);
CREATE INDEX IF NOT EXISTS idx_keyword_map_service ON keyword_map(service);
