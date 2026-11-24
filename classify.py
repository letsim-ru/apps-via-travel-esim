#!/usr/bin/env python3
"""Reproduce availability statuses offline from measurements.csv using classification rules v1.

No network access needed. Reads raw OONI counters from measurements.csv, applies rules v1,
compares with the `status` column, then rebuilds the via-eSIM statuses of data.csv from exit countries.

    python3 classify.py

Rules v1:
  ok_rate        = ok_count / (measurement_count - failure_count)
  confirmed_rate = confirmed_count / (measurement_count - failure_count)
  available - measurement_count >= 30, ok_rate >= 0.9 and confirmed_rate < 0.01
  blocked   - confirmed_rate > 0.1 or ok_rate < 0.6
  unstable  - otherwise
  no_data   - measurement_count < 30 (or missing)
Groups of exit countries (e.g. FR/NL/UK) take the worst status of their members;
Europe/EU (country not specified by the supplier) are measured as NL, FR, DE.
"""
import csv

RULES_VERSION = 'v1'
RANK = {'available': 0, 'no_data': 1, 'unstable': 2, 'blocked': 3}
GROUPS = {'Europe': ['NL', 'FR', 'DE'], 'EU': ['NL', 'FR', 'DE']}
CODE = {'UK': 'GB'}


def classify(n, ok, confirmed, failures):
    if n is None or n < 30:
        return 'no_data'
    valid = max(n - failures, 1)
    ok_rate, conf_rate = ok / valid, confirmed / valid
    if conf_rate > 0.1 or ok_rate < 0.6:
        return 'blocked'
    return 'available' if ok_rate >= 0.9 and conf_rate < 0.01 else 'unstable'


num = lambda v: int(v) if v not in ('', None) else None
read = lambda f: list(csv.DictReader(open(f, encoding='utf-8-sig'), delimiter=';'))

# 1) statuses from raw counters
measurements = read('measurements.csv')
status = {}
mismatch = 0
for m in measurements:
    got = classify(num(m['measurement_count']), num(m['ok_count']) or 0, num(m['confirmed_count']) or 0, num(m['failure_count']) or 0)
    status[(m['scope'], m['country_code'], m['service'])] = got
    if got != m['status'] or m['rules_version'] != RULES_VERSION:
        mismatch += 1
        print(f"measurements: {m['scope']} {m['country_code']} {m['service']}: file={m['status']} rules={got}")
print(f'measurements.csv: {len(measurements)} rows, mismatches: {mismatch}')

# 2) via-eSIM statuses of data.csv from exit countries
services = ['google', 'youtube', 'whatsapp', 'telegram', 'instagram']
rows = read('data.csv')
diff = 0
for r in rows:
    members = [CODE.get(c, c) for c in (GROUPS.get(r['exit_code']) or r['exit_code'].split('/'))]
    for s in services:
        got = max((status.get(('exit', c, s), 'no_data') for c in members), key=RANK.get)
        if got != r[f'via_esim_{s}']:
            diff += 1
            print(f"data: {r['country_code']} via {r['exit_code']} {s}: file={r[f'via_esim_{s}']} rules={got}")
        local = r[f'in_country_{s}']
        if local and status.get(('destination', r['country_code'], s), local) != local:
            diff += 1
            print(f"data: {r['country_code']} in-country {s}: file={local} rules={status[('destination', r['country_code'], s)]}")
print(f'data.csv: {len(rows)} rows, mismatches: {diff}')
