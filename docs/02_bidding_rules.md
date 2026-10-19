# 02 — Bidding rules: AEMO's bidirectional unit (BDU) format

**Audience:** trading & engineering · **Owner:** Market Operations · **Last reviewed:** 2024-09-02

Every 5 minutes, ahead of each interval, our unit submits an **energy bid** for a **bidirectional
unit (BDU)**. This is our internal reference for the format and the validation rules our gateway
enforces. It is not legal advice — AEMO's NER and the BDU definition govern.

## Structure

A bid has two sides:

- **LOAD side** — the price bands at which we are willing to **charge** (buy).
- **GEN side** — the price bands at which we are willing to **discharge** (sell).

Each side carries:

| Field | Rule |
| --- | --- |
| `prices` | **10** prices, **strictly increasing**, all within `[floor, cap]` |
| `band_mw` | MW offered **at each** band price; each in `[0, power_mw]` |
| `max_avail` | a MW cap on the whole side, in `[0, power_mw]` |
| `ramp_up_rate`, `ramp_down_rate` | MW/min — **must equal the unit's physical ramp rate** |

The band prices for a side are expressed at the **connection point**; AEMO scales by the marginal loss
factor (MLF) to get the regional price. Our sample data uses MLF = 1.0, so connection-point and
regional prices coincide.

## How a bid clears

"Bands accumulate": on the GEN side from band 1 upward, on the LOAD side from band 10 downward, each
capped by `max_avail`. If the actual RRP is at or above a GEN band's price, that band discharges; if
the RRP is at or below a LOAD band's price, that band charges. **Net MW = discharge − charge.**

A dispatched MW target is the value the unit must reach **by the end** of the interval; the unit ramps
in a straight line from its start-of-interval MW, and that trajectory is what settles.

## Validation — a bid is rejected if any of these fail

1. Each side has 10 **strictly increasing** prices, all inside `[floor, cap]`.
2. `band_mw` and `max_avail` are within `[0, power_mw]`.
3. **Convexity:** every effective LOAD band price is **strictly below** every effective GEN band price.
   (A bid can therefore never charge and discharge at once — the market won't accept it.)
4. Stated ramp rates equal the unit's configured rate.

**Consequences of getting it wrong:**
- A **rejected bid dispatches 0 MW** for that interval — a silent money-loser.
- If a bid clears more than the battery can physically deliver or absorb, the simulator clips it and
  flags **non-conformance**. Real-world, this is an AEMO non-conformance event and a fine.
- Any rejected bid, non-conformance, or wrong ramp rate makes a whole run/backtest **invalid**.

> **Policy (house rule):** our gateway always passes a bid through a `conform()` step last — it caps
> each side's `max_avail` so that whatever clears can be delivered and then stopped within the
> state-of-charge limits. Form bids however you like; conform last. Never submit a bid you haven't
> conformed.

## The daily price lock

**Band prices are fixed for the whole trading day.** The first *accepted* bid of a trading day locks
both sides' 10 prices until 04:00 next day. Later bids (rebids) may change **only** `band_mw`,
`max_avail` and ramp rates. A bid that changes a band price mid-day is **rejected**.

> **Policy:** choose the day's band ladder once, carefully, from the morning forecast. Everything
> intraday is MW allocation, never price reshaping. The trading desk's standing ladder lives in the
> config (`load_prices` / `gen_prices`).
