# cpc-classifier

### ▶ Live demo: **[cpc-classifier.kareemghazal.com](https://cpc-classifier.kareemghazal.com)**

[![CI](https://github.com/kgtceo/cpc-classifier/actions/workflows/ci.yml/badge.svg)](https://github.com/kgtceo/cpc-classifier/actions/workflows/ci.yml)

> ⚠️ **Illustrative subset — not for real classification or prosecution.** This runs against **50
> illustrative CPC classes**, not the official **~250,000-symbol** CPC scheme; every output is a
> suggestion for a human to confirm.

Paste an invention description and get suggested **CPC (Cooperative Patent Classification)** classes
with the supporting phrase — or an abstention when nothing fits. The model can only pick from
retrieved candidates, so it can't invent a symbol. (First run ~10–20s.)

![cpc-classifier: suggested CPC classes for an invention, each with confidence and the evidence phrase](docs/images/screenshot.png)

**How it works** — input → pipeline → output, with the eval harness that measures it:

![cpc-classifier — architecture and eval harness](docs/images/architecture.png)

> **Demo / educational — not a substitute for a professional classification search.** Uses a small
> **illustrative CPC subset** (not the full CPC scheme). Output is classification *suggestions* for a
> human to confirm. The bundled `cpc_subset.json` is a handful of illustrative classes across common
> CPC areas — it is NOT the official CPC scheme and is not maintained against CPC revisions.

Suggests **CPC classes** for a free-text invention description — built so the LLM **can't hallucinate
a symbol**. Classification symbols are a classic failure mode for LLMs (they'll happily emit a
plausible, wrong symbol), so this tool never lets the model produce one from memory.

How it stays safe:

1. **Retrieval first.** The invention is embedded and matched against the CPC subset — this produces
   a shortlist of **candidate classes** (real symbols + titles).
2. **The LLM only *chooses*.** It's shown the candidates and picks the ones the invention falls
   under, with a confidence and the evidence phrase from the description. It's told it may only use
   the given symbols.
3. **Validation enforces it.** After selection, any symbol that wasn't in the retrieved candidates is
   **dropped** — so even if the model invents one, it can't reach the output. The title is normalised
   back to the canonical subset title.
4. **Abstains** when nothing confidently fits, rather than forcing a weak match.

## Architecture

```
invention ─▶ Voyage embed ─▶ cosine search over CPC subset ─▶ candidate classes
                                                                     │
                                                                     ▼
                                                   LLM selects from candidates only
                                                                     │
                                          validate symbols ⊆ candidates ─▶ ClassificationResult
```

## Quickstart

**Requirements:** Python ≥3.10 (backend) · Node ≥18 (the `web/` UI) · an `ANTHROPIC_API_KEY` and a
`VOYAGE_API_KEY` (embeddings). The offline test suite needs neither.

```bash
pip install -e .
cp .env.example .env   # add ANTHROPIC_API_KEY + VOYAGE_API_KEY

cpc-classifier classify "A wearable sensor that measures blood glucose and streams readings to a phone"
```

## Evals

```bash
python evals/run_evals.py
```

- **Top-1 accuracy** — the highest-confidence pick is a correct class.
- **Recall@k** — expected classes appear among the selections.
- **Abstention** — non-classifiable inputs (e.g. "a recipe for sourdough bread") are refused.
- **No-hallucinated-symbol** — every selected symbol exists in the bundled subset (the core guarantee).

The eval set is **6 labelled cases** (5 classifiable inventions + 1 deliberately non-classifiable, to
test abstention) over the **50-class** illustrative subset — enough to gate the retrieval + selection
+ no-hallucination logic, not a benchmark. Add your own — each eval case and CPC
entry is one JSON object:

```json
// evals/dataset/cases.json
{ "invention": "A method for ...", "expected_symbols": ["G06N 3/08"], "expect_abstain": false }
// src/cpc_classifier/data/cpc_subset.json
{ "symbol": "G06N 3/08", "title": "Learning methods for neural networks" }
```

Extend `cpc_subset.json` to widen coverage, and add cases to test on your real domain.

**Latest run (claude-sonnet-4-6, voyage-3 embeddings):** all gates pass — **TOP-1 accuracy 5/5** and
recall@k **1.00** across the classifiable inventions (automotive→B60W, cryptography→H04L 9/00,
wearable→A61B 5/00…), correct **abstention** on a non-classifiable input, and every selected symbol
exists in the bundled subset (no hallucinated code).

## Tests

```bash
pytest -q   # offline: CPC class index + the anti-hallucination guarantee (fake embedder + client)
```

The key test proves that when the model returns a symbol that wasn't retrieved, the classifier drops it.

## Web

`web/` — a Next.js UI: paste an invention description, get suggested CPC classes with the evidence
phrase, or an honest abstention.

Run it locally in two terminals:

```bash
# terminal 1 — the API
pip install -e .
cp .env.example .env                  # add ANTHROPIC_API_KEY and VOYAGE_API_KEY
python -m uvicorn cpc_classifier.api:app --port 8000

# terminal 2 — the UI
cd web
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev                           # open http://localhost:3000
```

See [DEPLOY.md](./DEPLOY.md) — the FastAPI backend on Railway (via the `Dockerfile`; needs
`ANTHROPIC_API_KEY` + `VOYAGE_API_KEY`) + the Next.js `web/` UI on Vercel, ~5 minutes.

## Limitations (what it does NOT do)

- Classifies only against the **50-class illustrative subset** — a real classification needs the full
  CPC scheme (~250,000 symbols) and a professional search. This is a demonstration of the *method*,
  not a production classifier.
- Quality is bounded by **retrieval**: if the right class isn't in the subset (or isn't retrieved),
  the tool abstains rather than guess — by design, but it means coverage depends on the bundled data.
- Output is a **suggestion for a human to confirm**, not an authoritative classification.

**Extending to the full CPC scheme:** the retrieval + no-hallucination design scales unchanged — only
the data grows. Replace `src/cpc_classifier/data/cpc_subset.json` with entries derived from the
official **Cooperative Patent Classification** bulk data (published by the USPTO/EPO at
[cooperativepatentclassification.org](https://www.cooperativepatentclassification.org)); each entry is
just `{ "symbol": ..., "title": ... }`. Larger sets benefit from batching the Voyage embeddings and
caching the vectors, but the classifier logic doesn't change.

## License

MIT — see [LICENSE](./LICENSE).
