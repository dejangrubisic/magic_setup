import random

import numpy as np
import pytest

from magic.stats import (
    bootstrap_ci,
    paired_bootstrap_diff,
    seed_everything,
    stable_split,
    wilson_interval,
)


def test_bootstrap_ci_brackets_the_true_mean():
    values = np.random.default_rng(0).normal(loc=5.0, scale=1.0, size=400)
    point, lo, hi = bootstrap_ci(values, n_boot=500)
    assert point == pytest.approx(values.mean())
    assert lo < 5.0 < hi
    assert hi - lo == pytest.approx(2 * 1.96 / np.sqrt(400), abs=0.05)


def test_bootstrap_ci_is_seeded():
    values = list(range(50))
    assert bootstrap_ci(values, n_boot=200, seed=1) == bootstrap_ci(values, n_boot=200, seed=1)
    assert bootstrap_ci(values, n_boot=200, seed=1) != bootstrap_ci(values, n_boot=200, seed=2)


def test_bootstrap_ci_of_a_constant_is_degenerate():
    assert bootstrap_ci([3.0] * 20, n_boot=200) == (3.0, 3.0, 3.0)


def test_bootstrap_ci_accepts_other_statistics():
    point, lo, hi = bootstrap_ci(list(range(101)), stat=np.median, n_boot=300)
    assert point == 50.0
    assert lo <= 50.0 <= hi


def test_bootstrap_ci_empty_is_nan():
    assert all(np.isnan(x) for x in bootstrap_ci([]))


def test_wilson_matches_published_values():
    p, lo, hi = wilson_interval(50, 100)
    assert (p, lo, hi) == pytest.approx((0.5, 0.404, 0.596), abs=1e-3)
    assert wilson_interval(0, 10)[1] == pytest.approx(0.0, abs=1e-9)
    assert wilson_interval(10, 10)[2] == pytest.approx(1.0, abs=1e-9)


def test_wilson_is_asymmetric_near_zero_and_never_leaves_unit_interval():
    p, lo, hi = wilson_interval(1, 20)
    assert p == 0.05
    assert 0.0 < lo < p < hi < 1.0
    assert hi - p > p - lo


def test_wilson_zero_n_is_nan_not_an_error():
    assert all(np.isnan(x) for x in wilson_interval(0, 0))


def test_paired_diff_of_identical_arrays_is_zero():
    scores = [1.0, 0.0, 1.0, 1.0, 0.0]
    assert paired_bootstrap_diff(scores, scores, n_boot=200) == (0.0, 0.0, 0.0)


def test_paired_diff_detects_a_constant_offset():
    rng = np.random.default_rng(0)
    a = rng.normal(size=200)
    mean_diff, lo, hi = paired_bootstrap_diff(a + 0.5, a, n_boot=300)
    assert mean_diff == pytest.approx(0.5)
    assert lo == pytest.approx(0.5)
    assert hi == pytest.approx(0.5)


def test_paired_diff_on_noisy_pairs_includes_zero_when_runs_tie():
    rng = np.random.default_rng(1)
    a, b = rng.normal(size=300), rng.normal(size=300)
    mean_diff, lo, hi = paired_bootstrap_diff(a, b, n_boot=500)
    assert lo < mean_diff < hi
    assert lo < 0.0 < hi


def test_paired_diff_requires_aligned_arrays():
    with pytest.raises(ValueError, match="align"):
        paired_bootstrap_diff([1.0, 2.0], [1.0])


def test_bootstrap_ci_paired_arrays_and_nan_resamples():
    import numpy as np
    from scipy.stats import spearmanr

    from magic.stats import bootstrap_ci

    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    pred = np.array([1.1, 1.9, 3.2, 3.9, 5.3, 5.8])
    point, lo, hi = bootstrap_ci(y, lambda a, b: spearmanr(a, b).statistic, 300, 0.05, 0, pred)
    assert point == 1.0
    assert lo <= point <= hi
    assert not np.isnan(lo)  # constant resamples give NaN correlations and are ignored


IDS = [f"item-{i}" for i in range(10_000)]


def test_split_is_deterministic_and_binary():
    assert stable_split("item-1") == stable_split("item-1")
    assert {stable_split(u) for u in IDS[:100]} <= {"train", "test"}


def test_fraction_is_close_to_test_pct():
    for pct in (10, 20, 50):
        frac = sum(stable_split(u, test_pct=pct) == "test" for u in IDS) / len(IDS)
        assert abs(frac - pct / 100) < 0.03


def test_membership_does_not_depend_on_other_rows():
    subset = [stable_split(u) for u in IDS[::7]]
    assert subset == [stable_split(u) for u in IDS[::7]]
    assert stable_split("item-3", test_pct=20) == stable_split("item-3", test_pct=20)


def test_test_pct_edges():
    assert all(stable_split(u, test_pct=0) == "train" for u in IDS[:200])
    assert all(stable_split(u, test_pct=100) == "test" for u in IDS[:200])


def test_changing_salt_moves_some_ids():
    moved = sum(stable_split(u, salt="v1") != stable_split(u, salt="v2") for u in IDS)
    assert 0.1 * len(IDS) < moved < 0.5 * len(IDS)


def test_seed_everything_makes_random_and_numpy_reproducible():
    seed_everything(0)
    first = (random.random(), np.random.rand(3).tolist())
    seed_everything(0)
    assert (random.random(), np.random.rand(3).tolist()) == first
    seed_everything(1)
    assert (random.random(), np.random.rand(3).tolist()) != first
