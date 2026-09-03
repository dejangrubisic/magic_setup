from pathlib import Path

import pandas as pd
import pytest
from tasks.mmlupro import load_model_outputs, load_questions
from tasks.mmlupro_errors import all_fail_items, distractor_distribution, label_error_flags

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def questions():
    return load_questions(FIX / "mmlupro_questions.jsonl")


@pytest.fixture
def outputs(questions):
    return load_model_outputs(FIX / "mmlupro", questions)


def test_distractor_distribution(outputs):
    d = distractor_distribution(outputs)
    # wrong rows: modelA q4 (ans D idx3, pred A idx0), q5 (ans A idx0, pred B idx1), q6 (ans A, pred C idx2)
    #             modelB q2 (ans B idx1, pred A idx0), q4 (ans D idx3, pred B idx1), q5 (ans A idx0, pred B idx1)
    # law: q4 x2, q5 x2 -> preds A,B,B,B ; adjacent: q5 twice (|0-1|=1) -> 2/4
    #             modelC (re-keyed to q1..q3): q2 (ans B idx1, pred C idx2)
    # math: q6 (C), q2 (A), q2 (C) -> adjacent: q2/A (|0-1|), q2/C (|2-1|) -> 2/3
    assert list(d.index) == ["law", "math"]
    assert d.loc["law", "n_wrong"] == 4
    assert d.loc["law", "share_adjacent"] == pytest.approx(0.5)
    assert d.loc["law", "A"] == pytest.approx(0.25)
    assert d.loc["law", "B"] == pytest.approx(0.75)
    assert d.loc["law", "C"] == pytest.approx(0.0)
    assert d.loc["math", "n_wrong"] == 3
    assert d.loc["math", "share_adjacent"] == pytest.approx(2 / 3)
    assert d.loc["math", "C"] == pytest.approx(2 / 3)
    assert d.loc["math", "share_pred_none"] == pytest.approx(0.0)
    assert list(d.columns[:3]) == ["n_wrong", "share_pred_none", "share_adjacent"]
    assert list(d.columns[3:]) == list("ABCDEFGHIJ")


def test_distractor_distribution_counts_none_preds(outputs):
    out = outputs.copy()
    out.loc[(out["model"] == "modelA") & (out["question_id"] == 4), "pred"] = None
    d = distractor_distribution(out)
    assert d.loc["law", "n_wrong"] == 4
    assert d.loc["law", "share_pred_none"] == pytest.approx(0.25)


def test_distractor_distribution_empty_when_nothing_is_wrong(outputs):
    d = distractor_distribution(outputs[outputs["correct"]])
    assert len(d) == 0
    assert list(d.columns) == ["n_wrong", "share_pred_none", "share_adjacent", *"ABCDEFGHIJ"]


def test_all_fail_items(outputs, questions):
    af = all_fail_items(outputs, questions)
    # q4: both wrong (A, B); q5: both wrong (B, B); q6: only modelA has a row and it is wrong
    # modelC covers q1..q3 only, and gets q1 and q3 right
    assert af["question_id"].tolist() == [4, 5, 6]
    assert list(af.columns) == [
        "question_id",
        "category",
        "answer",
        "answer_index",
        "options",
        "n_models",
        "consensus_pred",
        "consensus_share",
    ]
    r = af.set_index("question_id")
    assert r.loc[5, "n_models"] == 2
    assert r.loc[5, "consensus_pred"] == "B"
    assert r.loc[5, "consensus_share"] == pytest.approx(1.0)
    assert r.loc[4, "consensus_share"] == pytest.approx(0.5)
    assert r.loc[6, "n_models"] == 1
    assert r.loc[6, "options"] == ["a", "a", "c", "d"]


def test_label_error_flags():
    base = {
        "answer": "A",
        "answer_index": 0,
        "options": ["x", "y", "z"],
        "n_models": 3,
        "consensus_pred": "B",
        "consensus_share": 0.5,
    }
    f = label_error_flags(pd.Series(base))
    assert f == {
        "dup_option": False,
        "consensus": False,
        "answer_index_mismatch": False,
        "suspect": False,
    }
    dup = label_error_flags(pd.Series({**base, "options": ["x", " X ", "z"]}))
    assert dup["dup_option"] is True
    assert dup["suspect"] is True
    cons = label_error_flags(pd.Series({**base, "consensus_share": 0.8}))
    assert cons["consensus"] is True
    few = label_error_flags(pd.Series({**base, "consensus_share": 1.0, "n_models": 2}))
    assert few["consensus"] is False  # needs >= 3 models
    mism = label_error_flags(pd.Series({**base, "answer_index": 2}))
    assert mism["answer_index_mismatch"] is True
