"""FastAPI wrapper: invention description → suggested CPC classes (or abstain).

The CPC class index is small and bundled, so it's embedded once at startup and reused.
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .classes import ClassIndex, load_classes
from .classifier import Classifier
from .client import LLMClient
from .config import Settings
from .models import ClassificationResult

app = FastAPI(title="cpc-classifier", version="1.0.0")

_env_origins = [o.strip() for o in os.getenv("CP_CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_env_origins,
    allow_origin_regex=r"https://cpc-classifier[a-z0-9-]*\.vercel\.app|http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

_classifier: Classifier | None = None
_SAMPLES = [
    {
        "label": "RSA public-key cryptosystem — US 4,405,829",
        "text": (
            "A cryptographic communications system in which a message is encoded as a number M "
            "and enciphered by raising M to a predetermined power and computing the remainder "
            "when divided by the product of two predetermined prime numbers; the ciphertext is "
            "deciphered at the receiving terminal by raising it to a second predetermined power "
            "associated with the receiver and computing the residue modulo the same product of "
            "primes, recovering the original message."
        ),
        "tag": "Real patent · granted 1983 · expired",
    },
    {
        "label": "Wearable blood-glucose sensor",
        "text": "A wearable sensor that continuously measures blood glucose and streams readings to a phone.",
        "tag": None,
    },
    {
        "label": "Neural-network image recognition",
        "text": "A method for training a deep neural network to recognise objects in camera images.",
        "tag": None,
    },
    {
        "label": "Autonomous-car lidar control",
        "text": "A system that lets an autonomous car steer itself and adjust speed using lidar and radar.",
        "tag": None,
    },
    {
        "label": "Secure wireless payment protocol",
        "text": "A protocol for secure payment authentication using cryptographic signatures over a wireless network.",
        "tag": None,
    },
]
DISCLAIMER = (
    "Demo/educational tool using an illustrative CPC subset (not the full scheme). "
    "Suggestions only — not a substitute for a professional classification search."
)


def _get_classifier() -> Classifier:
    global _classifier
    if _classifier is None:
        settings = Settings.from_env()
        from .embedder import VoyageEmbedder

        index = ClassIndex(load_classes(), VoyageEmbedder(model=settings.embed_model))
        _classifier = Classifier(index, LLMClient(settings), settings)
    return _classifier


class ClassifyRequest(BaseModel):
    invention: str = Field(..., min_length=3, max_length=2000)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/samples")
def samples() -> dict:
    return {"samples": _SAMPLES, "disclaimer": DISCLAIMER}


@app.post("/api/classify")
def classify(req: ClassifyRequest) -> ClassificationResult:
    try:
        return _get_classifier().classify(req.invention)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
