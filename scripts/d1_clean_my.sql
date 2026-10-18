-- .my D1 pass: remove the misleading "free 15-minute consultation, contact us" claim.
-- Main live form: "... or start a free 15-minute consultation." -> "... or contact us."

UPDATE posts_content SET content =
  REPLACE(
   REPLACE(
    REPLACE(
     REPLACE(
      REPLACE(content,
      'start a free 15-minute consultation', 'contact us'),
      'Free 15-Minute Consultation', 'Contact Us'),
      'Free 15-minute Consultation', 'Contact Us'),
      'free 15-minute consultation', 'consultation'),
      'free 15-minute review', 'review')
WHERE content GLOB '*[Ff]ree 15*[Mm]inute*';

UPDATE generated_drafts SET content =
  REPLACE(
   REPLACE(
    REPLACE(
     REPLACE(
      REPLACE(content,
      'start a free 15-minute consultation', 'contact us'),
      'Free 15-Minute Consultation', 'Contact Us'),
      'Free 15-minute Consultation', 'Contact Us'),
      'free 15-minute consultation', 'consultation'),
      'free 15-minute review', 'review')
WHERE status='draft' AND content GLOB '*[Ff]ree 15*[Mm]inute*';
