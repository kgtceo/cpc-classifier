"""Offline test doubles — FakeEmbedder + a fake selection client (no API keys, no network)."""

from __future__ import annotations

import pytest

from cpc_classifier.config import Settings
from cpc_classifier.models import Classification


class FakeClassifierClient:
    """Returns a scripted Classification. Use it to test the validation guarantee
    (drop symbols not retrieved)."""

    def __init__(self, classification: Classification) -> None:
        self._classification = classification
        self.calls = 0

    def structured(self, *, schema, system, user, model=None):
        self.calls += 1
        return self._classification


@pytest.fixture
def settings() -> Settings:
    return Settings(anthropic_api_key="test-key", top_k=5)
