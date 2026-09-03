"""Issue 02: 1PL fit and discrimination proxy on a synthetic matrix."""

import numpy as np
import pandas as pd
import pytest
from tasks.livebench_irt import binarise, discrimination_proxy, fit_1pl, item_table


@pytest.fixture
def matrix() -> pd.DataFrame:
    # 6 models (m0 strongest .. m5 weakest) x 8 items; item i7 is answered by nobody,
    # i6 only by the two weakest, i0 by everybody but the weakest.
    rng = np.random.default_rng(0)
    skill = np.array([3.0, 2.0, 1.0, 0.0, -1.0, -2.0])
    diff = np.array([-2.0, -1.0, 0.0, 0.5, 1.0, 2.0])
    p = 1 / (1 + np.exp(-(skill[:, None] - diff[None, :])))
    data = (rng.random(p.shape) < p).astype(float)
    data[0, :] = 1.0  # m0 answers everything
    data[:5, 0] = 1.0  # i0: everybody but the weakest
    data[5, :] = 0.0
    data[1:, 4] = 0.0  # i4: only the strongest model passes
    i6 = np.array([0, 0, 0, 0, 1, 1], dtype=float)
    i7 = np.zeros(6)
    full = np.column_stack([data, i6, i7])
    m = pd.DataFrame(full, index=[f"m{i}" for i in range(6)], columns=[f"i{j}" for j in range(8)])
    m.loc["m3", "i2"] = np.nan  # a missing cell must not break the fit
    return m


def test_fit_1pl_orders_models_and_items(matrix):
    ability, difficulty = fit_1pl(matrix)
    assert list(ability.index) == list(matrix.index)
    assert list(difficulty.index) == list(matrix.columns)
    assert ability.idxmax() == "m0"
    assert difficulty.idxmax() == "i7"
    pass_rate = matrix.mean()
    order_by_rate = pass_rate.sort_values(ascending=False).index.tolist()
    order_by_diff = difficulty.sort_values().index.tolist()
    assert order_by_diff[0] == order_by_rate[0]
    assert order_by_diff[-1] == order_by_rate[-1]
    assert np.corrcoef(pass_rate.rank(), difficulty.rank())[0, 1] < -0.9


def test_fit_1pl_rejects_constant_matrix():
    m = pd.DataFrame(np.ones((3, 3)), index=list("abc"), columns=list("xyz"))
    with pytest.raises(ValueError, match="both 0 and 1"):
        fit_1pl(m)


def test_discrimination_proxy_sign(matrix):
    ability, _ = fit_1pl(matrix)
    proxy = discrimination_proxy(matrix, ability)
    assert proxy["i6"] < 0  # only the two weakest models pass it
    assert proxy["i4"] > 0  # only the strongest model passes it
    assert proxy["i0"] > 0  # everybody but the weakest passes it
    assert np.isnan(proxy["i7"])  # constant item
    assert proxy.index.tolist() == matrix.columns.tolist()


def test_fit_1pl_excludes_nan_cells(matrix):
    _, with_nan = fit_1pl(matrix)
    _, as_zero = fit_1pl(matrix.fillna(0.0))
    assert with_nan["i2"] < as_zero["i2"]  # a missing cell must not count as a failure


def test_binarise_keeps_nan_and_drops_partial_credit():
    scores = pd.DataFrame({"a": [1.0, 0.5], "b": [np.nan, 0.0]}, index=["m0", "m1"])
    out = binarise(scores)
    assert out["a"].tolist() == [1.0, 0.0]
    assert np.isnan(out.loc["m0", "b"])
    assert out.loc["m1", "b"] == 0.0


def test_item_table_columns_and_values(matrix):
    meta = pd.DataFrame(
        {"task": ["spatial"] * 4 + ["zebra_puzzle"] * 4, "ground_truth": list("abcdefgh")},
        index=matrix.columns,
    )
    items = item_table(matrix, meta)
    assert list(items.columns) == [
        "task",
        "difficulty",
        "discrimination_proxy",
        "pass_rate",
        "ground_truth",
    ]
    assert items.index.name == "question_id"
    assert items.index.tolist() == matrix.columns.tolist()
    assert items.loc["i7", "pass_rate"] == 0.0
    assert items["difficulty"].idxmax() == "i7"
    assert items.loc["i6", "discrimination_proxy"] < 0
    assert items.loc["i0", "ground_truth"] == "a"
    assert items.loc["i5", "task"] == "zebra_puzzle"
