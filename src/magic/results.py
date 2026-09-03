"""Load run directories into DataFrames and slice them."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from magic.io import iter_jsonl


def load_runs(root: str | Path = "runs") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (runs_df, samples_df); only runs with summary.json count as finished runs."""
    runs: list[dict] = []
    samples: list[dict] = []
    for d in sorted(Path(root).glob("*")):
        if not d.is_dir():
            continue
        summary = d / "summary.json"
        if summary.exists():
            runs.append({"run": d.name, **json.loads(summary.read_text(encoding="utf-8"))})
        sample_file = d / "samples.jsonl"
        if sample_file.exists():
            samples += [{"run": d.name, **row} for row in iter_jsonl(sample_file)]
    return pd.json_normalize(runs), pd.json_normalize(samples)


def by_slice(
    samples_df: pd.DataFrame,
    slice_col: str,
    value_col: str = "score",
    run_col: str = "run",
) -> pd.DataFrame:
    """Mean value_col per slice (rows) x run (cols), plus an 'n' count and an 'ALL' row."""
    pivot = samples_df.pivot_table(
        index=slice_col, columns=run_col, values=value_col, aggfunc="mean"
    )
    pivot["n"] = samples_df.groupby(slice_col).size()
    overall = {**samples_df.groupby(run_col)[value_col].mean().to_dict(), "n": len(samples_df)}
    pivot.loc["ALL"] = pd.Series(overall).reindex(pivot.columns)
    return pivot


def to_markdown(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Markdown table via tabulate; the index becomes the first column."""
    return df.to_markdown(floatfmt=floatfmt)
