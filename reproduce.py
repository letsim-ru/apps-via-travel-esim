#!/usr/bin/env python3
"""Reproduce service availability statuses of the dataset from OONI.

Reads exit country codes and destination codes from data.csv, queries the OONI aggregation API
for the same 60-day window and applies the same status rules. Prints rows that differ from data.csv.

    python3 reproduce.py [--since 2026-09-25 --until 2026-11-24]

Rules (see README.md):
  ok_rate = ok_count / (measurement_count - failure_count)
  available - >= 30 measurements, ok_rate >= 0.9 and confirmed blocks < 1 %
  blocked   - confirmed blocks > 10 % or ok_rate < 0.6
  unstable  - in between;  no_data - fewer than 30 measurements
Groups of countries (FR/NL/UK) take the worst status; Europe/EU are measured as NL, FR, DE.
OONI data: CC BY-NC-SA 4.0, https://ooni.org
"""
import csv, json, sys, time, urllib.request

API = 'https://api.ooni.io/api/v1/aggregation'
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SINCE, UNTIL = arg('--since', '2026-09-25'), arg('--until', '2026-11-24')
SERVICES = {'whatsapp': ('whatsapp', None), 'telegram': ('telegram', None), 'google': ('web_connectivity', 'www.google.com'),
            'youtube': ('web_connectivity', 'www.youtube.com'), 'instagram': ('web_connectivity', 'www.instagram.com')}
GROUPS = {'Europe': ['NL', 'FR', 'DE'], 'EU': ['NL', 'FR', 'DE']}
CODE = {'UK': 'GB'}
RANK = {'available': 0, 'no_data': 1, 'unstable': 2, 'blocked': 3}
cache = {}


def agg(cc, test, domain):
    q = f'{API}?probe_cc={cc}&test_name={test}&since={SINCE}&until={UNTIL}' + (f'&domain={domain}' if domain else '')
    if q not in cache:
        for attempt in range(6):
            try:
                time.sleep(4)
                with urllib.request.urlopen(urllib.request.Request(q, headers={'User-Agent': 'reproduce-apps-via-esim/1'}), timeout=90) as r:
                    cache[q] = json.load(r)['result']
                break
            except Exception:  # noqa: BLE001 - rate limits: wait longer
                time.sleep(60 * (attempt + 1))
    return cache.get(q)


def status(r):
    if not r or r['measurement_count'] < 30:
        return 'no_data'
    valid = max(r['measurement_count'] - r['failure_count'], 1)
    rate, conf = r['ok_count'] / valid, r['confirmed_count'] / valid
    if conf > 0.1 or rate < 0.6:
        return 'blocked'
    return 'available' if rate >= 0.9 and conf < 0.01 else 'unstable'


def exit_status(code, svc):
    members = [CODE.get(c, c) for c in (GROUPS.get(code) or code.split('/'))]
    return max((status(agg(m, *SERVICES[svc])) for m in members), key=RANK.get)


rows = list(csv.DictReader(open('data.csv', encoding='utf-8-sig'), delimiter=';'))
diff = 0
for r in rows:
    for svc in SERVICES:
        got = exit_status(r['exit_code'], svc)
        if got != r[f'via_esim_{svc}']:
            diff += 1
            print(f"{r['country_code']} via {r['exit_code']} {svc}: dataset={r[f'via_esim_{svc}']} now={got}")
        if r[f'in_country_{svc}']:
            got = status(agg(r['country_code'], *SERVICES[svc]))
            if got != r[f'in_country_{svc}']:
                diff += 1
                print(f"{r['country_code']} in-country {svc}: dataset={r[f'in_country_{svc}']} now={got}")
print(f'differences: {diff}')
