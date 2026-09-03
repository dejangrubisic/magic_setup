"""Three plot helpers; import this module explicitly so `import magic` stays free of matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _save(fig, path) -> None:
    """Save a PNG, creating parent directories."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)


def bar_with_ci(labels, values, lows, highs, title: str = "", path=None):
    """Bars with asymmetric error bars; saves a PNG if `path` is given."""
    values, lows, highs = (np.asarray(x, dtype=float) for x in (values, lows, highs))
    fig, ax = plt.subplots(figsize=(max(4, 0.6 * len(labels)), 3.5))
    ax.bar(range(len(labels)), values, yerr=[values - lows, highs - values], capsize=3)
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_title(title)
    fig.tight_layout()
    if path:
        _save(fig, path)
    return fig


def heatmap(df, title: str = "", path=None, fmt: str = ".2f"):
    """Annotated heatmap of a numeric DataFrame (rows x columns)."""
    data = df.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(1 + 0.8 * data.shape[1], 1 + 0.5 * data.shape[0]))
    im = ax.imshow(data, aspect="auto")
    ax.set_xticks(range(data.shape[1]), [str(c) for c in df.columns], rotation=30, ha="right")
    ax.set_yticks(range(data.shape[0]), [str(i) for i in df.index])
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                ax.text(j, i, format(data[i, j], fmt), ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    if path:
        _save(fig, path)
    return fig


def line_with_ci(curves: dict, title: str = "", xlabel: str = "", ylabel: str = "", path=None):
    """Learning curves: {name: (x, mean, lo, hi)} as lines with shaded CI bands."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for name, (x, mean, lo, hi) in curves.items():
        x, mean, lo, hi = (np.asarray(v, dtype=float) for v in (x, mean, lo, hi))
        ax.plot(x, mean, label=name)
        ax.fill_between(x, lo, hi, alpha=0.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    if path:
        _save(fig, path)
    return fig
