"""Issue 01: loading, extraction, scoring and the score matrix on tiny fixtures."""

from pathlib import Path

import pandas as pd
import pytest
from tasks.livebench import extract_answer, load_reasoning, score_answer, score_matrix, score_rows

from magic import read_jsonl

FX = Path(__file__).parent / "fixtures"


@pytest.fixture
def frame() -> pd.DataFrame:
    answers = pd.DataFrame(read_jsonl(FX / "livebench_answers.jsonl"))
    questions = pd.DataFrame(read_jsonl(FX / "livebench_reasoning.jsonl"))
    return load_reasoning(FX, answers=answers, questions=questions)


def test_load_reasoning_joins_and_filters(frame):
    assert list(frame.columns) == ["question_id", "task", "model", "answer", "ground_truth"]
    assert (
        len(frame) == 12
    )  # 3 questions x 4 models; math, no-ground-truth and duplicate rows dropped
    assert not frame.duplicated(["model", "question_id"]).any()
    assert "stale duplicate" not in " ".join(frame["answer"])  # the older tstamp loses
    assert "no-gt" not in set(frame["question_id"])
    assert frame["model"].nunique() == 4
    assert set(frame["task"]) == {"spatial", "web_of_lies_v2", "zebra_puzzle"}
    assert frame["answer"].str.len().min() > 0


@pytest.mark.parametrize(
    ("text", "task", "strict", "lenient"),
    [
        ("so **4** pieces. Answer **5**", "spatial", "5", "5"),
        ("I think it is 4 pieces.\nSo 4.", "spatial", None, "4"),
        ("it is **four** pieces", "spatial", None, "four"),
        ("it is many pieces.", "spatial", None, None),
        ("nobody lies.", "web_of_lies_v2", None, None),
        ("**yes, no, yes**.", "web_of_lies_v2", "yes, no, yes", "yes, no, yes"),
        ("**Answer: no, no, no**", "web_of_lies_v2", None, "no, no, no"),
        (
            "- Q1? **No**\n- Q2? **Yes**\n\n**Final Answer: **no, yes, yes**",
            "web_of_lies_v2",
            None,
            "no, yes, yes",
        ),
        ("Q1? **Yes**. That is all.", "web_of_lies_v2", None, "Yes"),
        ("The answers are yes, yes, no.", "web_of_lies_v2", None, "yes, yes, no"),
        (
            "**bold** answers:\n**Yes, Yes, Yes**",
            "web_of_lies_v2",
            "Yes, Yes, Yes",
            "Yes, Yes, Yes",
        ),
        ("thus ***goldfish***.", "zebra_puzzle", "goldfish", "goldfish"),
        ("thus **goldfish**.", "zebra_puzzle", None, "goldfish"),
        ("The person has a goldfish.", "zebra_puzzle", None, "The person has a goldfish."),
        ("", "spatial", None, None),
        ("", "zebra_puzzle", None, None),
    ],
)
def test_extract_answer(text, task, strict, lenient):
    assert extract_answer(text, task, "strict") == strict
    assert extract_answer(text, task, "lenient") == lenient


def test_extract_answer_rejects_bad_args():
    with pytest.raises(ValueError, match="mode"):
        extract_answer("x", "spatial", "fuzzy")
    with pytest.raises(ValueError, match="task"):
        extract_answer("x", "math", "strict")


def test_score_answer():
    assert score_answer("**4**", "4", "spatial") == 1.0
    assert score_answer("**5**", "4", "spatial") == 0.0
    assert score_answer("so 4.", "4", "spatial", "strict") == 0.0
    assert score_answer("so 4.", "4", "spatial", "lenient") == 1.0
    assert score_answer("**Yes, No, YES**", "yes, no, yes", "web_of_lies_v2") == 1.0
    assert score_answer("**yes, no**", "yes, no, yes", "web_of_lies_v2") == 0.0
    assert score_answer("***Goldfish***", "goldfish", "zebra_puzzle") == 1.0
    assert score_answer("***1, a, x, y***", "1, a, b, c", "zebra_puzzle") == 0.5
    assert score_answer("***1, a***", "1, a, b, c", "zebra_puzzle") == 0.0
    assert score_answer("", "goldfish", "zebra_puzzle", "lenient") == 0.0


def test_score_rows_and_matrix(frame):
    strict = score_rows(frame, "strict")
    lenient = score_rows(frame, "lenient")
    assert strict.between(0, 1).all()
    assert (lenient >= strict).all()  # lenient only ever rescues
    m = score_matrix(frame, "strict")
    assert m.shape == (4, 3)
    assert m.notna().all().all()
    assert m.to_numpy().sum() == strict.sum()
    sparse = score_matrix(frame.iloc[1:], "strict")
    assert sparse.isna().sum().sum() == 1


def test_per_task_table_on_fixture(frame):
    from scripts.livebench_baseline import per_task_table

    df = frame.assign(strict=score_rows(frame, "strict"))
    table = per_task_table(df, top=2)
    assert len(table) == 2
    assert list(table.columns) == ["overall", "spatial", "web_of_lies_v2", "zebra_puzzle"]
    best = df.groupby("model")["strict"].mean().idxmax()
    assert table.index[0] == best
    assert table.loc[best, "spatial"].endswith("n=1")
    assert table.loc[best, "overall"].startswith(
        f"{df.groupby('model')['strict'].mean().max():.3f}"
    )
