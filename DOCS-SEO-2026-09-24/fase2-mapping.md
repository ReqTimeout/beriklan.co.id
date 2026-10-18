# Fase 2.1 — Schema Mapping: D1 (beriklan-seo) → Postgres (coid.*)

**Tanggal:** 2026-09-24 (audit)  
**Sumber:** `PRAGMA table_info` D1 (live) + `information_schema.columns` Postgres (live)  
**Verdict:** semua kolom target tercakup; tidak ada data loss; kolom Postgres **hanya** schema baru akan NULL saat backfill awal.

## Summary per tabel

| Tabel | D1 cols | PG cols | Match nama kolom |
|---|---|---|---|
| `posts_meta` | 19 | 20 | ⚠️ diverge |
| `posts_content` | 2 | 3 | ⚠️ diverge |
| `keyword_queue` | 22 | 26 | ⚠️ diverge |
| `generated_drafts` | 12 | 13 | ⚠️ diverge |
| `pending_indexing` | 12 | 13 | ⚠️ diverge |
| `keyword_ranks` | 9 | 10 | ⚠️ diverge |
| `growth_log` | 13 | 14 | ⚠️ diverge |

## Divergences (kolom D1 yang tidak ada di PG, atau sebaliknya)

### `posts_meta`
- **PG only (1):** `synced_from_d1_at`

### `posts_content`
- **PG only (1):** `synced_from_d1_at`

### `keyword_queue`
- **PG only (4):** `created_at`, `d1_id`, `language`, `synced_from_d1_at`

### `generated_drafts`
- **PG only (1):** `synced_from_d1_at`

### `pending_indexing`
- **PG only (1):** `synced_from_d1_at`

### `keyword_ranks`
- **PG only (1):** `synced_from_d1_at`

### `growth_log`
- **PG only (1):** `synced_from_d1_at`

## Type mapping per kolom

### `posts_meta`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `category` | TEXT | text |  |
| `city` | TEXT | text |  |
| `ctr_fixed_at` | TEXT | text |  |
| `date` | TEXT | text |  |
| `enriched_at` | TEXT | text |  |
| `excerpt` | TEXT | text |  |
| `featured` | INTEGER | integer |  |
| `generated` | INTEGER | integer |  |
| `iso_date` | TEXT | text |  |
| `iso_updated` | TEXT | text |  |
| `last_distributed_at` | TEXT | text |  |
| `readTime` | TEXT | text |  |
| `refreshed_at` | TEXT | text |  |
| `seo_description` | TEXT | text |  |
| `seo_title` | TEXT | text |  |
| `service` | TEXT | text |  |
| `slug` | TEXT | text |  |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |
| `tags` | TEXT | text |  |
| `title` | TEXT | text |  |

### `posts_content`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `content` | TEXT | text |  |
| `slug` | TEXT | text |  |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |

### `keyword_queue`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `article_quality_score` | REAL | double precision | **type diverge** |
| `article_slug` | TEXT | text |  |
| `best_rank` | INTEGER | integer |  |
| `city` | TEXT | text |  |
| `created_at` | — | timestamp with time zone | **type diverge** |
| `current_rank` | INTEGER | integer |  |
| `d1_id` | — | text | **type diverge** |
| `discovered_at` | TEXT | text |  |
| `estimated_volume` | INTEGER | integer |  |
| `first_rank_at` | TEXT | text |  |
| `id` | TEXT | bigint | **type diverge** |
| `indexed_at` | TEXT | text |  |
| `intent` | TEXT | text |  |
| `keyword` | TEXT | text |  |
| `keyword_normalized` | TEXT | text |  |
| `language` | — | text | **type diverge** |
| `priority_score` | INTEGER | integer |  |
| `published_at` | TEXT | timestamp with time zone | **type diverge** |
| `rank_match_profile` | TEXT | text |  |
| `revenue_30d` | REAL | double precision | **type diverge** |
| `revenue_total` | REAL | double precision | **type diverge** |
| `seed` | TEXT | text |  |
| `service` | TEXT | text |  |
| `source` | TEXT | text |  |
| `status` | TEXT | text |  |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |

### `generated_drafts`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `city` | TEXT | text |  |
| `committed_at` | TEXT | text |  |
| `content` | TEXT | text |  |
| `created_at` | TEXT | text |  |
| `id` | INTEGER | bigint | **type diverge** |
| `intent` | TEXT | text |  |
| `priority_score` | INTEGER | integer |  |
| `service` | TEXT | text |  |
| `slug` | TEXT | text |  |
| `source` | TEXT | text |  |
| `status` | TEXT | text |  |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |
| `title` | TEXT | text |  |

### `pending_indexing`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `created_at` | TIMESTAMP | timestamp with time zone | **type diverge** |
| `error` | TEXT | text |  |
| `gsc_submitted_at` | TEXT | text |  |
| `id` | INTEGER | bigint | **type diverge** |
| `index_checked_at` | TEXT | text |  |
| `index_state` | TEXT | text |  |
| `indexnow_at` | TEXT | text |  |
| `resubmit_count` | INTEGER | integer |  |
| `source` | TEXT | text |  |
| `status` | TEXT | text |  |
| `submitted_at` | TIMESTAMP | timestamp with time zone | **type diverge** |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |
| `url` | TEXT | text |  |

### `keyword_ranks`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `clicks` | INTEGER | integer |  |
| `created_at` | TEXT | text |  |
| `ctr` | REAL | double precision | **type diverge** |
| `date` | TEXT | text |  |
| `id` | INTEGER | bigint | **type diverge** |
| `impressions` | INTEGER | integer |  |
| `keyword` | TEXT | text |  |
| `page_url` | TEXT | text |  |
| `position` | REAL | double precision | **type diverge** |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |

### `growth_log`
| Column | D1 type | PG type | Notes |
|---|---|---|---|
| `action` | TEXT | text |  |
| `after_json` | TEXT | text |  |
| `ai_model` | TEXT | text |  |
| `before_json` | TEXT | text |  |
| `created_at` | TEXT | text |  |
| `ctr` | REAL | double precision | **type diverge** |
| `error` | TEXT | text |  |
| `id` | INTEGER | bigint | **type diverge** |
| `impressions` | INTEGER | integer |  |
| `keyword` | TEXT | text |  |
| `position` | REAL | double precision | **type diverge** |
| `slug` | TEXT | text |  |
| `static_page` | INTEGER | integer |  |
| `synced_from_d1_at` | — | timestamp with time zone | **type diverge** |


## Rekomendasi ETL per tabel

| Tabel | Backfill strategy |
|---|---|
| `posts_meta` | SELECT langsung semua kolom. PK=slug TEXT. Cek duplikat sebelum COPY. |
| `posts_content` | SELECT langsung. PK=slug. JOIN dengan posts_meta untuk skip orphan slugs (opsional, semua slug di posts_content harus match posts_meta). |
| `keyword_queue` | **KEYSET pagination** wajib (391k rows). SELECT WHERE id > $last ORDER BY id LIMIT 500 (id TEXT di D1 = `kw_xxx` prefix). PG `keyword_queue.id` adalah BIGSERIAL — perlu map ke BIGINT atau ubah kolom jadi TEXT. |
| `generated_drafts` | SELECT langsung. id INTEGER D1 → BIGSERIAL PG. Perlu map id D1 ke id PG (d1_id helper?) atau biarkan id auto-generate. |
| `pending_indexing` | SELECT langsung. id INTEGER D1 → BIGSERIAL PG. Sama — d1_id helper opsional. |
| `keyword_ranks` | SELECT langsung. id INTEGER → BIGSERIAL. |
| `growth_log` | SELECT langsung. id INTEGER → BIGSERIAL. |
## Koreksi: Sample values & data quality

**Tipe TEXT dates di kedua sisi** (no diverge, salin langsung):
- `posts_meta.iso_date`: `"2026-09-24T15:00:14.341Z"` (ISO 8601, sortable lexicographically)
- `posts_meta.enriched_at/ctr_fixed_at/refreshed_at`: TEXT (NULL untuk artikel yang belum di-growth)
- `generated_drafts.committed_at/created_at`: TEXT (ISO)
- `keyword_ranks.date`: TEXT
- `growth_log.created_at`: TEXT

**TIMESTAMP → TIMESTAMPTZ diverge (perlu CAST)** hanya di `pending_indexing`:
- `created_at`: `"2026-07-19 15:12:38"` (SQLite format, space separator, no TZ)
- `submitted_at`: sama
- Solusi: PG auto-cast accepts `'2026-07-19 15:12:38'::TIMESTAMP`, atau eksplisit `TO_TIMESTAMP(created_at, 'YYYY-MM-DD HH24:MI:SS')`

**Data quality: keyword_queue.id NULL**:
- D1 schema: `id TEXT` **nullable** (notnull=0)
- Sample populated: `"kw_jasa_pembuat_web_0"`, `"kw_situs_web_1"`, dll
- **27.811 dari 391.482 rows (7,1%) punya id NULL** — legacy data quality issue, bukan blocker ETL
- Rekomendasi: ETL preserve NULL; PG `d1_id` kolom sudah TEXT nullable. Fase 3 (kalau perlu JOIN by d1_id) bisa pakai rowid D1 sebagai natural key.

**Rekomendasi ETL final** (revisi):

| Tabel | Strategy | Catatan |
|---|---|---|
| `posts_meta` | SELECT langsung, COPY | TEXT dates no-op |
| `posts_content` | SELECT langsung, COPY | TEXT dates no-op |
| `keyword_queue` | KEYSET `WHERE rowid > $last ORDER BY rowid LIMIT 500` (rowid, bukan id) | 391k rows; `d1_id = id` (preserve NULL) |
| `generated_drafts` | SELECT langsung, COPY | INTEGER id → BIGSERIAL auto; no FK pressure |
| `pending_indexing` | SELECT langsung, COPY | TIMESTAMP cols perlu explicit CAST atau PG implicit cast works |
| `keyword_ranks` | SELECT langsung, COPY | REAL → double precision auto-cast |
| `growth_log` | SELECT langsung, COPY | Append-only, idempotent re-run safe |
