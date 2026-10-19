# Track 1 — architecture / design doc (fill this in)

> Copy this into your submission as `DESIGN.md` and fill it in. We grade this **before** the code.
> A crisp doc a colleague could build from beats a long, vague one. Don't paste AI output you can't
> defend — you'll be asked to explain it live.

## 1. Architecture (diagram or clear prose)

The moving parts: UI → runtime/agent → tools → sources. Name the specific CopilotKit pieces you used.

```
Your answer:
```

## 2. The two tools

**SQL tool** — what engine, how it reads the data, and how you keep it read-only:

**Retrieval tool** — how you retrieve from `docs/` (search method, any chunking). **Review the corpus
first** (~3,000 words, 6 short docs): does it need enrichment — chunking, metadata, heading
structure — or is it fine as-is? Justify the choice:

```
Your answer:
```

## 3. How you keep answers grounded (the hard part)

How do you stop the model from stating a number it didn't compute? What forces it to run a query, and
what forces a rule-answer to cite a doc?

```
Your answer:
```

## 4. As-of honesty

Forecasts in this data are versioned by run time. How does your agent avoid leaking the future when it
answers a forecast-related question?

```
Your answer:
```

## 5. Evaluation plan

How would you measure whether this thing is actually trustworthy? (A labelled question set? Citation
precision? A "can't-answer" set?) Even a sketch is fine.

```
Your answer:
```

## 6. Failure modes

Name the **weakest** kind of question your system will answer badly, and why.

```
Your answer:
```

## 7. Run it

Exact commands to install, set the key, and start:

```
Your answer:
```
