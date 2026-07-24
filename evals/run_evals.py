"""Run the cpc-classifier eval suite (needs ANTHROPIC + VOYAGE keys).

Gates:
  • TOP-1        — the top pick is one of the expected classes (for classifiable inventions).
  • RECALL@k     — expected classes appear among the selections.
  • ABSTENTION   — inventions with no fitting CPC class are abstained.
  • NO-HALLUCINATED-SYMBOL — every selected symbol exists in the bundled subset (core safety guarantee).

    python evals/run_evals.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cpc_classifier.classes import ClassIndex, load_classes
from cpc_classifier.classifier import Classifier
from cpc_classifier.client import LLMClient
from cpc_classifier.config import Settings
from cpc_classifier.embedder import VoyageEmbedder

from metrics import no_hallucinated_symbols, recall_at_k, selected_symbols, top1_correct  # noqa: E402

DATASET = Path(__file__).parent / "dataset" / "cases.json"


def main() -> int:
    settings = Settings.from_env()
    classes = load_classes()
    subset_symbols = {c.symbol for c in classes}
    index = ClassIndex(classes, VoyageEmbedder(model=settings.embed_model))
    classifier = Classifier(index, LLMClient(settings), settings)
    cases = json.loads(DATASET.read_text())

    failures: list[str] = []
    top1_hits = 0
    classifiable = 0
    for case in cases:
        result = classifier.classify(case["invention"])
        expected = set(case["expected_symbols"])
        print(f"\n=== {case['invention'][:55]} ===")
        print(f"  abstained={result.abstained} selected={sorted(selected_symbols(result))} expected={sorted(expected)}")

        if not no_hallucinated_symbols(result, subset_symbols):
            failures.append(f"{case['invention'][:35]}: selected a symbol not in the subset (HALLUCINATION)")

        if case["expect_abstain"]:
            if not result.abstained:
                failures.append(f"{case['invention'][:35]}: expected abstention, classified anyway")
        else:
            classifiable += 1
            if top1_correct(result, expected):
                top1_hits += 1
            else:
                failures.append(f"{case['invention'][:35]}: top-1 not in expected {sorted(expected)}")
            rec = recall_at_k(result, expected)
            print(f"  RECALL@k={rec:.2f}")
            if rec < 0.5:
                failures.append(f"{case['invention'][:35]}: low recall ({rec:.2f})")

    if classifiable:
        print(f"\n=== TOP-1 accuracy: {top1_hits}/{classifiable} ===")

    print("\n" + "=" * 40)
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("ALL GATES PASSED ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
