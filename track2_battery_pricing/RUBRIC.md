# Track 2 — grading rubric (battery pricing data science)

Weights sum to 100. We read the **findings doc first**, then the code, then the demo.
Candidates submit the findings doc by filling in `track2_battery_pricing/DESIGN_TEMPLATE.md`.

## 1. Findings / design doc (40)

| Criterion | Points | What we look for |
| --- | --- | --- |
| Problem framing | 10 | Treats stored energy as an **opportunity value** driven by forecast, not spot. Understands the $/MWh economics (`docs/03`). |
| Method clarity | 10 | We can follow how `charge_price`/`discharge_price` are produced, and why. |
| **Leakage discipline** | 15 | Forecast use is **as-of** (`RUN_DATETIME`/`LASTCHANGED` ≤ τ). This is the #1 failure; getting it right is the biggest single chunk. |
| Honest caveat | 5 | The single biggest way the result could be fooling itself, named plainly. |

## 2. Code & backtest (40)

| Criterion | Points | What we look for |
| --- | --- | --- |
| Physics correct | 10 | SOC limits, **81% round-trip losses**, wear $30/MW·h, straight-line dispatch trajectory. Getting losses/wear wrong invalidates the number. |
| As-of backtest over ≥ 1 month | 15 | Runs August (or similar), simulates SOC over time, no peeking. |
| Honest baseline (TWAP) | 10 | TWAP implemented faithfully (thresholds in `grader/simulate.py`), not a strawman. |
| Agentic workflow | 5 | `AGENT_LOG.md` shows task decomposition, the instructions given to agents, verification of agent output, and corrections. The log matches the code. |

**A number that ignores losses or wear scores ≤ 15 on this section**, however large it is.

## 3. Demo & reasoning (20)

| Criterion | Points | What we look for |
| --- | --- | --- |
| One clear chart | 5 | Price vs dispatch vs SOC, readable, tells a story. |
| Headline + honesty | 10 | The number, the baseline, and what you'd do with another day — argued, not oversold. |
| Explain-the-lines | 5 | Explain your model and one thing you'd change. |

## Automatic green flags (+, capped at +10 overall)

- Beating TWAP on a full month **with** losses + wear, on as-of forecasts.
- Spike-day case study (5 Aug NSW) showing you discharged into it — or a good reason you didn't.
- Cross-region comparison.

## Automatic red flags (–)

- **Lookahead** anywhere in vintage selection → this section is void.
- Gross spread presented as profit.
- Baseline that isn't the TWAP in `grader/simulate.py`.
- Can't explain your own feature engineering.

---

### Demo script (we run this)

1. Show the chart: price, your dispatch, SOC over a week that includes a spike.
2. The headline: **net after wear**, and the TWAP baseline's number on the same window.
3. "Show me the code that picks which forecast run to use at time τ." (leakage check)
4. "What's the biggest way this is fooling itself?"
5. **Agentic workflow:** "Show us one entry in your `AGENT_LOG.md`: the task, what the agent produced, and how you checked it."
