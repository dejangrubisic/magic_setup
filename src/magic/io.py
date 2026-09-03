"""JSONL and JSON helpers. Never write NaN: it is not JSON and breaks jq and every loader."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Iterator
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """mkdir -p and return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def nan_to_none(obj):
    """Recursively turn float NaN/inf and pandas NA into None so the result is valid JSON."""
    if isinstance(obj, dict):
        return {k: nan_to_none(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [nan_to_none(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    try:  # pandas.NA / numpy nan without importing pandas here
        if obj is not None and not isinstance(obj, str | bytes) and obj != obj:
            return None
    except (TypeError, ValueError):
        pass
    return obj


def dumps(obj, **kwargs) -> str:
    """json.dumps with NaN -> null and non-JSON types stringified."""
    return json.dumps(nan_to_none(obj), default=str, allow_nan=False, ensure_ascii=False, **kwargs)


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    """Yield one dict per non-blank line."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def read_jsonl(path: str | Path) -> list[dict]:
    """All rows of a JSONL file."""
    return list(iter_jsonl(path))


def write_jsonl(path: str | Path, rows: Iterable[dict], append: bool = False) -> Path:
    """Write rows one per line, creating parent dirs; append=True for resumable logs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a" if append else "w", encoding="utf-8") as f:
        for row in rows:
            f.write(dumps(row) + "\n")
    return p


def fetch_hf(
    repo: str, config: str | None = None, split: str = "train", out: str | Path | None = None
):
    """load_dataset(...).to_pandas(), print shape and dtypes (the 'inspect columns first' step),
    optionally save to parquet under data/raw. Network: never call from tests."""
    from datasets import load_dataset

    ds = load_dataset(repo, config, split=split) if config else load_dataset(repo, split=split)
    df = ds.to_pandas()
    print(f"{repo}{'/' + config if config else ''}[{split}] shape={df.shape}\n{df.dtypes}")
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)
    return df
