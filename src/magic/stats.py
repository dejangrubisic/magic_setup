"""Confidence intervals for eval numbers."""

from __future__ import annotations

import numpy as np

_NAN3 = (float("nan"), float("nan"), float("nan"))


def bootstrap_ci(
    values, stat=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float, float]:
    """Percentile bootstrap CI: returns (point, lo, hi); empty input gives nans."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return _NAN3
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, v.size, size=(n_boot, v.size))
    boots = np.array([stat(v[i]) for i in idx])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(stat(v)), float(lo), float(hi)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Wilson score interval for k/n; better than normal-approx at extremes, nans when n=0."""
    if n == 0:
        return _NAN3
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z / denom * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return float(p), float(center - half), float(center + half)


def paired_bootstrap_diff(
    a, b, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float, float]:
    """CI on the per-item difference a - b; requires the two arrays to be aligned by item."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"paired arrays must align: {x.shape} != {y.shape}")
    return bootstrap_ci(x - y, np.mean, n_boot=n_boot, alpha=alpha, seed=seed)
