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
