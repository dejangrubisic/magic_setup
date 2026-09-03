"""Per-slice MAP@k tables from a samples DataFrame."""

import pandas as pd
import pytest
from scripts.eedi_slices import hardest, slice_table


@pytest.fixture
def samples():
    return pd.DataFrame(
        {
            "SubjectName": ["A", "A", "B", "B", "B", "C"],
            "ConstructName": ["a1", "a1", "b1", "b2", "b2", "c1"],
            "ap": [1.0, 0.0, 0.5, 0.25, 0.0, 1.0],
        }
    )


def test_slice_table(samples):
    t = slice_table(samples, "SubjectName", n_boot=50)
    assert list(t.index) == ["A", "B", "C", "ALL"]
    assert list(t.columns) == ["n", "map25", "lo", "hi"]
    assert t.loc["A", "map25"] == pytest.approx(0.5)
    assert t.loc["B", "map25"] == pytest.approx(0.25)
    assert t.loc["ALL", "map25"] == pytest.approx(2.75 / 6)
    assert list(t.n) == [2, 3, 1, 6]
    assert (t.lo <= t.map25).all()
    assert (t.map25 <= t.hi).all()


def test_hardest_filters_min_n(samples):
    h = hardest(samples, "ConstructName", min_n=2, top=5, n_boot=50)
    assert list(h.index) == ["b2", "a1"]  # c1 and b1 have n=1; sorted ascending by map25
    assert h.loc["b2", "map25"] == pytest.approx(0.125)
    assert len(hardest(samples, "ConstructName", min_n=1, top=2, n_boot=50)) == 2
