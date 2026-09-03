from pathlib import Path

import pytest
from tasks.mmlupro import load_model_outputs
from tasks.mmlupro_extract import (
    category_accuracy,
    extract_lenient,
    extract_strict,
    score_extractors,
)

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Blah blah. The answer is (C).", "C"),
        ("the answer is B", "B"),
        ("Answer: (J)", "J"),
        ("The answer is (A). Later: the answer is (D).", "A"),  # first match wins (official scorer)
        ("ANSWER IS (e)", "E"),  # case-insensitive, upper-cased result
        ("So it must be C.", None),  # strict miss
        ("no letters here", None),
        ("answer is (K)", None),  # outside A-J
    ],
)
def test_extract_strict(text, expected):
    assert extract_strict(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("So it must be C.", "C"),  # strict miss, lenient hit
        ("I choose (B) over (A)", "A"),  # last standalone letter
        ("no letters here", None),
        ("The Big Answer", None),  # letters inside words must not match
        ("the answer is b", None),  # lowercase does not count
        ("Answer: (J).", "J"),
        ("", None),
    ],
)
def test_extract_lenient(text, expected):
    assert extract_lenient(text) == expected


def test_score_extractors_on_fixtures():
    out = load_model_outputs(FIX / "mmlupro")
    s = score_extractors(out).set_index("model")
    assert list(s.columns) == [
        "n",
        "acc_pred",
        "acc_strict",
        "acc_lenient",
        "agree_strict_pred",
        "agree_lenient_pred",
        "format_fail",
        "runaway",
    ]
    # modelA cots: "The answer is (A).", "answer is (B)", "So the answer is C", "I think A",
    #              "B is best", "Answer: (C)"  (answers A,B,C,D,A,A; preds A,B,C,A,B,C)
    a = s.loc["modelA"]
    assert a["n"] == 6
    assert a["acc_pred"] == pytest.approx(3 / 6)
    assert a["acc_strict"] == pytest.approx(3 / 6)  # strict: A,B,C,None,None,C
    assert a["acc_lenient"] == pytest.approx(3 / 6)  # lenient: A,B,C,A,B,C
    assert a["agree_strict_pred"] == pytest.approx(4 / 6)  # None != pred counts as disagreement
    assert a["agree_lenient_pred"] == pytest.approx(6 / 6)
    assert a["format_fail"] == pytest.approx(2 / 6)
    assert a["runaway"] == pytest.approx(0.0)
    # modelB cots all "The answer is (X)." except q4 "no format here"; preds A,A,C,B,B; answers A,B,C,D,A
    b = s.loc["modelB"]
    assert b["format_fail"] == pytest.approx(1 / 5)
    assert b["acc_strict"] == pytest.approx(2 / 5)
    assert b["agree_lenient_pred"] == pytest.approx(4 / 5)


def test_runaway_counts_first_last_disagreement():
    from tasks.mmlupro import load_model_outputs

    out = load_model_outputs(FIX / "mmlupro")
    out = out[out["model"] == "modelB"].copy()
    out.loc[out.index[0], "cot"] = "The answer is (A). Next question... The answer is (C)."
    s = score_extractors(out).set_index("model").loc["modelB"]
    assert s["runaway"] == pytest.approx(1 / 5)
    assert s["acc_strict"] == pytest.approx(2 / 5)  # first match (A) is still correct


def test_category_accuracy_wilson():
    out = load_model_outputs(FIX / "mmlupro")
    c = category_accuracy(out)
    assert list(c.columns) == ["category", "model", "n", "acc", "lo", "hi"]
    row = c.set_index(["category", "model"]).loc[("math", "modelA")]
    # modelA math: q1 ok, q2 ok, q6 wrong
    assert row["n"] == 3
    assert row["acc"] == pytest.approx(2 / 3)
    assert row["lo"] == pytest.approx(0.2077, abs=1e-3)
    assert row["hi"] == pytest.approx(0.9385, abs=1e-3)
    assert c.set_index(["category", "model"]).loc[("law", "modelB"), "n"] == 3
