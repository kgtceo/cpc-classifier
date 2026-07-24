"""Deterministic eval metrics for cpc-classifier."""

from __future__ import annotations

from cpc_classifier.models import ClassificationResult


def selected_symbols(result: ClassificationResult) -> set[str]:
    return {c.symbol for c in result.candidates}


def top1_correct(result: ClassificationResult, expected_symbols: set[str]) -> bool:
    """The single highest-confidence pick is one of the expected classes."""
    if not result.candidates:
        return False
    best = max(result.candidates, key=lambda c: c.confidence)
    return best.symbol in expected_symbols


def recall_at_k(result: ClassificationResult, expected_symbols: set[str]) -> float:
    """Fraction of expected classes present among the selected candidates."""
    if not expected_symbols:
        return 1.0
    return len(selected_symbols(result) & expected_symbols) / len(expected_symbols)


def no_hallucinated_symbols(result: ClassificationResult, subset_symbols: set[str]) -> bool:
    """Every selected symbol exists in the bundled subset (the core safety guarantee)."""
    return selected_symbols(result) <= subset_symbols
