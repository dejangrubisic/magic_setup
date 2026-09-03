"""1PL (Rasch) IRT on a models x items binary matrix via L2 logistic regression."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression


def _long(matrix: pd.DataFrame) -> pd.DataFrame:
    long = matrix.stack().dropna().rename("y").reset_index()
    long.columns = ["model", "item", "y"]
    return long


def fit_1pl(matrix: pd.DataFrame, C: float = 1.0) -> tuple[pd.Series, pd.Series]:
    """Return (ability per model, difficulty per item). NaN cells are excluded.

    P(correct) = sigmoid(ability_model - difficulty_item); fitted as a no-intercept logistic
    regression on one-hot(model) + one-hot(item); the L2 penalty pins the free location.
    """
    long = _long(matrix)
    if long["y"].nunique() < 2:
        raise ValueError("matrix must contain both 0 and 1 cells")
    models, m_idx = np.unique(long["model"], return_inverse=True)
    items, i_idx = np.unique(long["item"], return_inverse=True)
    n = len(long)
    rows = np.concatenate([np.arange(n), np.arange(n)])
    cols = np.concatenate([m_idx, len(models) + i_idx])
    X = sparse.csr_matrix((np.ones(2 * n), (rows, cols)), shape=(n, len(models) + len(items)))
    clf = LogisticRegression(fit_intercept=False, C=C, max_iter=2000)
    clf.fit(X, long["y"].to_numpy().astype(int))
    coef = clf.coef_[0]
    ability = pd.Series(coef[: len(models)], index=models, name="ability")
    difficulty = pd.Series(-coef[len(models) :], index=items, name="difficulty")
    return ability, difficulty


def discrimination_proxy(matrix: pd.DataFrame, ability: pd.Series) -> pd.Series:
    """Point-biserial correlation of item correctness with model ability; NaN if the item is constant."""
    out = {}
    for item in matrix.columns:
        col = matrix[item].dropna()
        a = ability.reindex(col.index).to_numpy(dtype=float)
        y = col.to_numpy(dtype=float)
        if len(y) < 3 or y.std() == 0 or a.std() == 0:
            out[item] = float("nan")
        else:
            out[item] = float(np.corrcoef(a, y)[0, 1])
    return pd.Series(out, name="discrimination_proxy")


def item_table(matrix: pd.DataFrame, meta: pd.DataFrame, C: float = 1.0) -> pd.DataFrame:
    """Per-item table (task, difficulty, discrimination_proxy, pass_rate, ground_truth) from a
    models x items matrix and a question_id-indexed frame with `task` and `ground_truth`."""
    ability, difficulty = fit_1pl(matrix, C=C)
    items = pd.DataFrame(
        {
            "task": meta["task"].reindex(matrix.columns),
            "difficulty": difficulty,
            "discrimination_proxy": discrimination_proxy(matrix, ability),
            "pass_rate": matrix.mean(),
            "ground_truth": meta["ground_truth"].reindex(matrix.columns),
        }
    )
    items.index.name = "question_id"
    return items


def binarise(scores: pd.DataFrame) -> pd.DataFrame:
    """1.0 where the score is exactly 1, 0.0 elsewhere, NaN preserved."""
    return (scores == 1.0).astype(float).where(scores.notna())
