"""Load the bundled illustrative CPC subset + a tiny in-memory class index.

The index embeds each class's symbol+title once; retrieval is cosine similarity (a single
matrix-vector dot product, both sides L2-normalised). Deliberately transparent — swap for a
real CPC search service when you outgrow a demo subset.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .embedder import Embedder
from .models import CpcClass, RetrievedClass

_SUBSET = Path(__file__).parent / "data" / "cpc_subset.json"


def load_classes() -> list[CpcClass]:
    data = json.loads(_SUBSET.read_text(encoding="utf-8"))
    return [CpcClass.model_validate(c) for c in data]


class ClassIndex:
    def __init__(self, classes: list[CpcClass], embedder: Embedder) -> None:
        self._classes = classes
        self._embedder = embedder
        self._matrix: np.ndarray | None = None
        if classes:
            self._matrix = embedder.embed([c.index_text() for c in classes], is_query=False)

    @property
    def symbols(self) -> set[str]:
        return {c.symbol for c in self._classes}

    def search(self, invention: str, k: int) -> list[RetrievedClass]:
        if self._matrix is None or not self._classes:
            return []
        qv = self._embedder.embed([invention], is_query=True)[0]
        scores = self._matrix @ qv.reshape(-1)
        top = np.argsort(-scores)[: min(k, len(self._classes))]
        return [RetrievedClass(cpc_class=self._classes[i], score=float(scores[i])) for i in top]
