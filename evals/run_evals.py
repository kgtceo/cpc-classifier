"""Run the cpc-classifier eval suite (needs ANTHROPIC + VOYAGE keys).

Gates:
  • TOP-1        — the top pick is one of the expected classes (for classifiable inventions).
  • RECALL@k     — expected classes appear among the selections.
  • ABSTENTION   — inventions with no fitting CPC class are abstained.
  • NO-HALLUCINATED-SYMBOL — every selected symbol exists in the bundled subset (core safety guarantee).
  • EVIDENCE-GROUNDED      — every surviving evidence_span is a verbatim substring of the invention
                             (enforced in the classifier; re-verified here independently).

Every run writes a reproducible artifact to evals/results/latest.json (metrics, per-case
outcomes, models used, timestamp) — the numbers quoted in the README come from that file.

    python evals/run_evals.py            # deterministic gates
    python evals/run_evals.py --judge    # + opus LLM-as-judge on every case
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from cpc_classifier.classes import ClassIndex, load_classes
from cpc_classifier.classifier import Classifier
from cpc_classifier.client import LLMClient
from cpc_classifier.config import Settings
from cpc_classifier.embedder import VoyageEmbedder

from judge import judge_case  # noqa: E402
from metrics import no_hallucinated_symbols, recall_at_k, selected_symbols, top1_correct  # noqa: E402

DATASET = Path(__file__).parent / "dataset" / "cases.json"
RESULTS = Path(__file__).parent / "results" / "latest.json"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def evidence_grounded(result) -> bool:
    """Independent re-check of the classifier's evidence guarantee."""
    inv = _norm(result.invention)
    return all(_norm(c.evidence_span) and _norm(c.evidence_span) in inv for c in result.candidates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", action="store_true", help="also grade every case with the opus judge")
    args = parser.parse_args()

    settings = Settings.from_env()
    classes = load_classes()
    subset_symbols = {c.symbol for c in classes}
    index = ClassIndex(classes, VoyageEmbedder(model=settings.embed_model))
    client = LLMClient(settings)
    classifier = Classifier(index, client, settings)
    cases = json.loads(DATASET.read_text())

    failures: list[str] = []
    per_case: list[dict] = []
    top1_hits = 0
    classifiable = 0
    recalls: list[float] = []
    judge_passes = 0
    judged = 0

    for case in cases:
        result = classifier.classify(case["invention"])
        expected = set(case["expected_symbols"])
        label = case.get("source") or case["invention"][:55]
        print(f"\n=== {label} ===")
        print(f"  abstained={result.abstained} selected={sorted(selected_symbols(result))} expected={sorted(expected)}")

        record: dict = {
            "invention": case["invention"][:80],
            "source": case.get("source"),
            "expected": sorted(expected),
            "selected": sorted(selected_symbols(result)),
            "abstained": result.abstained,
        }

        if not no_hallucinated_symbols(result, subset_symbols):
            failures.append(f"{label[:40]}: selected a symbol not in the subset (HALLUCINATION)")
        if not evidence_grounded(result):
            failures.append(f"{label[:40]}: evidence_span not verbatim in the invention (UNGROUNDED)")

        if case["expect_abstain"]:
            record["abstention_correct"] = result.abstained
            if not result.abstained:
                failures.append(f"{label[:40]}: expected abstention, classified anyway")
        else:
            classifiable += 1
            t1 = top1_correct(result, expected)
            rec = recall_at_k(result, expected)
            recalls.append(rec)
            record["top1_correct"] = t1
            record["recall_at_k"] = round(rec, 3)
            if t1:
                top1_hits += 1
            else:
                failures.append(f"{label[:40]}: top-1 not in expected {sorted(expected)}")
            print(f"  RECALL@k={rec:.2f}")
            if rec < 0.5:
                failures.append(f"{label[:40]}: low recall ({rec:.2f})")

        if args.judge:
            verdict = judge_case(client, settings, result)
            judged += 1
            record["judge"] = verdict.model_dump()
            if verdict.passed:
                judge_passes += 1
            else:
                failures.append(f"{label[:40]}: judge failed — {verdict.comment}")
            print(f"  JUDGE: sound={verdict.selection_sound} evidence={verdict.evidence_supports} "
                  f"no_overclaim={verdict.no_overclaim} — {verdict.comment}")

        per_case.append(record)

    if classifiable:
        print(f"\n=== TOP-1 accuracy: {top1_hits}/{classifiable} ===")
    if judged:
        print(f"=== JUDGE: {judge_passes}/{judged} cases passed all three dimensions ===")

    artifact = {
        "run": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model": settings.answer_model,
            "embed_model": settings.embed_model,
            "judge_model": settings.judge_model if args.judge else None,
            "dataset_size": len(cases),
            "subset_size": len(classes),
        },
        "metrics": {
            "top1": f"{top1_hits}/{classifiable}",
            "top1_rate": round(top1_hits / classifiable, 3) if classifiable else None,
            "recall_at_k_avg": round(sum(recalls) / len(recalls), 3) if recalls else None,
            "judge_pass": f"{judge_passes}/{judged}" if judged else None,
            "all_gates_passed": not failures,
        },
        "failures": failures,
        "per_case": per_case,
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"\nWrote {RESULTS.relative_to(Path(__file__).parent.parent)}")

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
