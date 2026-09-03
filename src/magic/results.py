"""Load run directories into DataFrames and slice them."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from magic.io import iter_jsonl
from magic.stats import bootstrap_ci


def load_runs(root: str | Path = "runs") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (runs_df, samples_df). runs_df: one row per finished run (summary.json), with its
    config.json keys prefixed `config.`; samples_df: one row per sample line with a `run` column."""
    runs: list[dict] = []
    samples: list[dict] = []
    for d in sorted(Path(root).glob("*")):
        if not d.is_dir():
            continue
        summary = d / "summary.json"
        if summary.exists():
            row = {"run": d.name, **json.loads(summary.read_text(encoding="utf-8"))}
            config = d / "config.json"
            if config.exists():
                row["config"] = json.loads(config.read_text(encoding="utf-8"))
            runs.append(row)
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


def ci_by_group(
    df: pd.DataFrame, group_cols: str | list[str], value_col: str = "score", n_boot: int = 1000
) -> pd.DataFrame:
    """Per group: n, mean, lo, hi (bootstrap). Feed the rows to plots.line_with_ci or to_markdown.
    Groups with n < 10 have unreliable intervals; the `n` column is there so you notice."""
    out = []
    for key, g in df.groupby(group_cols, sort=True):
        point, lo, hi = bootstrap_ci(g[value_col].to_numpy(), n_boot=n_boot)
        keys = key if isinstance(key, tuple) else (key,)
        names = group_cols if isinstance(group_cols, list) else [group_cols]
        out.append({**dict(zip(names, keys)), "n": len(g), "mean": point, "lo": lo, "hi": hi})
    return pd.DataFrame(out)


def to_markdown(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Markdown table via tabulate; the index becomes the first column."""
    return df.to_markdown(floatfmt=floatfmt)
