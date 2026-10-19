"""Reference battery simulator for Track 2.

Simulates a 1 MW / 2 MW.h battery clearing a dispatch schedule against actual
prices in `data/*.parquet`, applying round-trip losses, SOC limits and wear,
and reports the net value after wear. Ships with an honest TWAP baseline so you
have something to beat.

Physics (see docs/03_battery_operations.md):
  - A schedule row gives `target_mw`: the MW the unit must REACH by the END of
    the interval (negative = charge, positive = discharge).
  - The unit moves in a straight line from its start-of-interval MW to `target_mw`
    over the 5-minute interval; the energy SETTLED is the area under that line.
  - Charging: grid supplies `charge_mwh`, battery stores `charge_mwh * charge_eff`.
    Discharging: battery withdraws, grid receives `discharge_mwh`; the battery
    gives up `discharge_mwh / discharge_eff`.
  - Wear is charged on every MW.h moved, both directions.
  - SOC is clipped to [5%, 95%]; clipping is reported as a SOC-limit event.

Data lives in Parquet files under data/; this reads them with pandas/pyarrow.

Importable:
    from grader.simulate import load_prices, simulate, twap_schedule

CLI:
    python grader/simulate.py --baseline twap --region NSW1 --start 2024-08-01 --end 2024-09-01
    python grader/simulate.py --schedule mine.csv --region NSW1
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# --- battery spec (docs/03) ---
POWER_MW = 1.0
ENERGY_MWH = 2.0
CHARGE_EFF = 0.9
DISCHARGE_EFF = 0.9
SOC_MIN = 0.05 * ENERGY_MWH   # 0.1 MWh
SOC_MAX = 0.95 * ENERGY_MWH   # 1.9 MWh
SOC_START = 0.50 * ENERGY_MWH
WEAR_PER_MWH = 30.0           # $/MWh of throughput, both directions
DT_HOURS = 5.0 / 60.0


def load_prices(region: str, start: str | None = None, end: str | None = None,
                data_dir: Path | None = None) -> pd.DataFrame:
    """Actual 5-minute prices for one region, INTERVENTION = 0, ascending by time."""
    d = data_dir or DATA
    filters = [("REGIONID", "==", region), ("INTERVENTION", "==", 0)]
    if start:
        filters.append(("SETTLEMENTDATE", ">=", pd.Timestamp(start)))
    if end:
        filters.append(("SETTLEMENTDATE", "<", pd.Timestamp(end)))
    df = pd.read_parquet(d / "dispatchprice.parquet", filters=filters,
                         columns=["SETTLEMENTDATE", "RRP"])
    df = df.rename(columns={"SETTLEMENTDATE": "interval_end", "RRP": "price"})
    df["interval_end"] = pd.to_datetime(df["interval_end"])
    return df.sort_values("interval_end").reset_index(drop=True)


def _settle(mw0: float, mw1: float) -> tuple[float, float]:
    """Grid-side (discharge_mwh, charge_mwh) settled over one interval, moving in a
    straight line from mw0 to mw1. Handles a trajectory that crosses zero."""
    if mw0 == 0 and mw1 == 0:
        return 0.0, 0.0
    if mw0 * mw1 >= 0:  # same direction (or one is zero)
        e = 0.5 * (mw0 + mw1) * DT_HOURS
        return (e, 0.0) if e >= 0 else (0.0, -e)
    # crosses zero: split at the crossing into two triangles (each fully one sign)
    frac = abs(mw0) / abs(mw1 - mw0)
    e1 = 0.5 * mw0 * (frac * DT_HOURS)            # from mw0 to 0
    e2 = 0.5 * mw1 * ((1.0 - frac) * DT_HOURS)    # from 0 to mw1
    discharge = e1 if e1 > 0 else e2 if e2 > 0 else 0.0
    charge = (-e1) if e1 < 0 else (-e2) if e2 < 0 else 0.0
    return discharge, charge


def simulate(prices: pd.DataFrame, schedule: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Run a dispatch schedule against actual prices.

    `schedule` needs columns: interval_end (datetime), target_mw (float, negative=charge).
    Returns (per-interval ledger, summary dict)."""
    df = prices.merge(schedule[["interval_end", "target_mw"]], on="interval_end", how="inner")
    rows, soc, last_mw = [], SOC_START, 0.0
    clipped = 0
    for r in df.itertuples():
        target = max(min(r.target_mw, POWER_MW), -POWER_MW)
        # keep the trajectory inside SOC limits -> adjust the target
        if target < 0:   # charging raises SOC
            room = (SOC_MAX - soc) / (CHARGE_EFF * DT_HOURS)
            target = max(target, -min(POWER_MW, room))
        elif target > 0:  # discharging lowers SOC
            room = (soc - SOC_MIN) * DISCHARGE_EFF / DT_HOURS
            target = min(target, min(POWER_MW, room))
        if abs(target - r.target_mw) > 1e-9:
            clipped += 1
        discharge, charge = _settle(last_mw, target)
        soc += charge * CHARGE_EFF - discharge / DISCHARGE_EFF
        soc = max(min(soc, SOC_MAX), SOC_MIN)
        revenue = discharge * r.price
        cost = charge * r.price
        wear = WEAR_PER_MWH * (discharge + charge)
        rows.append({"interval_end": r.interval_end, "price": r.price, "target_mw": target,
                     "discharge_mwh": discharge, "charge_mwh": charge, "soc_mwh": soc,
                     "revenue": revenue, "cost": cost, "wear": wear,
                     "net": revenue - cost - wear})
        last_mw = target
    led = pd.DataFrame(rows)
    summary = {
        "intervals": len(led),
        "net_after_wear": round(float(led["net"].sum()), 2),
        "gross_revenue": round(float(led["revenue"].sum()), 2),
        "charge_cost": round(float(led["cost"].sum()), 2),
        "wear_cost": round(float(led["wear"].sum()), 2),
        "mwh_discharged": round(float(led["discharge_mwh"].sum()), 4),
        "mwh_charged": round(float(led["charge_mwh"].sum()), 4),
        "equivalent_cycles": round(float((led["discharge_mwh"].sum() + led["charge_mwh"].sum()) / (2 * ENERGY_MWH)), 3),
        "soc_clipped_intervals": clipped,
        "final_soc_mwh": round(float(led["soc_mwh"].iloc[-1]) if len(led) else SOC_START, 4),
    }
    return led, summary


def twap_schedule(region: str, start: str, end: str, data_dir: Path | None = None) -> pd.DataFrame:
    """The reference TWAP baseline (docs/03): value of stored energy V = the
    time-weighted average of the latest as-of P5MIN forecast. Charge full power when
    price <= 0.9*V - wear; discharge when price >= V/0.9 + wear; SOC-aware. As-of by
    construction (never looks ahead).

    Note: the full benchmark blends P5MIN with the half-hourly predispatch run for a
    longer horizon. This sample ships P5MIN only (predispatch was dropped to keep the
    data small), so V here is the mean of the ~1 h of P5MIN intervals ahead of tau."""
    d = data_dir or DATA
    prices = load_prices(region, start, end, data_dir)
    p5 = pd.read_parquet(
        d / "p5min_regionsolution.parquet",
        filters=[("REGIONID", "==", region), ("INTERVENTION", "==", 0)],
        columns=["RUN_DATETIME", "INTERVAL_DATETIME", "RRP"])
    p5["RUN_DATETIME"] = pd.to_datetime(p5["RUN_DATETIME"])
    p5["INTERVAL_DATETIME"] = pd.to_datetime(p5["INTERVAL_DATETIME"])
    price_at = dict(zip(prices["interval_end"], prices["price"]))

    targets = []
    for tau in prices["interval_end"]:
        # latest forecast run published at or before tau (the as-of rule, docs/04)
        run = p5[p5["RUN_DATETIME"] <= tau]
        if run.empty:
            targets.append(0.0); continue
        last_run = run["RUN_DATETIME"].max()
        fut = run[(run["RUN_DATETIME"] == last_run) & (run["INTERVAL_DATETIME"] > tau)]
        if fut.empty:
            targets.append(0.0); continue
        # P5MIN steps are uniform 5-min, so the time-weighted mean is the simple mean
        V = float(fut["RRP"].mean())
        price = float(price_at[tau])
        if price <= 0.9 * V - WEAR_PER_MWH:
            targets.append(-POWER_MW)
        elif price >= V / 0.9 + WEAR_PER_MWH:
            targets.append(POWER_MW)
        else:
            targets.append(0.0)
    out = prices[["interval_end"]].copy()
    out["target_mw"] = targets
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Backtest a battery dispatch schedule against NEM prices.")
    ap.add_argument("--schedule", type=Path, help="CSV with columns interval_end,target_mw")
    ap.add_argument("--baseline", choices=["twap"], help="generate and score the TWAP baseline")
    ap.add_argument("--region", default="NSW1")
    ap.add_argument("--start", default="2024-08-01")
    ap.add_argument("--end", default="2024-09-01")
    ap.add_argument("--out", type=Path, help="write the per-interval ledger CSV here")
    a = ap.parse_args()

    prices = load_prices(a.region, a.start, a.end)
    if a.schedule:
        sched = pd.read_csv(a.schedule)
        sched["interval_end"] = pd.to_datetime(sched["interval_end"])
    elif a.baseline == "twap":
        print("Generating TWAP baseline (as-of P5MIN)...")
        sched = twap_schedule(a.region, a.start, a.end)
    else:
        ap.error("pass --schedule FILE or --baseline twap")

    led, summary = simulate(prices, sched)
    print(f"\n=== {a.region}  {a.start} -> {a.end} ===")
    for k, v in summary.items():
        print(f"  {k:22s} {v}")
    if a.out:
        led.to_csv(a.out, index=False)
        print(f"\nLedger written to {a.out}")


if __name__ == "__main__":
    main()
