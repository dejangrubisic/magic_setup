"""Issue 01: hand features, stable split, Spearman CI, and the predict script end to end."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tasks.easy2hard import feature_frame, hand_features, spearman_ci  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "easy2hard_tiny.jsonl"


def test_hand_features_exact_values():
    row = {
        "question": "Tom has 3 apples and buys 12 more for $1.50 each. How many apples? He is happy!",
        "answer": "3+12=<<3+12=15>>15\n\n#### 15",
    }
    assert hand_features(row) == {
        "q_len_chars": len(row["question"]),
        "q_len_words": 17,
        "n_numbers": 3,
        "n_operators": 0,
        "n_sentences": 3,
        "answer_magnitude": pytest.approx(1.2041199826559248),
        "sol_len_lines": 2,
    }


def test_hand_features_missing_final_answer_is_zero_magnitude():
    assert hand_features({"question": "x", "answer": "no marker"})["answer_magnitude"] == 0.0


def test_spearman_ci_monotone_is_one():
    rho, lo, hi = spearman_ci([1, 2, 3, 4, 5, 6], [10, 20, 30, 40, 50, 60], seed=1)
    assert rho == 1.0
    assert lo <= rho <= hi


def test_spearman_ci_reversed_is_minus_one():
    rho, _, _ = spearman_ci([1, 2, 3, 4], [4, 3, 2, 1])
    assert rho == -1.0


def test_split_is_stable_per_id():
    rows = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
    a = feature_frame(rows).set_index("id").split
    b = feature_frame(list(reversed(rows))[:30]).set_index("id").split
    assert set(a.unique()) <= {"train", "test"}
    assert (a.loc[b.index] == b).all()


def test_predict_script_writes_run_and_prints_table(tmp_path):
    out = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "easy2hard_predict.py"),
            "--data",
            str(FIXTURE),
            "--limit",
            "50",
            "--runs",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    assert "length_only" in out.stdout
    for col in ("spearman", "lo", "hi", "n_test"):
        assert col in out.stdout
    runs = list(tmp_path.glob("easy2hard_predict__*"))
    assert len(runs) == 1
    for f in ("config.json", "samples.jsonl", "summary.json"):
        assert (runs[0] / f).exists()
    summary = json.loads((runs[0] / "summary.json").read_text())
    res = summary["results"][0]
    assert res["model"] == "length_only"
    assert -1 <= res["lo"] <= res["spearman"] <= res["hi"] <= 1
    assert res["n_test"] == json.loads((runs[0] / "config.json").read_text())["n_test"]
