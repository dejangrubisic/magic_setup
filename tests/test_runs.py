import re
import sys

import pytest

from magic.runs import RunDir


def test_new_creates_timestamped_dir(tmp_path):
    run = RunDir.new(root=tmp_path, name="mmlu__sonnet")
    assert run.path.is_dir()
    assert re.fullmatch(r"mmlu__sonnet__\d{8}-\d{6}__[0-9a-f]{6}", run.path.name)
    assert RunDir.new(root=tmp_path, name="mmlu__sonnet").path != run.path


def test_config_records_python_and_git(tmp_path):
    run = RunDir.new(root=tmp_path, name="r")
    run.write_config({"model": "claude-sonnet-5", "n": 10})
    cfg = run.config()
    assert cfg["model"] == "claude-sonnet-5"
    assert cfg["python"] == ".".join(str(x) for x in sys.version_info[:3])
    assert "git_sha" in cfg


def test_append_done_ids_and_resume(tmp_path):
    run = RunDir.new(root=tmp_path, name="r")
    assert run.done_ids() == set()
    for i in range(3):
        run.append({"id": f"q{i}", "score": i})
    assert run.done_ids() == {"q0", "q1", "q2"}

    reopened = RunDir(run.path)
    assert reopened.done_ids() == {"q0", "q1", "q2"}
    todo = [i for i in ["q1", "q2", "q3"] if i not in reopened.done_ids()]
    assert todo == ["q3"]
    reopened.append({"id": "q3", "score": 9})
    assert [s["id"] for s in run.samples()] == ["q0", "q1", "q2", "q3"]


def test_append_requires_id(tmp_path):
    run = RunDir.new(root=tmp_path, name="r")
    with pytest.raises(ValueError, match="id"):
        run.append({"score": 1})
    assert run.samples() == []


def test_summary_is_the_completion_marker(tmp_path):
    run = RunDir.new(root=tmp_path, name="r")
    assert run.summary() is None
    assert run.config() is None
    run.write_summary({"accuracy": 0.75, "n": 4})
    assert RunDir(run.path).summary() == {"accuracy": 0.75, "n": 4}
