"""cpc-classifier — suggest CPC classes for a free-text invention description.

Retrieval over an illustrative CPC (Cooperative Patent Classification) subset finds candidate
classes; the LLM selects only among those candidates (it can never emit a symbol it wasn't
shown), and abstains when nothing fits. Ships an eval harness scoring accuracy, abstention, and
that no symbol is hallucinated.

DEMO / EDUCATIONAL — illustrative subset; suggestions only; not a substitute for a professional
classification search."""

from .classes import ClassIndex, load_classes
from .classifier import Classifier
from .client import LLMClient
from .config import Settings
from .embedder import Embedder, FakeEmbedder, VoyageEmbedder
from .models import (
    Classification,
    ClassificationResult,
    CpcCandidate,
    CpcClass,
    RetrievedClass,
)

__all__ = [
    "LLMClient",
    "Classifier",
    "ClassIndex",
    "load_classes",
    "Settings",
    "Embedder",
    "FakeEmbedder",
    "VoyageEmbedder",
    "CpcCandidate",
    "Classification",
    "ClassificationResult",
    "RetrievedClass",
    "CpcClass",
]
