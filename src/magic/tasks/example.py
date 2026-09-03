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


def extract_strict(text: str) -> str | None:
    """First 'answer is (X)'; None means a format failure, not a wrong answer."""
    m = _STRICT.search(text)
    return m.group(1).upper() if m else None


def extract_lenient(text: str) -> str | None:
    """Last standalone capital letter; the strict/lenient gap is the format-failure rate."""
    found = _LENIENT.findall(text)
    return found[-1] if found else None


def score(prediction: str | None, target: str) -> float:
    """Deterministic reward in [0, 1]; keep rewards pure so they are unit-testable."""
    return float(prediction is not None and prediction.upper() == target.upper())
