"""JSONL read/write helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Create a directory (and parents) if missing and return it."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    """Yield one dict per non-blank line; streams, so it never loads the whole file."""
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                yield json.loads(stripped)


def read_jsonl(path: str | Path) -> list[dict]:
    """Read a whole JSONL file into a list of dicts (blank lines skipped)."""
    return list(iter_jsonl(path))


def write_jsonl(path: str | Path, rows: Iterable[dict], append: bool = False) -> Path:
    """Write dicts as JSONL, creating parent dirs; non-JSON values are str()-ed, not dropped."""
    p = Path(path)
    ensure_dir(p.parent)
    with p.open("a" if append else "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    return p
