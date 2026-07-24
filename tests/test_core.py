"""Offline tests: CPC class index, retrieval plumbing, and the anti-hallucination guarantee."""

from __future__ import annotations

from conftest import FakeClassifierClient

from cpc_classifier.classes import ClassIndex, load_classes
from cpc_classifier.classifier import Classifier
from cpc_classifier.embedder import FakeEmbedder
from cpc_classifier.models import Classification, CpcCandidate


def _index() -> ClassIndex:
    return ClassIndex(load_classes(), FakeEmbedder())


def test_subset_loads():
    classes = load_classes()
    assert len(classes) >= 20
    assert all(c.symbol and c.title for c in classes)


def test_index_search_returns_k():
    idx = _index()
    hits = idx.search("neural network trained on device", k=5)
    assert len(hits) == 5  # plumbing works (FakeEmbedder isn't semantic)


def test_hallucinated_symbol_is_dropped(settings):
    """The model 'returns' a symbol that wasn't retrieved → classifier must drop it."""
    idx = _index()
    # use the SAME invention string for the retrieval check and classify()
    # (FakeEmbedder isn't semantic, so retrieval must be pinned to identical input text)
    invention = "some invention"
    retrieved_symbols = [r.cpc_class.symbol for r in idx.search(invention, settings.top_k)]
    bogus = "Z99Z 99/99"
    assert bogus not in retrieved_symbols
    client = FakeClassifierClient(Classification(
        candidates=[
            CpcCandidate(symbol=bogus, title="Made up", confidence=0.9, evidence_span="x"),
            CpcCandidate(symbol=retrieved_symbols[0], title="whatever", confidence=0.8, evidence_span="x"),
        ],
        abstained=False,
    ))
    result = Classifier(idx, client, settings).classify(invention)
    symbols = {c.symbol for c in result.candidates}
    assert bogus not in symbols                       # hallucinated symbol dropped
    assert retrieved_symbols[0] in symbols            # legit symbol kept
    assert all(c.symbol in retrieved_symbols for c in result.candidates)


def test_title_is_normalised_to_canonical(settings):
    """Even if the model rewrites the title, we restore the canonical subset title."""
    idx = _index()
    invention = "an invention"  # same string for retrieval check and classify()
    r0 = idx.search(invention, settings.top_k)[0].cpc_class
    client = FakeClassifierClient(Classification(
        candidates=[CpcCandidate(symbol=r0.symbol, title="MODEL REWROTE THIS", confidence=0.9, evidence_span="x")],
        abstained=False,
    ))
    result = Classifier(idx, client, settings).classify(invention)
    assert result.candidates[0].title == r0.title


def test_abstain_when_model_returns_nothing(settings):
    idx = _index()
    client = FakeClassifierClient(Classification(candidates=[], abstained=True))
    result = Classifier(idx, client, settings).classify("a recipe for chocolate cake")
    assert result.abstained is True
    assert result.candidates == []
