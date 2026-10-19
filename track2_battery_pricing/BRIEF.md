# Track 2 — Battery charge and discharge pricing (data science)

## Task

Build a **pricing model**. For each 5-minute interval, the model estimates the **value of stored
energy**. It produces a **charge price** and a **discharge price** for the battery: the price at
which you agree to charge, and the price at which you agree to discharge.

Then **backtest** the model: run it against the data and show how much it earns compared to a simple
baseline.

This model is the core of the trading system of a merchant battery. The important question is not
"buy low, sell high". The important question is: **what is one unit of stored energy worth now** —
given round-trip losses, degradation, and an uncertain future price path?

## Framing (you can deviate — but justify it)

- **Battery:** 1 MW / 2 MW·h, 90% charge efficiency, 90% discharge efficiency (81% round-trip), SOC
  5–95%, start at 50%, wear cost **$30/MW·h** of throughput. See `docs/03_battery_operations.md`.
- **Output for each interval:** a `charge_price` and a `discharge_price` (in $/MWh). A natural
  strategy charges when the price is less than or equal to `charge_price`, and discharges when the
  price is greater than or equal to `discharge_price`. You can output a different quantity if you
  can defend it.
- **The value of stored energy** is an opportunity value. It comes from the **forecast**, not from
  the current spot price (`docs/04_forecasts.md`). Use P5MIN (`p5min_regionsolution`), **as-of**
  only. NOTE: this sample contains P5MIN only. Predispatch is not included.

## Minimum viable product (mandatory in the 2 hours)

1. **A model** that emits `charge_price` and `discharge_price` for each (region, interval). Any
   method is acceptable: forecast blend (similar to TWAP), a learned regressor, a small
   optimisation. You must be able to defend the method.
2. **An as-of backtest** for **at least one full month** of the sample. We recommend August — it
   contains the price spikes. Simulate SOC, round-trip losses, and wear. Report the **net value
   after wear**.
3. **A baseline comparison.** Compare against TWAP (`docs/03`; exact thresholds in
   `grader/simulate.py`). Derive the break-even spread yourself from the specification in
   `docs/03`. If your model does not earn more than TWAP, explain why. An honest, well-argued
   negative result is acceptable.
4. **A short report** (`FINDINGS.md`): the approach, one chart (price, dispatch, and SOC), the
   headline number, and **the most important way the result could fool itself**.

## The reference simulator

`grader/simulate.py` simulates the battery against a dispatch schedule. It reports the value after
wear. You can use it, or you can write your own simulator. If you write your own, be careful with
SOC, efficiency, and the straight-line dispatch trajectory (`docs/03`).

```
python grader/simulate.py --help
```

## Optional items (only if the minimum viable product works)

- Cross-region comparison: which region is the most battery-friendly in the sample?
- Spike-day case study (5 Aug 2024, NSW): did your model discharge into the spike?
- Uncertainty: a confidence-aware price band that widens when forecasts disagree.
- Ablation: how much of the value comes from P5MIN forecasts, and how much from recent spot
  momentum?

## Mandatory requirements (we check these)

- **No lookahead.** Forecasts must be **as-of** the decision time (`RUN_DATETIME`/`LASTCHANGED` ≤
  τ). This is the most common failure. If your model looks at the future, the result is void. Show
  your vintage selection in the code.
- **Include losses and wear.** A gross-spread number that ignores the 81% round-trip efficiency and
  the $30/MW·h wear is not a result.
- **Honest baseline.** Compare against TWAP. Read the exact thresholds in `grader/simulate.py`
  (`twap_schedule`). Do not invent a weaker baseline.

## Agentic thinking (mandatory)

Show your agentic thinking while you code the solution. Keep a short log: `AGENT_LOG.md`. For each
major task, record:

- the instruction that you gave to the agent,
- what the agent produced,
- how you verified the result (tests, queries, manual checks),
- what you corrected or rejected.

Also record how you decomposed the problem into tasks that are small enough for an agent. One page
is sufficient. We will ask about your log in the demo.

## Deliverables

1. **Findings doc** — start from `DESIGN_TEMPLATE.md` and submit it as `FINDINGS.md`: the approach,
   the number, the honest caveat. **We grade this first.**
2. **Code** — the model and the backtest, runnable.
3. **Live demo** — 15 minutes: the chart, the headline number, and one thing you would do with
   another day.

## Resources

- `data/SCHEMA.md` — the tables.
- `docs/01, 03, 04, 05` — market, battery economics, forecasts, normalisation.
- `grader/simulate.py` — the reference simulator.
