"""Issue 02: three models, residual table, worst examples, residuals script."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tasks.easy2hard import (  # noqa: E402
    build_models,
    feature_frame,
    residual_table,
    worst_examples,
)

FIXTURE = ROOT / "tests" / "fixtures" / "easy2hard_tiny.jsonl"


def _samples() -> pd.DataFrame:
    q = np.linspace(0.05, 0.95, 10)
    return pd.DataFrame(
        {
            "item_id": [f"i{k}" for k in range(10)],
            "y_true": np.zeros(10),
            "y_pred": [0.1, -0.1, 0.2, 0.2, 0.3, -0.3, 0.0, 0.4, -0.5, 0.5],
            "rating_quantile": q,
        }
    )


def test_build_models_has_three_fittable_models():
    rows = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
    df = feature_frame(rows)
    models = build_models(seed=0)
    assert set(models) == {"length_only", "ridge_hand_tfidf", "gbr_hand"}
    for m in models.values():
        pred = m.fit(df, df.rating).predict(df)
        assert pred.shape == (len(df),)
        assert np.isfinite(pred).all()


def test_residual_table_values():
    t = residual_table(_samples(), n_bins=5)
    assert list(t.columns) == ["n", "mean_abs_err", "mean_signed_err"]
    assert len(t) == 5
    assert t.n.tolist() == [2, 2, 2, 2, 2]
    assert t.mean_abs_err.tolist() == pytest.approx([0.1, 0.2, 0.3, 0.2, 0.5])
    assert t.mean_signed_err.tolist() == pytest.approx([0.0, 0.2, 0.0, 0.2, 0.0])


def test_worst_examples_sorted_and_k():
    w = worst_examples(_samples(), k=3)
    assert len(w) == 3
    assert w.item_id.tolist() == ["i8", "i9", "i7"]
    assert w.abs_err.tolist() == pytest.approx([0.5, 0.5, 0.4])


def test_predict_and_residual_scripts(tmp_path):
    common = {"capture_output": True, "text": True, "check": True, "cwd": ROOT}
    out = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "easy2hard_predict.py"),
            "--data",
            str(FIXTURE),
            "--runs",
            str(tmp_path),
        ],
        **common,
    )
    for name in ("length_only", "ridge_hand_tfidf", "gbr_hand"):
        assert name in out.stdout
    run_dir = next(tmp_path.glob("easy2hard_predict__*"))
    samples = [json.loads(line) for line in (run_dir / "samples.jsonl").read_text().splitlines()]
    n_test = json.loads((run_dir / "config.json").read_text())["n_test"]
    assert len(samples) == 3 * n_test
    assert {"id", "model", "y_true", "y_pred", "rating_quantile"} <= set(samples[0])

    out = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "easy2hard_residuals.py"),
            "--run",
            str(run_dir),
            "--k",
            "3",
        ],
        **common,
    )
    assert "mean_signed_err" in out.stdout
    assert "worst test items" in out.stdout
    assert out.stdout.count("gsm8k-") == 3
