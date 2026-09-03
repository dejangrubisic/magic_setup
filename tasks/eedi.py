"""Eedi misconception retrieval: reshape train.csv, split by question, TF-IDF ranking, MAP@k."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

from magic import stable_split

RAW = Path("data/raw/eedi")
LETTERS = "ABCD"
ROW_COLS = [
    "QuestionId",
    "letter",
    "QuestionText",
    "AnswerText",
    "ConstructName",
    "SubjectName",
    "MisconceptionId",
]


def load_raw(raw_dir: str | Path = RAW) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(train, misconception_mapping) as read from the competition csvs."""
    raw_dir = Path(raw_dir)
    return pd.read_csv(raw_dir / "train.csv"), pd.read_csv(raw_dir / "misconception_mapping.csv")


def reshape(train: pd.DataFrame) -> pd.DataFrame:
    """One row per (question, wrong answer) that has a labelled misconception."""
    rows = []
    for r in train.itertuples(index=False):
        for letter in LETTERS:
            mid = getattr(r, f"Misconception{letter}Id")
            if letter == r.CorrectAnswer or pd.isna(mid):
                continue
            rows.append(
                {
                    "QuestionId": int(r.QuestionId),
                    "letter": letter,
                    "QuestionText": r.QuestionText,
                    "AnswerText": getattr(r, f"Answer{letter}Text"),
                    "ConstructName": r.ConstructName,
                    "SubjectName": r.SubjectName,
                    "MisconceptionId": int(mid),
                }
            )
    return pd.DataFrame(rows, columns=ROW_COLS)


def add_split(rows: pd.DataFrame, test_pct: int = 20, salt: str = "eedi-v1") -> pd.DataFrame:
    """Stable train/test column keyed on QuestionId, so all answers of a question stay together."""
    out = rows.copy()
    out["split"] = [stable_split(str(q), test_pct=test_pct, salt=salt) for q in out.QuestionId]
    return out


def query_text(rows: pd.DataFrame, use_construct: bool = True) -> pd.Series:
    """The retrieval query for each row: [construct +] question + wrong answer."""
    parts = [rows.QuestionText, rows.AnswerText]
    if use_construct:
        parts = [rows.ConstructName, *parts]
    return pd.Series([" ".join(map(str, p)) for p in zip(*parts)], index=rows.index)


def ap_at_k(ranked_ids, true_id) -> float:
    """Average precision with a single relevant item: 1/rank if present in the list, else 0."""
    for i, mid in enumerate(ranked_ids, start=1):
        if mid == true_id:
            return 1.0 / i
    return 0.0


class TfidfRanker:
    """Word (1-2 gram) + char_wb (3-5 gram) TF-IDF cosine ranking over misconception names."""

    def __init__(self) -> None:
        self.word = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.ids: np.ndarray | None = None
        self._names_mat = None

    def fit(self, names: pd.Series, extra_texts: list[str] | None = None) -> TfidfRanker:
        """names: MisconceptionName indexed by MisconceptionId; extra_texts widen the vocabulary."""
        corpus = list(names.astype(str)) + list(extra_texts or [])
        self.word.fit(corpus)
        self.char.fit(corpus)
        self.ids = np.asarray(names.index)
        self._names_mat = self._transform(list(names.astype(str)))
        return self

    def _transform(self, texts: list[str]):
        return hstack([self.word.transform(texts), self.char.transform(texts)]).tocsr()

    def rank(self, queries: list[str], k: int = 25) -> np.ndarray:
        """Top-k misconception ids per query, best first; shape (len(queries), k)."""
        if self.ids is None:
            raise RuntimeError("call fit() first")
        sims = (self._transform(list(queries)) @ self._names_mat.T).toarray()
        # TfidfVectorizer rows are l2-normalised, so the dot product is the cosine similarity.
        top = np.argsort(-sims, axis=1)[:, :k]
        return self.ids[top]
