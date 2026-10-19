# Track 1 — grading rubric (CopilotKit QnA)

Weights sum to 100. We read the **design doc first**, then the code, then the demo.
Candidates submit the design doc by filling in `track1_qna_copilotkit/DESIGN_TEMPLATE.md`.

## 1. Design doc (40)

| Criterion | Points | What we look for |
| --- | --- | --- |
| Architecture clarity | 15 | Can we see the moving parts — UI → runtime/agent → {SQL tool, retrieval tool} → sources? A diagram or clear prose. |
| Grounding & trust strategy | 15 | Explicitly how numbers come from SQL (not parametric memory) and rules come from `docs/`. How you stop hallucinated figures. Retrieval approach justified against the actual corpus — did you review it before choosing tooling? |
| As-of / honesty | 5 | Awareness that forecasts are versioned (`docs/04`), and how the agent avoids leaking the future when it queries forecasts. |
| Evaluation plan | 5 | How you'd measure answer quality (a labelled question set, citation precision, a "can't-answer" set). Even a sketch scores. |

**Not required to be long — ≤ 2 pages.** A crisp doc that a colleague could build from beats a rambling one.

## 2. Code (40)

| Criterion | Points | What we look for |
| --- | --- | --- |
| CopilotKit integration done properly | 10 | Real `@copilotkit/react-ui` + a runtime (CoAgents/LangGraph or a custom route). Not a hand-rolled chat box labelled "CopilotKit". |
| Two tools, wired for grounding | 15 | A **read-only** SQL tool + a retrieval tool over `docs/`, actually invoked by the agent, results fed back into the answer. |
| Honesty & guardrails | 10 | Read-only DB, refuses writes; reasonable query shaping/timeout/row caps; sources shown; graceful when it can't answer. |
| Agentic workflow | 5 | `AGENT_LOG.md` shows task decomposition, the instructions given to agents, verification of agent output, and corrections. The log matches the code. |

**Runnable** is a pass/fail gate on this section: if we can't start it from the README in the demo, cap
this at 20.

## 3. Demo & reasoning (20)

| Criterion | Points | What we look for |
| --- | --- | --- |
| Live answers correct & grounded | 10 | The 2–3 questions we pick (mix of DB / policy / both) come back right, with the SQL and sources visible. |
| Explain-the-lines | 5 | Can you explain any line of your code and one design decision? You own what the AI wrote. |
| Failure awareness | 5 | Name the weakest answer your system gives and why. |

## Automatic green flags (+, capped at +10 overall)

- Inline citations that resolve to a real doc heading.
- A labelled eval set committed in the repo.
- Human-in-the-loop confirmation before wide queries.

## Automatic red flags (–)

- Numbers in answers that didn't come from a query (we ask "show me the SQL for that number").
- API key committed to the repo.
- A generic "chat with docs" template with the DB tool bolted on but never exercised.

---

### Demo script (we run this)

1. Start it from your README. If it needs an env var, say which.
2. **DB question:** "Highest SA1 price in August 2024, and when?"
3. **Policy question:** "Can we change bid prices mid-trading day?"
4. **Both:** "On 5 Aug 2024 NSW, how long was the price above $10,000, and does our wear policy make
   discharging into it worth it?"
5. **Can't-answer:** "What's our FCAS revenue?" — the right answer is "the data is energy-only."
6. **Agentic workflow:** "Show us one entry in your `AGENT_LOG.md`: the task, what the agent produced, and how you checked it."
