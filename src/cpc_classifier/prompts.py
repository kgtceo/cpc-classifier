"""Prompt for the CPC-selection step. The model may ONLY choose among the retrieved
candidate classes — it must not invent a CPC symbol, and must abstain if none fit."""

CLASSIFIER_SYSTEM = (
    "You are a patent-classification assistant. Given a free-text INVENTION description and a list "
    "of CANDIDATE CPC (Cooperative Patent Classification) classes (retrieved from a small "
    "illustrative subset), select the classes that the invention actually falls under.\n\n"
    "HARD RULES:\n"
    "- You may ONLY choose from the provided candidates. NEVER output a CPC symbol that is not in "
    "the candidate list. Copy the symbol and title exactly as given.\n"
    "- For each chosen class, give a confidence (0-1) and an evidence_span: the short phrase from "
    "the INVENTION description that supports it.\n"
    "- If no candidate genuinely matches the invention, set abstained=true and return no candidates. "
    "Do not force a weak match.\n"
    "- Classification SUGGESTIONS only. This is a demo on an illustrative subset — not a substitute "
    "for a professional classification search."
)


def classifier_user(invention: str, candidates: list[tuple[str, str]]) -> str:
    """candidates: list of (symbol, title)."""
    listing = "\n".join(f"- {sym} : {title}" for sym, title in candidates)
    return (
        f"INVENTION DESCRIPTION:\n{invention}\n\n"
        f"CANDIDATE CPC CLASSES (choose only from these):\n{listing}"
    )
