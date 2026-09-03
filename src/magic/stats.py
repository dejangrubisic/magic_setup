"""Uncertainty helpers: bootstrap and Wilson intervals. Small n gives wide, honest intervals."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def bootstrap_ci(
    values,
    stat: Callable = np.mean,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
    *arrays,
) -> tuple[float, float, float]:
    """(point, lo, hi) percentile bootstrap. With extra `arrays`, `stat` gets aligned resamples of all of them
    (paired statistics such as Spearman(y, pred)); NaN resamples (constant draws) are ignored."""
    cols = [np.asarray(values)] + [np.asarray(a) for a in arrays]
    n = len(cols[0])
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    point = float(stat(*cols))
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = np.array([stat(*[c[i] for c in cols]) for i in idx], dtype=float)
    lo, hi = np.nanpercentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def paired_bootstrap_diff(
    a, b, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float, float]:
    """(mean_diff, lo, hi) of a - b over the same items; the CI excluding 0 is the usual read."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("a and b must be aligned per item")
    return bootstrap_ci(a - b, np.mean, n_boot=n_boot, alpha=alpha, seed=seed)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """(p, lo, hi) Wilson score interval for k successes in n trials; n=0 -> NaNs."""
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return p, float(centre - half), float(centre + half)
