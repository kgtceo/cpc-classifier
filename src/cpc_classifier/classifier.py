"""invention -> retrieved candidate CPC classes -> LLM selection (validated) -> ClassificationResult.

The safety guarantee lives here, in two deterministic filters applied AFTER the LLM selects:
  1. Symbol filter — DROP any candidate whose symbol was not among the retrieved candidates,
     so even if the model invents a symbol, it can never reach the output.
  2. Evidence filter — DROP any candidate whose evidence_span is not a verbatim substring of
     the invention description (whitespace/case-normalised), so the model can't fabricate the
     "supporting phrase" either. If you can't quote it, you can't claim it.
If nothing survives, we abstain.
"""

from __future__ import annotations

import re

from . import prompts
from .classes import ClassIndex
from .client import LLMClient
from .config import Settings
from .models import Classification, ClassificationResult, CpcCandidate


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


class Classifier:
    def __init__(self, index: ClassIndex, client: LLMClient, settings: Settings) -> None:
        self._index = index
        self._client = client
        self._settings = settings

    def classify(self, invention: str) -> ClassificationResult:
        retrieved = self._index.search(invention, self._settings.top_k)
        if not retrieved:
            return ClassificationResult(
                invention=invention, candidates=[], abstained=True, retrieved=[]
            )

        allowed = {r.cpc_class.symbol: r.cpc_class.title for r in retrieved}
        selection = self._client.structured(
            schema=Classification,
            system=prompts.CLASSIFIER_SYSTEM,
            user=prompts.classifier_user(
                invention, [(sym, title) for sym, title in allowed.items()]
            ),
        )

        # Enforce the guarantees: keep only candidates whose symbol was actually retrieved AND
        # whose evidence_span is a verbatim substring of the invention (a fabricated "supporting
        # phrase" is a fabricated fact — drop the candidate). Titles are normalised to canonical.
        invention_norm = _norm(invention)
        valid: list[CpcCandidate] = []
        for c in selection.candidates:
            if c.symbol not in allowed:
                continue
            span_norm = _norm(c.evidence_span)
            if not span_norm or span_norm not in invention_norm:
                continue
            valid.append(c.model_copy(update={"title": allowed[c.symbol]}))

        return ClassificationResult(
            invention=invention,
            candidates=valid,
            abstained=selection.abstained or not valid,
            retrieved=retrieved,
        )
