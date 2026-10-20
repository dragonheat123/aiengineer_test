# Track 1 — Question-answering interface for market data and policy documents

## Task

Build a **conversational question-answering interface**. A user asks questions in natural language.
The answers must use **both** of these sources:

1. **`data/*.parquet`** — the structured market data. Query it with SQL through DuckDB. See
   `data/SCHEMA.md`.
2. **`docs/`** — the policy corpus (6 Markdown documents).

This is our internal "ask the market anything" tool. A trading analyst types a question and gets an
answer **grounded in the data and the policy**, with the reasoning shown.

## What a good solution does

The primary problem is **trust**. An LLM that gives plausible numbers that it did not compute is
dangerous in this domain. Your agent must:

- **Query the database for numbers.** It must not recall numbers from memory. Example: "What was the
  peak price in NSW in August?" The number must come from a SQL query that the agent runs.
- **Cite the policy documents for rules.** Example: "Can I change bid prices mid-day?" The answer
  must quote or point to `docs/02_bidding_rules.md`.
- **Answer mixed questions** that need both sources. Example: *"Our policy caps spread at $X — did
  the NSW prices on 5 August go above that?"* This needs a database query **and** a policy lookup.
- **Be honest when it cannot answer.** Example: a question about FCAS. The data is energy-only. The
  agent must say so. It must not invent a number.

## Minimum viable product (mandatory in the 2 hours)

1. Any webUI, either via **CopilotKit** chat UI (React): `@copilotkit/react-ui` and `@copilotkit/react-core` or google ADK web.
2. An **agent runtime**: CopilotKit **CoAgents** / LangGraph runtime, or a custom Next.js API route.
   The runtime must have two tools:
   - A **SQL tool** for the Parquet data, through DuckDB, read-only.
   - A **retrieval tool** for `docs/`. The corpus is small: about 3,000 words in 6 short Markdown
     files. **Review the corpus before you choose the tooling.** Embeddings with a vector store,
     keyword/BM25 search, or structured section lookup are all acceptable. Justify your choice in
     the design doc. If you think the corpus needs **enrichment** (chunking, metadata, heading
     structure), describe the enrichment in the design doc. Implementation is optional.
3. **Streaming answers** in the UI, with the **tool calls and sources visible**: show the SQL that
   ran and the document sections that were retrieved.
4. A **runnable README**: how to set the API key, install, and start.

## Optional items (only if the minimum viable product works)

- A **human-in-the-loop** confirmation step before an expensive or wide query.
- **Inline citations**: link the answer text to the document and the heading.
- **Guardrails**: read-only database enforcement, query timeout, row caps, refusal of write
  operations.
- A **structured output** mode. Example: return a chart specification for price-over-time questions.
- **Corpus enrichment**: if your design doc says that the corpus needs better chunking, metadata, or
  structure, implement it here.

## Agentic thinking (mandatory)

Show your agentic thinking while you code the solution. Keep a short log: `AGENT_LOG.md`. For each
major task, record:

- the instruction that you gave to the agent,
- what the agent produced,
- how you verified the result (tests, queries, manual checks),
- what you corrected or rejected.

Also record how you decomposed the problem into tasks that are small enough for an agent. One page
is sufficient. We will ask about your log in the demo.

## Constraints

- Bring your own **LLM API key** (any provider). Use an environment variable. Never commit keys.
- You can install packages and read public documentation. Do **not** download other electricity
  datasets.
- The Parquet files are the only data source. Query them read-only (DuckDB or pandas). Do not modify
  them.
- Use the standard CopilotKit path if possible. If it does not work for you, a plain chat UI over
  your own Next.js API route with the same two tools is an acceptable fallback. Say so in the
  README, and give the reason.

## Deliverables

1. **Design doc** — start from `DESIGN_TEMPLATE.md` and submit it as `DESIGN.md` (maximum 2 pages):
   the system, the two tools, grounding, as-of honesty, and your evaluation plan. **We grade this
   first.**
2. **Code** — the application, runnable.
3. **Live demo** — 15 minutes: run it, answer 2–3 questions that we choose live, then walk through
   the design.

## Sample questions for the live demo

- *"What was the highest price in South Australia in August 2024, and when?"* (database)
- *"What is our rule on changing bid prices during a trading day?"* (policy)
- *"Round-trip efficiency is 81% — how many August intervals in NSW were wide enough to clear
  round-trip losses plus wear?"* (both)
- *"How does the price cap in this data compare to today's?"* (policy + database)
