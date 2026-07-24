"""Typed contracts for cpc-classifier.

CPC classes come from a bundled illustrative CPC subset. The LLM is only ever allowed to
CHOOSE among retrieved candidate classes — it can't emit a raw CPC symbol from memory
(CPC symbols are hallucination-prone). Every returned symbol is validated against the subset.

DEMO / EDUCATIONAL — illustrative CPC subset, not the full scheme; not a substitute for a
professional classification search.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CpcClass(BaseModel):
    """One CPC class in the illustrative subset."""

    symbol: str = Field(description="CPC classification symbol (from the bundled subset).")
    title: str = Field(description="Class title / definition.")

    def index_text(self) -> str:
        return f"{self.symbol} : {self.title}"


class RetrievedClass(BaseModel):
    cpc_class: CpcClass
    score: float = Field(description="Cosine similarity to the invention (higher = closer).")


class CpcCandidate(BaseModel):
    """A CPC class the model selected — its symbol MUST be one of the retrieved candidates."""

    symbol: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0, description="0-1 confidence this class applies.")
    evidence_span: str = Field(
        description="The short phrase from the invention description that supports this class."
    )


class Classification(BaseModel):
    """The model's selection — validated so every symbol exists in the retrieved candidates."""

    candidates: list[CpcCandidate] = Field(default_factory=list)
    abstained: bool = Field(
        description="True when no retrieved candidate confidently fits the invention."
    )


class ClassificationResult(BaseModel):
    """The deliverable: the invention, chosen candidate classes, and the retrieval trace."""

    invention: str
    candidates: list[CpcCandidate] = Field(default_factory=list)
    abstained: bool = False
    retrieved: list[RetrievedClass] = Field(default_factory=list)
    disclaimer: str = (
        "Demo/educational tool using an illustrative CPC subset (not the full scheme). "
        "Suggestions only — not a substitute for a professional classification search."
    )
