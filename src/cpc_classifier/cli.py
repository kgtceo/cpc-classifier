"""`cpc-classifier` CLI — suggest CPC classes for an invention description (illustrative subset).

    cpc-classifier classify "A neural network accelerator that trains models on-device over 5G"
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .classes import ClassIndex, load_classes
from .classifier import Classifier
from .client import LLMClient
from .config import Settings
from .embedder import VoyageEmbedder

app = typer.Typer(
    add_completion=False,
    help="Suggest CPC classes for an invention description (illustrative subset).",
)
console = Console()


@app.callback()
def _root() -> None:
    """CPC classification suggestions for free-text inventions (demo subset; illustrative only)."""


@app.command()
def classify(
    invention: str = typer.Argument(..., help="The free-text invention description.")
) -> None:
    settings = Settings.from_env()
    embedder = VoyageEmbedder(model=settings.embed_model)
    index = ClassIndex(load_classes(), embedder)
    classifier = Classifier(index, LLMClient(settings), settings)

    with console.status("Classifying…"):
        result = classifier.classify(invention)

    if result.abstained:
        console.print("[yellow]No confident CPC match in the subset — abstained.[/]")
    else:
        t = Table(title="Suggested CPC classes")
        t.add_column("Symbol"); t.add_column("Title"); t.add_column("Conf"); t.add_column("Evidence")
        for c in result.candidates:
            t.add_row(c.symbol, c.title, f"{c.confidence:.2f}", c.evidence_span)
        console.print(t)
    console.print(f"\n[dim]{result.disclaimer}[/]")


if __name__ == "__main__":
    app()
