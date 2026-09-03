import numpy as np
import pandas as pd
import pytest

from magic.results import by_slice, load_runs, to_markdown
from magic.runs import RunDir

SAMPLES = {
    "a": [("q1", "math", 1.0), ("q2", "math", 0.0), ("q3", "code", 1.0), ("q4", "code", 1.0)],
    "b": [("q1", "math", 1.0), ("q2", "math", 1.0), ("q3", "code", 0.0), ("q4", "code", 1.0)],
}


@pytest.fixture
def runs_root(tmp_path):
    root = tmp_path / "runs"
    for name, rows in SAMPLES.items():
        run = RunDir(root / name)
        for uid, category, score in rows:
            run.append({"id": uid, "score": score, "metadata": {"category": category}})
        run.write_summary({"accuracy": np.mean([r[2] for r in rows]), "n": len(rows)})
    RunDir(root / "unfinished").append({"id": "q9", "score": 0.0})
    return root


def test_load_runs_reads_only_finished_runs(runs_root):
    runs_df, samples_df = load_runs(runs_root)
    assert list(runs_df["run"]) == ["a", "b"]
    assert list(runs_df.columns) == ["run", "accuracy", "n"]
    assert runs_df.set_index("run")["accuracy"].to_dict() == {"a": 0.75, "b": 0.75}
    assert len(samples_df) == 9
    assert set(samples_df["run"]) == {"a", "b", "unfinished"}


def test_nested_metadata_is_flattened(runs_root):
    _, samples_df = load_runs(runs_root)
    assert "metadata.category" in samples_df.columns
    assert samples_df.loc[samples_df["run"] == "a", "metadata.category"].tolist() == [
        "math",
        "math",
        "code",
        "code",
    ]


def test_load_runs_on_an_empty_root(tmp_path):
    runs_df, samples_df = load_runs(tmp_path)
    assert runs_df.empty
    assert samples_df.empty


def test_by_slice_pivot_numbers_are_exact(runs_root):
    _, samples_df = load_runs(runs_root)
    pivot = by_slice(samples_df[samples_df["run"] != "unfinished"], "metadata.category")
    assert list(pivot.columns) == ["a", "b", "n"]
    assert pivot.loc["math", "a"] == 0.5
    assert pivot.loc["math", "b"] == 1.0
    assert pivot.loc["code", "a"] == 1.0
    assert pivot.loc["code", "b"] == 0.5
    assert pivot.loc["ALL", "a"] == 0.75
    assert pivot.loc["ALL", "b"] == 0.75
    assert pivot["n"].to_dict() == {"code": 4, "math": 4, "ALL": 8}


def test_by_slice_handles_a_single_run_and_custom_columns():
    df = pd.DataFrame(
        {
            "run": ["r"] * 3,
            "lang": ["py", "py", "js"],
            "latency": [1.0, 3.0, 10.0],
        }
    )
    pivot = by_slice(df, "lang", value_col="latency")
    assert pivot.loc["py", "r"] == 2.0
    assert pivot.loc["ALL", "r"] == pytest.approx(14 / 3)
    assert pivot.loc["ALL", "n"] == 3


def test_to_markdown_renders_a_table(runs_root):
    _, samples_df = load_runs(runs_root)
    table = to_markdown(
        by_slice(samples_df[samples_df["run"] != "unfinished"], "metadata.category")
    )
    assert "| ALL" in table
    assert "0.500" in table
    assert table.count("\n") == 4
