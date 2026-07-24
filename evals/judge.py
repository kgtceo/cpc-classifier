"""LLM-as-judge for cpc-classifier (opus grades the sonnet classifier's selections).

The deterministic gates prove the hard guarantees (no hallucinated symbol, evidence spans
verbatim, abstention). The judge grades what set-membership can't: whether the SELECTION
itself is sound — do the chosen classes genuinely fit the invention, does the quoted
evidence actually support each class, and was nothing forced where an abstention (or a
different candidate) was the honest call.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from cpc_classifier.client import LLMClient
from cpc_classifier.config import Settings
from cpc_classifier.models import ClassificationResult

JUDGE_SYSTEM = (
    "You are a strict evaluator of a patent-classification assistant. You are given an "
    "INVENTION description, the CANDIDATE CPC classes the assistant could choose from, and "
    "the assistant's SELECTION (chosen classes, each with a confidence and an evidence quote "
    "from the description).\n\n"
    "Grade three things, strictly:\n"
    "- selection_sound: every chosen class genuinely fits the invention — nothing forced, "
    "nothing clearly wrong, and no obviously-better retrieved candidate was ignored.\n"
    "- evidence_supports: for every chosen class, the quoted evidence really does support "
    "that class (not just words that happen to appear in the description).\n"
    "- no_overclaim: confidences are not absurdly high for weak fits, and the selection does "
    "not read more into the invention than the text states.\n"
    "Judge only from the given text. Be strict: when in doubt, fail the dimension and say why."
)


class JudgeVerdict(BaseModel):
    selection_sound: bool = Field(description="Every chosen class genuinely fits the invention.")
    evidence_supports: bool = Field(description="Every evidence quote supports its chosen class.")
    no_overclaim: bool = Field(description="No inflated confidence or over-reading of the text.")
    comment: str = Field(description="One or two sentences explaining the grades.")

    @property
    def passed(self) -> bool:
        return self.selection_sound and self.evidence_supports and self.no_overclaim


def judge_case(client: LLMClient, settings: Settings, result: ClassificationResult) -> JudgeVerdict:
    candidates = "\n".join(
        f"- {r.cpc_class.symbol} : {r.cpc_class.title}" for r in result.retrieved
    )
    selection = "\n".join(
        f"- {c.symbol} : {c.title} (confidence {c.confidence:.2f}) — evidence: \"{c.evidence_span}\""
        for c in result.candidates
    ) or "(abstained — no classes selected)"
    user = (
        f"INVENTION DESCRIPTION:\n{result.invention}\n\n"
        f"CANDIDATE CPC CLASSES (what the assistant could choose from):\n{candidates}\n\n"
        f"ASSISTANT'S SELECTION:\n{selection}"
    )
    return client.structured(
        schema=JudgeVerdict, system=JUDGE_SYSTEM, user=user, model=settings.judge_model
    )
