"""Build the candidate data files from the pulled AEMO DuckDB.

Writes one zstd-compressed Parquet file per table into data/ (~10 MB total, vs
~210 MB as SQLite). Timestamps become real timestamp columns.

DuckDB queries these directly with SQL — no load step:
    con = duckdb.connect()                      # in-memory
    con.sql("SELECT * FROM 'data/dispatchprice.parquet' WHERE REGIONID='NSW1'")

pandas also reads them natively:
    pd.read_parquet("data/dispatchprice.parquet")

Run from the storage_optimization_benchmark directory after scripts/pull_data.py:
    python ../ai_engineer_test/build_data.py

Prices are kept RAW (AEMO's published RRP, unmapped) — see docs/05.
"""

import os
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
DUCK = HERE.parent / "storage_optimization_benchmark" / "data" / "benchmark.duckdb"
OUT = HERE / "data"

# predispatchprice is intentionally excluded to keep the sample small; the
# forecast-based work (both tracks) runs on P5MIN alone. Add it back if needed.
# Each entry: (table, ORDER BY clause for better compression + query locality).
TABLES = [
    ("dispatchprice", "REGIONID, SETTLEMENTDATE"),
    ("p5min_regionsolution", "REGIONID, RUN_DATETIME, INTERVAL_DATETIME"),
    ("dispatchregionsum", "REGIONID, SETTLEMENTDATE"),
    ("market_price_thresholds", "EFFECTIVEDATE, VERSIONNO"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCK), read_only=True)
    total = 0
    for table, order in TABLES:
        path = OUT / f"{table}.parquet"
        con.sql(
            f"COPY (SELECT * FROM {table} ORDER BY {order}) "
            f"TO '{os.path.abspath(path)}' (FORMAT parquet, COMPRESSION zstd)"
        )
        sz = path.stat().st_size / 1e6
        total += sz
        n = con.sql(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"{table:26s} {n:>10,} rows  {sz:7.1f} MB", flush=True)
    con.close()
    print(f"{'TOTAL':26s} {'':>10s}    {total:7.1f} MB")


if __name__ == "__main__":
    main()
