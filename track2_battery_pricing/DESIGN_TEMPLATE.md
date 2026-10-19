# Track 2 — design / findings doc (fill this in)

> Copy this into your submission as `FINDINGS.md` and fill it in. We grade this **before** the code.
> Be concrete. We'd rather see a small, honest, well-argued result than a big unexplained one.
> Don't paste AI output you can't defend — you'll be asked to explain it live.

## 1. Problem framing (3–5 sentences)

In your own words: what is being maximised, and why is "value of stored energy" not the same as "the
current price"? What makes a battery trade profitable that a simple buy-low-sell-high misses?

```
Your answer:
```

## 2. The economics you derived

You were given efficiencies, wear cost, and SOC limits — but **not** the break-even spread. Show your
derivation of the minimum price spread needed for a full cycle to be profitable at flat prices, and
state the number you get.

```
Your derivation + number:
```

## 3. Your method

How does your model produce a `charge_price` / `discharge_price` per interval? What's the value of
stored energy `V` in your approach, and where does it come from?

```
Your answer:
```

## 4. How you avoided lookahead (critical)

Quote the exact code/mechanism that selects which forecast run is visible at decision time τ. Why can
you guarantee it never uses a run published after τ?

```
Your answer (with a code snippet):
```

## 5. Results

- Window tested (must be ≥ 1 full month):
- **Net value after wear:**
- **TWAP baseline on the same window:**
- Did you beat it? If not, why not?

```
Your answer:
```

## 6. The biggest way this could be fooling itself

Name **one** specific way your number is optimistic or wrong. Not a generic disclaimer — the real one.

```
Your answer:
```

## 7. What you'd do with another day

```
Your answer:
```
