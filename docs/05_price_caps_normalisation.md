# 05 — Price caps, floors, and normalisation across years

**Audience:** data science & engineering · **Owner:** Data · **Last reviewed:** 2024-09-02

## The problem

The market price **cap changes every 1 July**. Between October 2021 and 2024 it rose from $15,100 to
$17,500/MW·h; today it is **$23,200/MW·h**. The floor has been a steady **−$1,000/MW·h**. This means a
"$15,000 price" in 2022 and a "$15,000 price" in 2026 are *not* the same severity: the first was near
the cap (extreme scarcity), the second was a moderate spike. Comparing or pooling raw prices across
cap regimes misstates risk and flatters older years.

## The mapping

To compare across years we map each period's prices onto **today's cap**. The map is the identity up
to a **knee** of **$1,000/MW·h**, and above the knee stretches the tail so that the period's cap lands
on today's:

```
g(p) = k + (MPC_now − k) · ((p − k) / (MPC_then − k))^γ,     k = 1000, γ = 1
```

- Prices **≤ $1,000** (including all negatives and the floor) are **unchanged** — they're set by bids,
  not by the cap.
- Prices **> $1,000** are stretched so the top of the range lines up.
- γ = 1 is a linear stretch of the tail; higher γ pushes more of the tail down.

**Which cap applies:** actual prices use the cap in force when the *interval started*; forecast prices
use the cap in force when the *forecast run published*.

## Why the knee is $1,000

Analysis of the archive showed that prices between ~$300 and ~$1,000 sit at the same levels whatever
the cap — they're set by bid stacks, not scarcity. Only the extreme tail tracks the cap. So we leave
everything under the knee alone and only normalise the scarcity tail.

## The data you have

**The sample data (`data/*.parquet`) contains RAW, unmapped prices** — AEMO's published RRP as-is. This is deliberate for
this sample (it's 2024 only, one cap regime, so normalisation is a no-op anyway). But be aware:
- The 2024 cap in the data is **$17,500**, not today's $23,200.
- If you pool these with data from other years, normalise first or you'll bias the tail.
- `market_price_thresholds` holds the cap/floor history you'd need to build the map.

> **Policy:** model-risk sign-off requires either (a) all prices normalised to a single cap, or (b) a
> documented argument that the cap regime is irrelevant to the specific question. Raw cross-year
> pooling without either is an automatic rejection.
