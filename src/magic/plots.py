"""Two matplotlib helpers, headless (Agg) so they work over ssh and in CI."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from magic.io import ensure_dir


def _save(fig, path: str | Path | None) -> None:
    if path is not None:
        ensure_dir(Path(path).parent)
        fig.savefig(path, dpi=150, bbox_inches="tight")


def bar_with_ci(labels, values, lows, highs, title: str = "", path=None):
    """Bar chart with asymmetric error bars from (lo, hi) bounds, not +/- widths."""
    values, lows, highs = (np.asarray(a, dtype=float) for a in (values, lows, highs))
    fig, ax = plt.subplots(figsize=(max(4.0, 0.9 * len(values)), 4.0))
    ax.bar(
        list(labels),
        values,
        yerr=np.vstack([values - lows, highs - values]),
        capsize=4,
        color="#4c78a8",
    )
    ax.set_title(title)
    ax.margins(y=0.15)
    ax.tick_params(axis="x", rotation=30)
    _save(fig, path)
    return fig


def heatmap(df: pd.DataFrame, title: str = "", path=None, fmt: str = ".2f"):
    """Annotated heatmap of a numeric DataFrame; NaN cells render as 'nan'."""
    data = df.to_numpy(dtype=float)
    n_rows, n_cols = data.shape
    fig, ax = plt.subplots(figsize=(1.3 * n_cols + 2.0, 0.5 * n_rows + 2.0))
    im = ax.imshow(data, cmap="viridis", aspect="auto")
    ax.set_xticks(range(n_cols), [str(c) for c in df.columns], rotation=30, ha="right")
    ax.set_yticks(range(n_rows), [str(i) for i in df.index])
    for i in range(n_rows):
        for j in range(n_cols):
            ax.text(j, i, format(data[i, j], fmt), ha="center", va="center", color="w", fontsize=8)
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    _save(fig, path)
    return fig
