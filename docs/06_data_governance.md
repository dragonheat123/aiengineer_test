# 06 — Data governance & provenance

**Audience:** everyone · **Owner:** Data · **Last reviewed:** 2024-09-02

## Source

All market data in `data/*.parquet` originates from **AEMO's NEMweb MMSDM historical archive**
(nemweb.com.au), used under AEMO's copyright permissions. It is **not redistributed** by us in
production; this sample is provided for evaluation purposes only.

## What's in the sample

Three calendar months — **January, May and August 2024** — across all five regions. Chosen to span:
summer peak demand and negative-price solar events (Jan), a shoulder month (May), and a winter month
with the year's sharpest price spikes (Aug, including the 5 Aug 2024 NSW event).

Timestamps are AEMO time (UTC+10), interval-ending. **Prices are RAW** (see `05`).

## Provenance chain

```
AEMO MMSDM monthly zip
  → scripts/pull_data.py      (extracts only the columns the platform needs)
  → data/benchmark.duckdb     (internal)
  → build_data.py             (converts to the candidate Parquet files)
  → data/*.parquet            (this sample)
```

Every transformation is deterministic and re-runnable; `build_data.py` is shipped with the sample so
the conversion is auditable.

## Quality notes and known issues

- **`INTERVENTION` is always 0** in this sample — the non-intervention (normal market) run only.
  Production data includes intervention runs; filter on `INTERVENTION = 0` anyway, out of habit.
- **`MARKETSUSPENDEDFLAG` is always 0** — the only NEM suspension (June 2021) predates the sample.
- **`APCFLAG`** takes values 0, 1, 4, 5 — AEMO's administered-pricing condition codes. Any non-zero
  means an administered price cap applied that interval; treat those intervals with care in analysis.
- **Forecast gaps.** AEMO occasionally omits a P5MIN run. "Latest available" can be
  stale. See `04_forecasts.md`.
- **NoFCAS, no demand-response, no interconnector constraints** are modelled in this sample. The
  battery here is energy-only and price-taking.

## Handling rules

- Do not attempt to re-identify commercial participants from the data; the archive is regional and
  aggregated.
- Figures quoted externally must cite "AEMO NEMweb MMSDM".
- This sample is for the take-home exercise; don't commit real analysis built on it to public repos
  without checking with Data.
