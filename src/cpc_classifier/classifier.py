"""invention -> retrieved candidate CPC classes -> LLM selection (validated) -> ClassificationResult.

The safety guarantee lives here: after the LLM selects, we DROP any candidate whose symbol
was not among the retrieved candidates. So even if the model invents a symbol, it can never reach
the output. If nothing survives, we abstain.
"""

from __future__ import annotations

from . import prompts
from .classes import ClassIndex
from .client import LLMClient
from .config import Settings
from .models import Classification, ClassificationResult, CpcCandidate


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

        # Enforce the guarantee: keep only candidates whose symbol was actually retrieved, and
        # normalise the title to the canonical one (ignore any title the model rewrote).
        valid: list[CpcCandidate] = []
        for c in selection.candidates:
            if c.symbol in allowed:
                valid.append(c.model_copy(update={"title": allowed[c.symbol]}))

        return ClassificationResult(
            invention=invention,
            candidates=valid,
            abstained=selection.abstained or not valid,
            retrieved=retrieved,
        )
