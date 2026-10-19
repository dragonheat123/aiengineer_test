# 01 — Market overview: the NEM in five minutes

**Audience:** everyone · **Owner:** Market Operations · **Last reviewed:** 2024-09-02

## What we participate in

We operate grid-scale batteries in Australia's **National Electricity Market (NEM)**, the wholesale
electricity market covering the eastern seaboard. Electricity is traded in **5-minute intervals** and
settled at a **regional reference price (RRP)** — the price of energy in that region for that interval,
in **$/MWh**.

## The five regions

| Region id | Name | Notes |
| --- | --- | --- |
| `QLD1` | Queensland | coal-heavy, net exporter |
| `NSW1` | New South Wales | largest demand, frequent evening spikes |
| `VIC1` | Victoria | coal retiring fast, growing solar |
| `SA1` | South Australia | highest renewable penetration, most negative prices |
| `TAS1` | Tasmania | hydro, via Basslink |

Prices in one region spill into neighbours through interconnectors, but each region clears its own
RRP. Our positions are **price-taker**: a 1 MW battery never moves the regional price.

## Time

- All timestamps are **AEMO time (UTC+10)** and **interval-ending**.
- A **trading day** runs from the interval ending **04:05** to the interval ending **04:00** the next
  day. This is *not* a calendar day — anything that buckets by day must use the trading-day boundary,
  or morning off-peak gets split across two days.
- Calendar months are used for reporting and performance periods.

## Price bounds

The **market price cap** and **market price floor** are set by AEMO and change each 1 July. In 2024
the cap was **$17,500/MWh** and the floor **−$1,000/MWh**. Prices can and do go **negative**: in high
solar periods SA1 and VIC1 routinely clear below zero, and you can be *paid to charge* a battery.

Two special conditions appear in the data as flags on `dispatchprice`:

- **Administered pricing** (`APCFLAG` > 0): AEMO caps the price administratively when a generator is
  behaving badly. Our risk systems treat these intervals as non-tradeable for backtesting purposes.
- **Market suspension** (`MARKETSUSPENDEDFLAG` = 1): a temporary wholesale price cap during a
  system emergency. The June 2021 suspension is the canonical example; it predates this data sample,
  so the flag is always 0 here.

## What we hold

Each of our units is a **1 MW / 2 MW·h** battery (see `03_battery_operations.md`). We bid energy only
— no FCAS in this dataset. Every 5 minutes the unit submits a bid for the next interval; the market
clears it and we settle at the RRP.
