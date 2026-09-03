import json

import pytest

from magic.io import ensure_dir, iter_jsonl, read_jsonl, write_jsonl

ROWS = [{"id": "a", "score": 1}, {"id": "b", "score": 0}]


def test_write_then_read_roundtrip(tmp_path):
    path = write_jsonl(tmp_path / "nested" / "dir" / "out.jsonl", ROWS)
    assert path.exists()
    assert read_jsonl(path) == ROWS


def test_append_extends_and_overwrite_truncates(tmp_path):
    path = tmp_path / "out.jsonl"
    write_jsonl(path, ROWS)
    write_jsonl(path, [{"id": "c", "score": 1}], append=True)
    assert [r["id"] for r in read_jsonl(path)] == ["a", "b", "c"]
    write_jsonl(path, [{"id": "z"}])
    assert read_jsonl(path) == [{"id": "z"}]


def test_blank_lines_skipped_and_iter_is_lazy(tmp_path):
    path = tmp_path / "gappy.jsonl"
    path.write_text('{"id": "a"}\n\n   \n{"id": "b"}\n', encoding="utf-8")
    assert read_jsonl(path) == [{"id": "a"}, {"id": "b"}]
    stream = iter_jsonl(path)
    assert next(stream) == {"id": "a"}
    stream.close()


def test_non_json_values_are_stringified(tmp_path):
    path = write_jsonl(tmp_path / "obj.jsonl", [{"id": "a", "when": {1, 2}}])
    assert isinstance(json.loads(path.read_text())["when"], str)


def test_ensure_dir_is_idempotent(tmp_path):
    d = ensure_dir(tmp_path / "a" / "b")
    assert d.is_dir()
    assert ensure_dir(d) == d


def test_read_jsonl_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_jsonl(tmp_path / "nope.jsonl")


def test_nan_and_inf_become_null_in_jsonl(tmp_path):
    import json
    import math

    import numpy as np

    from magic.io import nan_to_none, read_jsonl, write_jsonl

    p = write_jsonl(tmp_path / "x.jsonl", [{"a": float("nan"), "b": [1.0, math.inf], "c": np.nan}])
    text = p.read_text()
    assert "NaN" not in text
    assert "Infinity" not in text
    assert read_jsonl(p) == [{"a": None, "b": [1.0, None], "c": None}]
    assert json.loads(json.dumps(nan_to_none({"k": (float("nan"), "s")}))) == {"k": [None, "s"]}
