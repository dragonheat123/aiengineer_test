# AI Engineer Take-Home Test — Battery Storage Market Data

**Duration:** 1 day · **Format:** remote or onsite · **Schedule:** the data and briefs are
distributed at the start; a 15-minute live demo follows at the end.

You are given three months of real Australian National Electricity Market (NEM) data and a set of
internal policy documents, and asked to build something useful on top of them. **Choose one of the
two tracks.**

| Track | Question it tests |
| --- | --- |
| **Track 1 — QnA frontend (CopilotKit)** | Can you build a trustworthy conversational interface over structured market data and unstructured policy documents? |
| **Track 2 — Battery charge/discharge pricing (data science)** | Can you turn raw prices and forecasts into a defensible marginal price for every unit of battery energy? |

Read `data/SCHEMA.md` for the database schema and `docs/` for the policy corpus (Track 1's retrieval
source).

## What you get

```
ai_engineer_test/
├── README.md                  ← this file
├── data/                      ← 3 months of AEMO NEM data as Parquet (~10 MB): Jan, May, Aug 2024
│   ├── dispatchprice.parquet          ← actual 5-min prices
│   ├── p5min_regionsolution.parquet   ← P5MIN forecasts
│   ├── dispatchregionsum.parquet      ← demand & supply
│   ├── market_price_thresholds.parquet← cap/floor history
│   └── SCHEMA.md              ← file & column documentation
├── docs/                      ← internal policy corpus — Track 1's retrieval source (Markdown)
│   ├── 01_market_overview.md
│   ├── 02_bidding_rules.md
│   ├── 03_battery_operations.md
│   ├── 04_forecasts.md
│   ├── 05_price_caps_normalisation.md
│   └── 06_data_governance.md
├── track1_qna_copilotkit/
│   ├── BRIEF.md               ← Track 1 task
│   ├── DESIGN_TEMPLATE.md     ← complete this as your design doc
│   └── RUBRIC.md              ← how Track 1 is graded (shared in full — no hidden criteria)
├── track2_battery_pricing/
│   ├── BRIEF.md               ← Track 2 task
│   ├── DESIGN_TEMPLATE.md     ← complete this as your design doc
│   └── RUBRIC.md              ← how Track 2 is graded
└── grader/
    └── simulate.py            ← Track 2: backtest a dispatch schedule against the data
```

## Ground rules

- **Grading** We grade the design doc first (see the rubrics),
  so an incomplete submission with a clear design doc scores better than a rushed, finished one.
- **AI coding assistants are allowed and encouraged** — You are responsible for everything they produce;
  be prepared to explain any line of it. Both briefs also require a short `AGENT_LOG.md`: a record of how you worked with the agents.
- **Internet use:** you may install packages and read public documentation. You may **not** download
  other electricity datasets — everything needed for the analysis is in `data/*.parquet`.
- **LLM API keys:** you must bring your own (any provider). Track 1 requires one. Never commit keys
  to the repository; use environment variables.
- **Deliverables** (details in each brief): (1) a short **design doc** — complete the
  `DESIGN_TEMPLATE.md` for your track; (2) **code**; (3) a **live demo**. Submit as a git repository
  or a zip archive.

## Suggested time budget (both tracks)

| Minutes | Activity |
| --- | --- |
| 0–15 | Read the brief, schema, and policy docs; explore the data |
| 15–45 | Design doc: architecture, data model, approach, evaluation plan |
| 45–105 | Build |
| 105–120 | Smoke-test, write run instructions, prepare the demo |

## Live demo 
A 15-minute walkthrough: run your solution and answer 2–3 questions we choose (Track 1), or walk us
through your findings and one chart (Track 2); then explain your design doc and describe one thing
you would do with another day.
