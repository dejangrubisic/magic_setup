import random

import numpy as np

from magic.splits import seed_everything, stable_split

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
