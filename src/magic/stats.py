"""Stats and reproducibility: bootstrap/Wilson intervals, hash-stable splits, seeding."""

from __future__ import annotations

import random
import zlib
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


def hit_at_k(ranks, k: int) -> float:
    """Fraction of items whose true answer rank (1-based; None/0 = absent) is <= k."""
    r = list(ranks)
    return float(np.mean([x is not None and 0 < x <= k for x in r])) if r else float("nan")


def stable_split(uid: str, test_pct: int = 20, salt: str = "v1") -> str:
    """Assign a uid to "train"/"test" by hash, so other rows appearing never move it."""
    bucket = zlib.crc32(f"{salt}:{uid}".encode()) % 100
    return "test" if bucket < test_pct else "train"


def seed_everything(seed: int) -> None:
    """Seed random and numpy (and torch if installed); does not touch cuDNN determinism."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
