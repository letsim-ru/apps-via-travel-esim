# Which apps work through travel eSIMs — 196 countries

**Какие приложения работают через туристические eSIM — исследование по 196 странам**

Open dataset by [Letsim](https://letsim.ru) (letsim.ru).

**Disclosure:** conducted by Letsim, a commercial travel eSIM provider that sells the plans discussed here. Data, rules and raw inputs are published so that the results can be checked independently.

Measurement data: [OONI — Open Observatory of Network Interference](https://ooni.org).
Page with findings and methodology (in Russian): https://letsim.ru/issledovaniya/prilozheniya-cherez-esim

## What is inside

Travel eSIMs usually work as international roaming: user traffic exits to the internet not in the visited country but in the country of the network the plan is connected through. Which apps open therefore depends on that exit country.

For each of 196 destinations with own eSIM plans the dataset lists:

- the exit country (or group of countries) for each plan variant — from the eSIM profile supplier's plan data (`ipExport`);
- availability of Google, YouTube, WhatsApp, Telegram and Instagram in the exit country, from aggregated OONI measurements;
- availability of the same services in the visited country itself, for the 40 most popular destinations.

Key findings (measurement window 25 Sep — 24 Nov 2026, 2.38 million OONI measurements):

- 190 of 196 destinations exit to the internet through another country, not through the visited country's network;
- based on plan routing and OONI measurements, Google Search, YouTube, WhatsApp, Telegram and Instagram are expected to be available in all 196 destinations (for 21 destinations with an unspecified European exit — estimated from the Netherlands, France and Germany); working through a specific eSIM was not tested;
- in China all five services are restricted locally, while travel eSIM traffic exits via Hong Kong or Singapore; in Tanzania Telegram is restricted locally.

## Files

| File | Rows | Description |
|---|---|---|
| `data.csv` | 206 | One row per destination × exit country. UTF-8 with BOM, `;` separator |
| `data.json` | 206 | Same data in JSON with metadata |
| `measurements.csv` | 285 | Raw OONI counters per country × service: measurement, ok, anomaly, confirmed and failure counts, ok rate, confirmed rate, status, rules version and an OONI Explorer link to the same measurements |
| `classify.py` | — | Offline: applies rules v1 to `measurements.csv` and reproduces every status of `measurements.csv` and `data.csv` (0 mismatches on release v1) |
| `reproduce.py` | — | Re-queries OONI for the same window and reports differences from `data.csv` |

### Columns (`data.csv`)

| Column | Meaning |
|---|---|
| `country_code` | ISO 3166-1 alpha-2 code of the destination |
| `country_ru` | Destination name in Russian |
| `world_region` | Part of the world (Russian) |
| `exit_code` | Exit country code as given by the supplier: ISO code, a group like `FR/NL/UK` (one of these countries), or `Europe`/`EU` (European exit, country not specified) |
| `exit_country_ru` | Exit country name in Russian |
| `plans` | Which plans of the destination use this exit (packs, unlimited tiers, Premium) |
| `local_breakout` | 1 if traffic exits in the visited country itself |
| `via_esim_<service>` | Availability in the exit country: `available`, `unstable`, `blocked`, `no_data` |
| `in_country_<service>` | Availability in the visited country (empty if not measured) |
| `page_url` | Destination page on letsim.ru |

## Provenance

- Routing snapshot (exit countries): 23 November 2026.
- OONI measurement window: 25 September — 24 November 2026.
- Status rules: version `v1` (below). `data.json` contains the same in its `provenance` block.
- Not included: number of networks (ASN) behind the measurements.

## Methodology

- **Exit country**: supplier plan data (`ipExport`) for every pack and unlimited plan of a destination; if variants differ, each exit is a separate row.
- **Availability**: OONI aggregation API (`api.ooni.io/api/v1/aggregation`), 60-day window, tests `whatsapp`, `telegram` and `web_connectivity` for `www.google.com` (Google Search, not Maps), `www.youtube.com`, `www.instagram.com`.
  - `ok_rate = ok_count / (measurement_count − failure_count)`;
  - `available` — at least 30 measurements, ok_rate ≥ 0.9 and confirmed blocks < 1 %;
  - `blocked` — confirmed blocks > 10 % or ok_rate < 0.6;
  - `unstable` — in between; `no_data` — fewer than 30 measurements.
  - Isolated confirmed blocks (school, corporate or parental filters) do not mark a whole country as blocked.
  - Groups of countries take the worst status among members; `Europe`/`EU` are measured as Netherlands, France and Germany.
- **Limitations**: an inference from routing and measurements, not an in-trip test. The OONI WhatsApp test checks reachability of the app, registration and web endpoints, not voice calls; website checks do not measure video speed. An OONI anomaly is not always censorship. Services may geo-restrict by IP themselves.
- Independent evidence that travel eSIMs exit in third countries: Jang, Varvello, Lutu, Zaki, *Roam Without a Home: Unraveling the Airalo Ecosystem*, IMC 2025, doi:10.1145/3730567.3764473.

## Versions

Release v1 — 24 November 2026. Frozen copies on the website: `https://letsim.ru/issledovaniya/prilozheniya-cherez-esim/v1-2026-11-24/` (`data.csv`, `data.json`, `measurements.csv`). Files at the page root are updated with new data; archived versions with a DOI are on Zenodo.

## License and citation

OONI measurement data are published under **CC BY-NC-SA 4.0**; this derived dataset is released under the same license: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Cite as: *Letsim (letsim.ru). Which apps work through travel eSIMs: 196 countries. 2026. Measurement data: Open Observatory of Network Interference (OONI), ooni.org.*

Updated every 1–2 months together with the OONI window and plan routing.
