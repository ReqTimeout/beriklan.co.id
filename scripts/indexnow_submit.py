"""
IndexNow Auto-Submit
====================
Submits URLs to IndexNow (Bing, Seznam, Naver) for faster indexing.

IndexNow batch API: POST up to 10,000 URLs in one request.
Endpoint: https://api.indexnow.org/indexnow

Key file location: web/public/INDEXNOW_KEY.txt
The key MUST also exist at: https://beriklan.co.id/INDEXNOW_KEY.txt
(bing verifies ownership by GETting that URL)

Modes:
  --all         Submit ALL URLs from sitemap-blog.xml (newest posts first)
  --urls FILE   Submit URLs listed in a file (one per line)
  --sitemap     Submit URLs from all sitemap-*.xml
  --since DAYS  Only submit URLs whose lastmod >= now - DAYS (default: 7)
  --dry-run     Print URLs without submitting

Usage after deploy:
  python3 scripts/indexnow_submit.py --sitemap --since 7

Logs to: logs/indexnow.log (append)
"""
import os, sys, re, json, time, datetime, urllib.request, urllib.error, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'web')
DIST = os.path.join(WEB, 'dist')
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

SITE = 'https://beriklan.co.id'
KEY_PATH = os.path.join(WEB, 'public/INDEXNOW_KEY.txt')
KEY = open(KEY_PATH).read().strip() if os.path.exists(KEY_PATH) else None

ENDPOINT = 'https://api.indexnow.org/indexnow'


def log(msg):
    line = f'[{datetime.datetime.utcnow().isoformat()}] {msg}'
    print(line)
    try:
        with open(os.path.join(LOG_DIR, 'indexnow.log'), 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass


def submit(urls):
    """Submit batch to IndexNow API."""
    if not KEY:
        log('ERROR: No IndexNow key. Run: python3 -c "import secrets; open(\'web/public/INDEXNOW_KEY.txt\',\'w\').write(secrets.token_hex(16))"')
        return False
    if not urls:
        log('No URLs to submit.')
        return True
    # IndexNow batch max 10,000
    chunk_size = 10000
    submitted = 0
    ok_count = 0
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        payload = {
            'host': 'beriklan.co.id',
            'key': KEY,
            'keyLocation': f'{SITE}/INDEXNOW_KEY.txt',
            'urlList': chunk,
        }
        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'Mozilla/5.0 (compatible; BeriklanIndexNow/1.0; +https://beriklan.co.id/)',
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                if 200 <= status < 300:
                    ok_count += len(chunk)
                    log(f'OK {status}: submitted {len(chunk)} URLs (cumulative: {ok_count}/{len(urls)})')
                else:
                    log(f'WARN status={status}: {resp.read().decode()[:200]}')
        except urllib.error.HTTPError as e:
            log(f'ERR status={e.code}: {e.read().decode()[:200]}')
        except Exception as e:
            log(f'ERR {type(e).__name__}: {e}')
        submitted += len(chunk)
        time.sleep(0.2)  # polite throttle
    log(f'Done: {ok_count}/{len(urls)} accepted')
    return ok_count > 0


def extract_sitemap_urls(sitemap_path, since_days=None):
    """Parse sitemap XML and return URLs (filtered by lastmod if since_days given)."""
    if not os.path.exists(sitemap_path):
        return []
    text = open(sitemap_path).read()
    urls = []
    threshold = None
    if since_days:
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=since_days)
    for m in re.finditer(r'<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', text):
        url, lastmod = m.group(1), m.group(2)
        if threshold:
            try:
                lm = datetime.datetime.fromisoformat(lastmod.replace('Z', '+00:00').replace('+00:00', ''))
                if lm < threshold:
                    continue
            except Exception:
                pass
        urls.append(url)
    return urls


def main():
    args = sys.argv[1:]
    if not args or '--help' in args:
        print(__doc__)
        return

    urls = []
    since = None
    dry = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']

    if '--sitemap' in args:
        for f in sorted(glob_files(os.path.join(DIST, 'sitemap-*.xml'))):
            u = extract_sitemap_urls(f, since_days=since)
            urls.extend(u)
            log(f'  + {len(u):5d} from {os.path.basename(f)}')
    elif '--urls' in args:
        idx = args.index('--urls')
        fp = args[idx + 1]
        urls = [l.strip() for l in open(fp) if l.strip()]
    elif '--all' in args:
        for f in sorted(glob_files(os.path.join(DIST, 'sitemap-*.xml'))):
            u = extract_sitemap_urls(f, since_days=since)
            urls.extend(u)
            log(f'  + {len(u):5d} from {os.path.basename(f)}')

    # de-dupe
    urls = sorted(set(urls))
    log(f'Total unique URLs to submit: {len(urls)}')

    if dry:
        log('DRY RUN — not submitting. Sample:')
        for u in urls[:5]:
            log(f'  {u}')
        return

    submit(urls)


def glob_files(p):
    import glob
    return glob.glob(p)


if __name__ == '__main__':
    main()
