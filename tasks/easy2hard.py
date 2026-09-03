"""Easy2Hard-Bench (E2H-GSM8K): hand features and difficulty-prediction helpers."""

from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from magic import bootstrap_ci, stable_split

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
_OPERATOR = re.compile("[+\\-*/\u00d7\u00f7%=]")
_SENTENCE = re.compile(r"[.?!]+(?:\s+|$)")
_FINAL = re.compile(r"####\s*([-\d.,]+)")

HAND_FEATURES = [
    "q_len_chars",
    "q_len_words",
    "n_numbers",
    "n_operators",
    "n_sentences",
    "answer_magnitude",
    "sol_len_lines",
]
LENGTH_FEATURES = ["q_len_chars", "q_len_words"]


def _final_answer(answer: str) -> float | None:
    m = _FINAL.search(answer)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def hand_features(row: dict) -> dict:
    """Cheap surface features of a GSM8K item; answer_magnitude is log10(1 + |final answer|)."""
    q, a = row["question"], row.get("answer", "")
    final = _final_answer(a)
    return {
        "q_len_chars": len(q),
        "q_len_words": len(q.split()),
        "n_numbers": len(_NUMBER.findall(q)),
        "n_operators": len(_OPERATOR.findall(q)),
        "n_sentences": sum(1 for s in _SENTENCE.split(q) if s.strip()),
        "answer_magnitude": math.log10(1 + abs(final)) if final is not None else 0.0,
        "sol_len_lines": sum(1 for line in a.splitlines() if line.strip()),
    }


def feature_frame(rows: list[dict]) -> pd.DataFrame:
    """One row per item: id, split, question, rating columns and the hand features."""
    recs = []
    for r in rows:
        recs.append(
            {
                "id": r["id"],
                "split": stable_split(r["id"], test_pct=20),
                "question": r["question"],
                "rating": r["rating"],
                "rating_quantile": r["rating_quantile"],
                **hand_features(r),
            }
        )
    return pd.DataFrame(recs)


def spearman_ci(y_true, y_pred, seed: int = 0, n_boot: int = 2000) -> tuple[float, float, float]:
    """Spearman rho with a percentile-bootstrap 95% CI over paired resamples of items."""
    yt, yp = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)

    def rho(idx: np.ndarray) -> float:
        i = idx.astype(int)
        if len(np.unique(yt[i])) < 2 or len(np.unique(yp[i])) < 2:
            return 0.0  # degenerate resample (constant); only happens for tiny n
        return float(spearmanr(yt[i], yp[i]).statistic)

    return bootstrap_ci(np.arange(len(yt)), stat=rho, n_boot=n_boot, seed=seed)


def build_models(seed: int = 0) -> dict[str, Pipeline]:
    """Named sklearn pipelines that fit on the feature_frame columns."""
    length_only = Pipeline(
        [
            ("cols", ColumnTransformer([("num", StandardScaler(), LENGTH_FEATURES)])),
            ("ridge", Ridge(alpha=1.0)),
        ]
    )
    ridge_hand_tfidf = Pipeline(
        [
            (
                "cols",
                ColumnTransformer(
                    [
                        ("num", StandardScaler(), HAND_FEATURES),
                        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2), "question"),
                    ]
                ),
            ),
            ("ridge", Ridge(alpha=3.0)),
        ]
    )
    gbr_hand = Pipeline(
        [
            ("cols", ColumnTransformer([("num", "passthrough", HAND_FEATURES)])),
            (
                "gbr",
                GradientBoostingRegressor(
                    n_estimators=200, max_depth=3, learning_rate=0.05, random_state=seed
                ),
            ),
        ]
    )
    return {
        "length_only": length_only,
        "ridge_hand_tfidf": ridge_hand_tfidf,
        "gbr_hand": gbr_hand,
    }


def residual_table(samples_df: pd.DataFrame, n_bins: int = 5) -> pd.DataFrame:
    """Error by true-rating quantile bin: n, mean |pred - true|, mean (pred - true)."""
    df = samples_df.copy()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    df["bin"] = pd.cut(df.rating_quantile, edges, include_lowest=True)
    err = df.y_pred - df.y_true
    out = pd.DataFrame(
        {
            "n": df.groupby("bin", observed=False).size(),
            "mean_abs_err": err.abs().groupby(df.bin, observed=False).mean(),
            "mean_signed_err": err.groupby(df.bin, observed=False).mean(),
        }
    )
    out.index = out.index.astype(str)
    return out


def worst_examples(samples_df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    """The k items with the largest |pred - true|, largest first."""
    df = samples_df.assign(abs_err=(samples_df.y_pred - samples_df.y_true).abs())
    return df.sort_values("abs_err", ascending=False).head(k)
