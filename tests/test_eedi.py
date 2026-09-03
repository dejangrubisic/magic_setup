"""Eedi reshape / split / ranking / MAP@k on tiny real fixtures."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from tasks.eedi import TfidfRanker, add_split, ap_at_k, load_raw, query_text, reshape

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def raw():
    train = pd.read_csv(FIX / "eedi_train.csv")
    misc = pd.read_csv(FIX / "eedi_misconceptions.csv")
    return train, misc


def test_load_raw_reads_both_files(tmp_path):
    (tmp_path / "train.csv").write_text((FIX / "eedi_train.csv").read_text())
    (tmp_path / "misconception_mapping.csv").write_text(
        (FIX / "eedi_misconceptions.csv").read_text()
    )
    train, misc = load_raw(tmp_path)
    assert len(train) == 8
    assert list(misc.columns) == ["MisconceptionId", "MisconceptionName"]


def test_reshape_rows(raw):
    train, _ = raw
    rows = reshape(train)
    cols = [f"Misconception{L}Id" for L in "ABCD"]
    expected = int(train[cols].notna().sum().sum())
    assert len(rows) == expected
    assert list(rows.columns) == [
        "QuestionId",
        "letter",
        "QuestionText",
        "AnswerText",
        "ConstructName",
        "SubjectName",
        "MisconceptionId",
    ]
    correct = train.set_index("QuestionId")["CorrectAnswer"]
    assert all(rows.letter != rows.QuestionId.map(correct))
    # spot check one real row: question 2, answer D has misconception 1073
    r = rows[(rows.QuestionId == 2) & (rows.letter == "D")].iloc[0]
    assert r.MisconceptionId == 1073
    assert r.AnswerText == train.loc[train.QuestionId == 2, "AnswerDText"].iloc[0]
    assert rows.MisconceptionId.dtype.kind == "i"


def test_split_is_by_question(raw):
    train, _ = raw
    rows = add_split(reshape(train), test_pct=50)
    assert set(rows.split) <= {"train", "test"}
    assert (rows.groupby("QuestionId").split.nunique() == 1).all()
    # duplicated rows do not move the assignment
    again = add_split(pd.concat([rows, rows]).drop(columns="split"), test_pct=50)
    assert (
        again.groupby("QuestionId").split.first().equals(rows.groupby("QuestionId").split.first())
    )


def test_map_at_k():
    assert ap_at_k([7, 3, 5], 7) == 1.0
    assert ap_at_k([1, 2, 7], 7) == pytest.approx(1 / 3)
    assert ap_at_k([1, 2, 3], 7) == 0.0
    assert ap_at_k([], 7) == 0.0


def test_query_text_optionally_includes_construct(raw):
    train, _ = raw
    rows = reshape(train).head(1)
    with_c = query_text(rows, use_construct=True).iloc[0]
    without = query_text(rows, use_construct=False).iloc[0]
    assert rows.ConstructName.iloc[0] in with_c
    assert rows.ConstructName.iloc[0] not in without
    assert rows.AnswerText.iloc[0] in without


def test_rank_returns_topk_ids(raw):
    _, misc = raw
    names = misc.set_index("MisconceptionId")["MisconceptionName"]
    ranker = TfidfRanker().fit(names)
    target = names.index[3]
    top = ranker.rank([names.loc[target], "zzz unrelated text"], k=5)
    assert top.shape == (2, 5)
    assert top[0, 0] == target
    assert set(np.unique(top)) <= set(names.index)


def test_reshape_drops_correct_letter_even_if_labelled():
    train = pd.DataFrame(
        {
            "QuestionId": [7],
            "ConstructId": [1],
            "ConstructName": ["c"],
            "SubjectId": [1],
            "SubjectName": ["s"],
            "CorrectAnswer": ["A"],
            "QuestionText": ["q"],
            "AnswerAText": ["a"],
            "AnswerBText": ["b"],
            "AnswerCText": ["c"],
            "AnswerDText": ["d"],
            "MisconceptionAId": [5.0],  # labelled but correct: must be dropped
            "MisconceptionBId": [6.0],
            "MisconceptionCId": [None],
            "MisconceptionDId": [None],
        }
    )
    rows = reshape(train)
    assert list(rows.letter) == ["B"]
    assert list(rows.MisconceptionId) == [6]
