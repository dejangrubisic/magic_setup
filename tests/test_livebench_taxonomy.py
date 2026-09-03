"""Issue 03: failure taxonomy classes and strict/lenient agreement."""

import pandas as pd
import pytest
from tasks.livebench_taxonomy import CLASSES, agreement, bottom_quartile_items, classify


@pytest.mark.parametrize(
    ("text", "gt", "task", "expected"),
    [
        ("so ***goldfish***.", "goldfish", "zebra_puzzle", "correct"),
        ("so ***cat***.", "goldfish", "zebra_puzzle", "wrong_answer"),
        ("so **goldfish**.", "goldfish", "zebra_puzzle", "format_failure"),
        ("Let me think. The person at position 2 has a", "goldfish", "zebra_puzzle", "truncation"),
        ("", "goldfish", "zebra_puzzle", "truncation"),
        ("**4**", "4", "spatial", "correct"),
        ("**5**", "4", "spatial", "wrong_answer"),
        ("I think 5 pieces.", "4", "spatial", "format_failure"),
        ("I cannot determine the number of pieces.", "4", "spatial", "no_answer"),
        ("I cannot determine the number of pieces", "4", "spatial", "truncation"),
        ("**yes, no**", "yes, no, yes", "web_of_lies_v2", "wrong_answer"),
        ("So the answer is: no, yes, yes.", "yes, no, yes", "web_of_lies_v2", "format_failure"),
        ("Nobody tells the truth here.", "yes, no, yes", "web_of_lies_v2", "no_answer"),
    ],
)
def test_classify(text, gt, task, expected):
    assert expected in CLASSES
    assert classify(text, gt, task) == expected


def test_agreement_counts():
    df = pd.DataFrame({"strict": [1.0, 0.0, 0.0, 0.0], "lenient": [1.0, 1.0, 0.0, 0.5]})
    out = agreement(df)
    assert out == {
        "n": 4,
        "exact_agree": 0.5,
        "strict_mean": 0.25,
        "lenient_mean": 0.625,
        "lenient_rescues": 2,
    }


def test_bottom_quartile_items():
    df = pd.DataFrame(
        {
            "question_id": ["a", "a", "b", "b", "c", "c", "d", "d"],
            "strict": [0, 0, 1, 1, 1, 0, 1, 1],
        }
    )
    assert bottom_quartile_items(df) == ["a"]
