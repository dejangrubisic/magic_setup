from magic.tasks.example import extract_lenient, extract_strict, load_rows, score


def test_strict_extractor_reads_answer_is_pattern():
    assert extract_strict("Thinking... The answer is (C). Done") == "C"
    assert extract_strict("no explicit answer here") is None


def test_lenient_extractor_takes_last_standalone_letter():
    assert extract_lenient("Could be A or maybe B") == "B"
    assert extract_lenient("nothing") is None


def test_score_is_case_insensitive_and_none_is_zero():
    assert score("c", "C") == 1.0
    assert score("A", "C") == 0.0
    assert score(None, "C") == 0.0


def test_load_rows_limit(tmp_path):
    p = tmp_path / "rows.jsonl"
    p.write_text('{"id": "a"}\n{"id": "b"}\n{"id": "c"}\n')
    assert [r["id"] for r in load_rows(str(p), limit=2)] == ["a", "b"]
    assert len(load_rows(str(p))) == 3


def test_strict_last_and_runaway_flag():
    from magic.tasks.example import extract_strict, runaway

    text = "The answer is (A). Wait, actually the answer is (C)."
    assert extract_strict(text) == "A"
    assert extract_strict(text, first=False) == "C"
    assert runaway(text) is True
    assert runaway("The answer is (B).") is False


def test_example_stage_writes_a_resumable_run(tmp_path, capsys, monkeypatch):
    """The pattern every stage script copies: run main() on the fixture into tmp_path."""
    import json
    import runpy
    import sys

    argv = [
        "x",
        "--data",
        "tests/fixtures/example.jsonl",
        "--limit",
        "2",
        "--runs-root",
        str(tmp_path),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    runpy.run_path("scripts/example_stage.py", run_name="__main__")
    run = next(tmp_path.glob("example__*"))
    assert {p.name for p in run.iterdir()} == {"config.json", "samples.jsonl", "summary.json"}
    assert json.loads((run / "summary.json").read_text())["n"] == 2
    assert "ALL" in capsys.readouterr().out
