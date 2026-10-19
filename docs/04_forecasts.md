# 04 — Forecasts: P5MIN, predispatch, and how to use them honestly

**Audience:** engineering & data science · **Owner:** Data · **Last reviewed:** 2024-09-02

We have two families of AEMO forecast in the real market. Both are **vintages**: a run published at
time τ describes intervals *after* τ. Using the wrong vintage is the single most common way an energy
model quietly cheats.

> **In this sample you only get P5MIN.** The half-hourly predispatch family is described below for
> context — it exists in the real NEM and in our production data — but it is **not** in the sample
> Parquet files, so every forecast you use in this exercise is P5MIN.

## P5MIN (`p5min_regionsolution`)

- **Published every 5 minutes** (`RUN_DATETIME`).
- Forecasts **5-minute intervals** out a short horizon (roughly the next hour, in 5-minute steps).
- This is the forecast closest to real-time — the most accurate short-horizon view, and the one an
  operator would actually bid against.
- Keyed by `(RUN_DATETIME, INTERVAL_DATETIME, REGIONID)`.

## Predispatch (`predispatchprice`) — *not in this sample*

- **Published every 30 minutes** (`LASTCHANGED` is the as-of time).
- Forecasts **half-hourly periods** out to the end of the next trading day (~2 days ahead).
- Longer horizon, coarser, less accurate — but the only source of *far* future price shape.
- Keyed by `(PREDISPATCHSEQNO, DATETIME, REGIONID)`.

## The as-of rule (non-negotiable)

> To know "what did the market expect for interval *i*", use the **latest run published at or before
> the decision time**. In this sample that is:
> `p5min_regionsolution WHERE RUN_DATETIME <= τ` → take the max `RUN_DATETIME`.

Never join a forecast to an interval by `INTERVAL_DATETIME`/`DATETIME` alone across all runs — that
silently picks the *last* run to forecast that interval, which ran minutes before the interval and has
already seen most of the price move. Backtests built this way look brilliant and lose money.

## Known data issues

- **Gaps.** AEMO's archive occasionally misses a run. The "latest available" forecast can be stale by
  more than one interval. Real systems carry a staleness check.
- **Forecast error around spikes.** Forecasts are worst exactly when money is largest: they
  systematically **under-predict** the depth and timing of price spikes. A policy that trusts the
  forecast blindly will under-discharge into spikes.
- **P5MIN covers only ~1 hour.** Beyond that you must use predispatch, which is half-hourly. Blending
  the two (P5MIN for the near hour, predispatch beyond) is the standard approach in production — but
  this sample ships P5MIN only, so any forecast you build here sees at most ~1 hour ahead.

> **Policy:** any backtest we sign off must be an **as-of** backtest. If a reviewer can't reproduce the
> vintage selection from the code, it doesn't ship. The data-science rubric marks leakage above every
> other failure.
