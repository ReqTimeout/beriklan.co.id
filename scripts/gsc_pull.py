"""
GSC Pull — Pull Google Search Console data for beriklan.co.id
=============================================================
Uses the service account JSON (lgc-indexer-4db07b28450d.json) with GSC API.

Outputs to: web/public/data/gsc-stats.json
  {
    "last_pulled": "ISO timestamp",
    "site": "https://www.beriklan.co.id/",
    "totals": { "clicks": int, "impressions": int, "ctr": float, "position": float },
    "top_pages": [{url, clicks, impressions, ctr, position}, ...]   (last 28 days, top 25)
    "top_queries": [...]                                              (top 25)
    "by_country": [{country, clicks, impressions}, ...]               (top 10)
    "by_device": [{device, clicks, impressions}, ...]                 (top 5)
    "daily": [{date, clicks, impressions, ctr, position}, ...]        (last 28 days)
    "freshness_alerts": [                                            (impressions dropping >40% w/w)
        {url, last_week_impressions, this_week_impressions, drop_pct}
    ]
  }

Idempotent. Can be run via cron nightly.
"""
import os, sys, json, datetime, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS = os.path.join(ROOT, 'lgc-indexer-4db07b28450d.json')
OUT_PATH = os.path.join(ROOT, 'web/public/data/gsc-stats.json')

SITE = 'https://www.beriklan.co.id/'
DAYS = 28
TOP_N = 25


def fetch_analytics(service, start_date, end_date, dimensions, row_limit=100, dimension_filter=None):
    body = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': dimensions,
        'rowLimit': row_limit,
    }
    if dimension_filter:
        body['dimensionFilterGroups'] = [{'filters': [dimension_filter]}]
    return service.searchanalytics().query(siteUrl=SITE, body=body).execute()


def main():
    if not os.path.exists(CREDS):
        print(f'ERROR: credentials not found: {CREDS}')
        sys.exit(1)

    from google.oauth2 import service_account
    import googleapiclient.discovery

    credentials = service_account.Credentials.from_service_account_file(
        CREDS,
        scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )
    service = googleapiclient.discovery.build('searchconsole', 'v1', credentials=credentials, cache_discovery=False)

    end = datetime.date.today() - datetime.timedelta(days=3)  # GSC data lags ~3 days
    start = end - datetime.timedelta(days=DAYS)
    last_week_end = end
    last_week_start = end - datetime.timedelta(days=6)
    prev_week_end = last_week_start - datetime.timedelta(days=1)
    prev_week_start = prev_week_end - datetime.timedelta(days=6)

    print(f'Window: {start} to {end}')

    # Totals
    print('  fetching totals...')
    totals_resp = fetch_analytics(service, start, end, [])
    totals = {
        'clicks': int(totals_resp.get('rows', [{'clicks': 0}])[0].get('clicks', 0)) if totals_resp.get('rows') else 0,
        'impressions': int(totals_resp.get('rows', [{'impressions': 0}])[0].get('impressions', 0)) if totals_resp.get('rows') else 0,
        'ctr': float(totals_resp.get('rows', [{'ctr': 0}])[0].get('ctr', 0)) if totals_resp.get('rows') else 0,
        'position': float(totals_resp.get('rows', [{'position': 0}])[0].get('position', 0)) if totals_resp.get('rows') else 0,
    }
    if totals['impressions']:
        totals['ctr'] = round(totals['clicks'] / totals['impressions'], 4)

    # Top pages
    print('  fetching top pages...')
    pages_resp = fetch_analytics(service, start, end, ['page'], row_limit=TOP_N)
    top_pages = []
    for r in pages_resp.get('rows', []):
        top_pages.append({
            'url': r['keys'][0],
            'clicks': r['clicks'],
            'impressions': r['impressions'],
            'ctr': round(r['ctr'], 4),
            'position': round(r['position'], 1),
        })

    # Top queries
    print('  fetching top queries...')
    q_resp = fetch_analytics(service, start, end, ['query'], row_limit=TOP_N)
    top_queries = [{
        'query': r['keys'][0],
        'clicks': r['clicks'],
        'impressions': r['impressions'],
        'ctr': round(r['ctr'], 4),
        'position': round(r['position'], 1),
    } for r in q_resp.get('rows', [])]

    # By country
    print('  fetching by country...')
    c_resp = fetch_analytics(service, start, end, ['country'], row_limit=10)
    by_country = [{
        'country': r['keys'][0],
        'clicks': r['clicks'],
        'impressions': r['impressions'],
    } for r in c_resp.get('rows', [])]

    # By device
    print('  fetching by device...')
    d_resp = fetch_analytics(service, start, end, ['device'], row_limit=5)
    by_device = [{
        'device': r['keys'][0],
        'clicks': r['clicks'],
        'impressions': r['impressions'],
    } for r in d_resp.get('rows', [])]

    # Daily
    print('  fetching daily series...')
    day_resp = fetch_analytics(service, start, end, ['date'], row_limit=DAYS + 1)
    daily = [{
        'date': r['keys'][0],
        'clicks': r['clicks'],
        'impressions': r['impressions'],
        'ctr': round(r['ctr'], 4),
        'position': round(r['position'], 1),
    } for r in day_resp.get('rows', [])]

    # Freshness alerts: this week vs last week (page-level)
    print('  fetching freshness alerts (week-over-week)...')
    this_resp = fetch_analytics(service, last_week_start, last_week_end, ['page'], row_limit=500)
    prev_resp = fetch_analytics(service, prev_week_start, prev_week_end, ['page'], row_limit=500)
    this_by_page = {r['keys'][0]: r['impressions'] for r in this_resp.get('rows', [])}
    prev_by_page = {r['keys'][0]: r['impressions'] for r in prev_resp.get('rows', [])}
    freshness_alerts = []
    for url, this_imp in this_by_page.items():
        prev_imp = prev_by_page.get(url, 0)
        if prev_imp >= 20 and this_imp < prev_imp * 0.6:  # dropped >40%, only with meaningful volume
            drop_pct = round((this_imp - prev_imp) / prev_imp * 100, 1)
            freshness_alerts.append({
                'url': url,
                'last_week_impressions': prev_imp,
                'this_week_impressions': this_imp,
                'drop_pct': drop_pct,
            })
    freshness_alerts.sort(key=lambda x: x['drop_pct'])  # biggest drops first
    freshness_alerts = freshness_alerts[:30]

    # Low CTR pages: high impressions, low CTR (need title/meta fix)
    # Pull last 28 days, but for the page view
    print('  fetching low-CTR candidates (28d, by page)...')
    p28 = fetch_analytics(service, start, end, ['page'], row_limit=200)
    low_ctr = []
    for r in p28.get('rows', []):
        if r['impressions'] >= 100 and r['ctr'] < 0.02:  # <2% CTR, big sample
            low_ctr.append({
                'url': r['keys'][0],
                'clicks': r['clicks'],
                'impressions': r['impressions'],
                'ctr': round(r['ctr'], 4),
                'position': round(r['position'], 1),
            })
    low_ctr.sort(key=lambda x: -x['impressions'])
    low_ctr = low_ctr[:20]

    out = {
        'last_pulled': datetime.datetime.utcnow().isoformat() + 'Z',
        'site': SITE,
        'window': {'start': start.isoformat(), 'end': end.isoformat()},
        'totals': totals,
        'top_pages': top_pages,
        'top_queries': top_queries,
        'by_country': by_country,
        'by_device': by_device,
        'daily': daily,
        'freshness_alerts': freshness_alerts,
        'low_ctr': low_ctr,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\nWrote {OUT_PATH}')
    print(f'  totals: clicks={totals["clicks"]} impr={totals["impressions"]} ctr={totals["ctr"]} pos={totals["position"]:.1f}')
    print(f'  top_pages: {len(top_pages)}')
    print(f'  top_queries: {len(top_queries)}')
    print(f'  freshness_alerts: {len(freshness_alerts)}')


if __name__ == '__main__':
    main()
