"""Template task module. Copy to magic/tasks/<name>.py; keep loading, scoring and rewards here."""

from __future__ import annotations

import re

from magic.io import read_jsonl


def load_rows(path: str, limit: int | None = None) -> list[dict]:
    """Rows of {id, input, target, metadata}; adapt foreign schemas here, never downstream."""
    rows = read_jsonl(path)
    return rows[:limit] if limit else rows


_STRICT = re.compile(r"answer is \(?([A-J])\)?", re.IGNORECASE)
_LENIENT = re.compile(r"\b([A-J])\b")


def extract_strict(text: str, first: bool = True) -> str | None:
    """'answer is (X)' (first match by default); None means a format failure, not a wrong answer."""
    found = _STRICT.findall(text)
    return (found[0] if first else found[-1]).upper() if found else None


def runaway(text: str) -> bool:
    """True when the first and last strict answers differ: the model kept generating after answering."""
    found = [f.upper() for f in _STRICT.findall(text)]
    return len(found) > 1 and found[0] != found[-1]


def extract_lenient(text: str) -> str | None:
    """Last standalone capital letter; the strict/lenient gap is the format-failure rate."""
    found = _LENIENT.findall(text)
    return found[-1] if found else None


def score(prediction: str | None, target: str) -> float:
    """Deterministic reward in [0, 1]; keep rewards pure so they are unit-testable."""
    return float(prediction is not None and prediction.upper() == target.upper())
