import math
from pathlib import Path

import pytest
from tasks.mmlupro import correctness_matrix, load_model_outputs, load_questions, model_accuracy

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def questions():
    return load_questions(FIX / "mmlupro_questions.jsonl")


@pytest.fixture
def outputs(questions):
    return load_model_outputs(FIX / "mmlupro", questions)


def test_load_questions_types(questions):
    assert len(questions) == 6
    assert questions["question_id"].dtype.kind == "i"
    assert questions["answer_index"].dtype.kind == "i"
    assert isinstance(questions.loc[0, "options"], list)
    assert list(questions.columns[:1]) == ["question_id"]


def test_load_model_outputs_normalises_and_dedupes(outputs):
    assert set(outputs["model"]) == {"modelA", "modelB", "modelC"}
    assert len(outputs[outputs["model"] == "modelA"]) == 6  # duplicate q1 row dropped
    assert len(outputs[outputs["model"] == "modelB"]) == 5
    assert outputs["question_id"].dtype.kind == "i"
    assert outputs["answer_index"].dtype.kind == "i"
    first_a = outputs[(outputs["model"] == "modelA") & (outputs["question_id"] == 1)]
    assert first_a["pred"].item() == "A"  # first row kept, not the "D" duplicate
    assert first_a["cot"].item() == "The answer is (A)."
    b = outputs[(outputs["model"] == "modelB") & (outputs["question_id"] == 4)]
    assert b["cot"].item() == "no format here"  # generated_text mapped to cot
    assert isinstance(outputs["options"].iloc[0], list)
    assert set(outputs.columns) >= {"model", "question_id", "pred", "answer", "category", "cot"}
    assert not outputs.loc[outputs["model"] != "modelC", "rekeyed"].any()


def test_load_model_outputs_rekeys_shifted_ids_by_text(questions):
    raw = load_model_outputs(FIX / "mmlupro")
    assert raw.loc[raw["model"] == "modelC", "question_id"].tolist() == [100, 101, 102, 103]
    assert not raw["rekeyed"].any()
    assert raw.loc[(raw["model"] == "modelC") & (raw["question_id"] == 103), "pred"].item() is None
    assert (
        raw.loc[(raw["model"] == "modelC") & (raw["question_id"] == 103), "correct"].item() is False
    )
    out = load_model_outputs(FIX / "mmlupro", questions)
    c = out[out["model"] == "modelC"]
    assert c["question_id"].tolist() == [1, 2, 3]  # row 103 (unknown text) dropped
    assert c["rekeyed"].all()
    assert c["correct"].tolist() == [True, False, True]


def test_load_questions_from_parquet(questions, tmp_path):
    p = tmp_path / "q.parquet"
    questions.to_parquet(p)
    again = load_questions(p)
    assert again["question_id"].tolist() == questions["question_id"].tolist()
    assert isinstance(again.loc[0, "options"], list)
    assert again.loc[5, "options"] == ["a", "a", "c", "d"]


def test_correctness_matrix(outputs):
    m = correctness_matrix(outputs)
    assert list(m.columns) == ["modelA", "modelB", "modelC"]
    assert list(m.index) == [1, 2, 3, 4, 5, 6]
    assert m["modelA"].tolist() == [True, True, True, False, False, False]
    assert m.loc[1:5, "modelB"].tolist() == [True, False, True, False, False]
    assert math.isnan(m.loc[6, "modelB"])
    assert m["modelC"].tolist()[:3] == [True, False, True]
    assert math.isnan(m.loc[4, "modelC"])


def test_model_accuracy_wilson(outputs):
    acc = model_accuracy(outputs).set_index("model")
    assert acc.loc["modelA", "n"] == 6
    assert acc.loc["modelA", "acc"] == pytest.approx(0.5)
    assert acc.loc["modelB", "n"] == 5
    assert acc.loc["modelB", "acc"] == pytest.approx(0.4)
    # Wilson bounds for 3/6, z=1.96
    assert acc.loc["modelA", "lo"] == pytest.approx(0.1881, abs=1e-3)
    assert acc.loc["modelA", "hi"] == pytest.approx(0.8119, abs=1e-3)
    assert list(acc.columns) == ["n", "acc", "lo", "hi"]
    assert acc.loc["modelC", "n"] == 3
    assert acc.loc["modelC", "acc"] == pytest.approx(2 / 3)
