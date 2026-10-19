# 03 — Battery operations & the value of stored energy

**Audience:** engineering & trading · **Owner:** Engineering · **Last reviewed:** 2024-09-02

## Unit specification (per 1 MW / 2 MW·h unit)

| Parameter | Value | Notes |
| --- | --- | --- |
| Power | 1.0 MW | symmetric charge/discharge |
| Energy capacity | 2.0 MW·h | 2 h at full power |
| Charge efficiency | 90% | one-way |
| Discharge efficiency | 90% | one-way |
| **Round-trip efficiency** | **81%** | 0.9 × 0.9 |
| SOC window | 5% – 95% | 0.1 – 1.9 MW·h usable band; never a true 0% or 100% |
| Start-of-day SOC | 50% | our operational convention |
| Ramp rate | 1.0 MW/min | full power in 1 minute; not a binding constraint at 5-min resolution |
| Degradation (wear) cost | **$30 / MW·h** | charged on **every** MW·h charged *and* discharged |

The **wear cost is a house accounting number**, not a market price. It's calibrated so that a
lossless-foresight planner averages roughly **one equivalent full cycle per day** — the typical
throughput of a merchant battery in this market. Treat it as the internal shadow price of throughput.

## Charging economics

Every trade moves energy in and out, so it wears twice (once charging, once discharging) and it pays
the round-trip loss on the way. A discharge is only worth doing against the charge that filled the
battery **after** both effects are accounted for. The raw inputs are all in the spec table above — the
spread you need before a full cycle is profitable at flat prices is *derived* from them, not stated
here. Work it out; it's the first thing any pricing model has to get right, and getting it wrong is
the most expensive silent bug in this domain.

This is also why "buy low, sell high" needs a *wide* gap here, and why **negative-price charging
events** (SA1/VIC1 midday) are disproportionately valuable — you're paid to take on energy you can
later sell.

## State of charge as the real asset

A battery's position at time *t* is not its cash — it's its **stored energy**, and that energy is worth
the best price it can be converted into later. The value of stored energy is *not* the current price;
it's the **opportunity value**: the highest net price the unit expects to discharge into, discounted
for round-trip losses and wear.

A correct valuation therefore needs a **forecast**, not a spot price. The higher a forecast price the
unit expects later, the more the energy sitting in the tank is worth now — and symmetrically for
charging.

## The reference baseline: TWAP

We benchmark every strategy against **TWAP** (time-weighted average price). It treats the
time-weighted average of the price forecast as the value of stored energy `V`, and acts to **charge**
when the market is cheap relative to `V` and **discharge** when it's rich relative to `V`, with the
thresholds set wide enough to clear round-trip losses and wear. It is deliberately simple and
forecast-driven.

**The exact TWAP implementation ships in `grader/simulate.py` (`twap_schedule`)** — read it to see the
precise thresholds, and use it as the baseline to beat. It is the yardstick every policy is judged
against; a strategy that can't beat it on as-of forecasts shouldn't be trading.

## Degradation and cycles

Wear is charged per MW·h of throughput, both directions. A "cycle" is ~2 MW·h of throughput (1 in, 1
out). At $30/MW·h, one full cycle costs ~$60. The calibration target of ~1 cycle/day is the operational
norm; policies that thrash the battery (many small cycles) bleed value through wear even when gross
spread looks positive.

> **Policy:** never submit a trade whose expected margin doesn't clear round-trip losses + wear. The
> gateway enforces this as a soft floor, not a hard block — but the P&L review flags repeat offenders.
