# `data/*.parquet` — schema

Four **Parquet** files (zstd-compressed, ~10 MB total) of real Australian NEM data:
**January, May and August 2024**, all 5 regions (`NSW1`, `QLD1`, `SA1`, `TAS1`, `VIC1`), 5-minute
settlement.

Source: AEMO NEMweb MMSDM archive (see `docs/06_data_governance.md`). Timestamps are **AEMO time
(UTC+10)** and **interval-ending**: `2024-08-05 17:30:00` is the interval (17:25, 17:30]. They are
stored as real `timestamp` columns.

## Reading them

**DuckDB** (queries directly, no load step — this is what we recommend for the SQL/text-to-SQL work):

```python
import duckdb
con = duckdb.connect()                       # in-memory
con.sql("SELECT max(RRP), count(*) FROM 'data/dispatchprice.parquet' WHERE REGIONID='NSW1'")
# or attach for a persistent SQL schema:
con.sql("CREATE VIEW dispatchprice AS SELECT * FROM 'data/dispatchprice.parquet'")
```

**pandas / pyarrow** (native, with predicate pushdown):

```python
import pandas as pd
df = pd.read_parquet("data/dispatchprice.parquet",
                     filters=[("REGIONID", "==", "NSW1")])
```

---

## `dispatchprice.parquet` — actual settled prices (133,920 rows)

One row per (region, 5-min interval). This is the ground-truth price.

| column | type | meaning |
| --- | --- | --- |
| `SETTLEMENTDATE` | timestamp | interval-ending timestamp |
| `REGIONID` | string | `NSW1`/`QLD1`/`SA1`/`TAS1`/`VIC1` |
| `INTERVENTION` | int32 | 0 = normal market. **Always 0 in this sample** — filter on it anyway. |
| `RRP` | double | regional reference price, $/MWh. Can be negative (floor −1000) up to the cap. |
| `APCFLAG` | int32 | administered-pricing condition: 0 = off, >0 = on (a cap applied that interval) |
| `MARKETSUSPENDEDFLAG` | int32 | market suspension flag. **Always 0 in this sample** (2021 suspension predates it). |
| `PRICE_STATUS` | string | AEMO's price-derivation status code |

## `p5min_regionsolution.parquet` — P5MIN forecasts (1,607,040 rows)

The 5-minute-ahead forecast a participant could actually see. `RUN_DATETIME` = when the forecast run
was published (decision time τ); `INTERVAL_DATETIME` = the interval it forecasts. **Only use runs with
`RUN_DATETIME` ≤ the decision time** — later runs leak the future.

| column | type | meaning |
| --- | --- | --- |
| `RUN_DATETIME` | timestamp | when the forecast was published |
| `INTERVAL_DATETIME` | timestamp | the forecast interval (ending) |
| `REGIONID` | string | region |
| `INTERVENTION` | int32 | 0 (only value present) |
| `RRP` | double | forecast price, $/MWh |

> **Note:** the real NEM also has a half-hourly, longer-horizon **predispatch** forecast. It is
> **intentionally excluded from this sample** to keep the data small. All forecast-based work here
> uses **P5MIN** alone. See `docs/04_forecasts.md`.

## `dispatchregionsum.parquet` — demand & supply (133,920 rows)

Per (region, interval). Useful as features / context.

| column | type | meaning |
| --- | --- | --- |
| `SETTLEMENTDATE` | timestamp | interval-ending timestamp |
| `REGIONID` | string | region |
| `INTERVENTION` | int32 | 0 |
| `TOTALDEMAND` | double | regional demand, MW |
| `AVAILABLEGENERATION` | double | available generation, MW |
| `NETINTERCHANGE` | double | net interconnector flow into the region, MW (neg = exporting) |
| `SS_SOLAR_UIGF` | double | semi-scheduled solar unconstrained intermittent generation forecast, MW |
| `SS_WIND_UIGF` | double | semi-scheduled wind UIGF, MW |

## `market_price_thresholds.parquet` — cap & floor history (17 rows)

The market price cap (`VOLL`), floor and administered-price threshold by effective date. Changes each
July. The 2024 cap was **$17,500/MWh**, the floor **−$1,000/MWh**.

| column | type | meaning |
| --- | --- | --- |
| `EFFECTIVEDATE` | timestamp | when this version took effect |
| `VERSIONNO` | int32 | version (bump on re-issue) |
| `VOLL` | double | market price cap, $/MWh |
| `MARKETPRICEFLOOR` | double | market price floor, $/MWh |
| `ADMINISTERED_PRICE_THRESHOLD` | double | threshold above which administered pricing can apply, $/MWh |
| `AUTHORISEDDATE` / `LASTCHANGED` | timestamp | bookkeeping |

---

## Gotchas worth knowing

- **As-of joins.** Forecasts are versioned by run. Joining a price to "the forecast" without clipping
  to `RUN_DATETIME` ≤ interval time leaks the future and will flatter every model.
- **Prices are RAW** (AEMO's published RRP), *not* mapped onto today's cap. 2024's cap was $17,500;
  today's is $23,200. `docs/05_price_caps_normalisation.md` explains why that matters.
- **Negative prices are real** — South Australia and Victoria regularly go below zero midday. A battery
  that can charge gets *paid to charge*.
- **Round-trip losses.** A real battery loses ~10% each way (see `docs/03_battery_operations.md`), so
  buy and sell prices must differ by more than that to make money.
