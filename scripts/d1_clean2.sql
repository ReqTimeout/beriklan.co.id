-- D1 pass-2: case-variant sweep of the "free 15-min consultation" claim.
-- Drop-qualifier treatment (keeps headings/links grammatical).
-- PRESERVES: reversed "Gratis Konsultasi" (keyword slugs) and neutral "audit gratis".

UPDATE posts_content SET content =
  REPLACE(
   REPLACE(
    REPLACE(
     REPLACE(
      REPLACE(content,
      'Konsultasi 15 menit gratis', 'Konsultasi'),
      'konsultasi 15 menit gratis', 'konsultasi'),
      ' gratis 15 menit', ''),
      'Konsultasi Gratis', 'Konsultasi'),
      'Konsultasi gratis', 'Konsultasi')
WHERE content GLOB '*[Kk]onsultasi 15 [Mm]enit gratis*'
   OR content GLOB '*[Gg]ratis 15 [Mm]enit*'
   OR content GLOB '*Konsultasi [Gg]ratis*';

UPDATE generated_drafts SET content =
  REPLACE(
   REPLACE(
    REPLACE(
     REPLACE(
      REPLACE(content,
      'Konsultasi 15 menit gratis', 'Konsultasi'),
      'konsultasi 15 menit gratis', 'konsultasi'),
      ' gratis 15 menit', ''),
      'Konsultasi Gratis', 'Konsultasi'),
      'Konsultasi gratis', 'Konsultasi')
WHERE status='draft' AND (
      content GLOB '*[Kk]onsultasi 15 [Mm]enit gratis*'
   OR content GLOB '*[Gg]ratis 15 [Mm]enit*'
   OR content GLOB '*Konsultasi [Gg]ratis*');
