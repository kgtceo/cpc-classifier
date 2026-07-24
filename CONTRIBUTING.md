# Contributing

Thanks for looking! This is an educational demo, but issues and PRs are welcome — the two most useful
contributions are **more eval cases** and **more CPC entries** (wider coverage).

## Run it locally

```bash
pip install -e .
pip install pytest
pytest -q                 # offline (fake embedder) — no API key needed
```

**Requirements:** Python ≥3.10 · Node ≥18 (for the `web/` UI). CI runs `pytest -q` on every push;
keep it green. The full eval (`python evals/run_evals.py`) needs `ANTHROPIC_API_KEY` + `VOYAGE_API_KEY`.

## Add cases / classes (most valuable)

Eval case → `evals/dataset/cases.json`:

```json
{ "invention": "A method for ...", "expected_symbols": ["G06N 3/08"], "expect_abstain": false }
```

CPC entry → `src/cpc_classifier/data/cpc_subset.json`:

```json
{ "symbol": "G06N 3/08", "title": "Learning methods for neural networks" }
```

To grow toward real coverage, derive entries from the official CPC bulk data
([cooperativepatentclassification.org](https://www.cooperativepatentclassification.org)) — the
classifier logic doesn't change, only the data.

## Guidelines

- It's an **illustrative subset**, not the full CPC scheme — keep that framing (not for real prosecution).
- Every returned symbol must exist in the subset (the no-hallucination guarantee) — don't weaken it.
- Keep PRs small and focused; `pytest -q` must stay green.
