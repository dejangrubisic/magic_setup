import json

import numpy as np
from scripts.gridworld_train import main as train_main
from tasks.gridworld import Easy2Hard, PLRLite, RandomCurriculum, make_pool


def test_random_curriculum_covers_pool():
    pool = make_pool(20, seed=5)
    cur = RandomCurriculum(pool, seed=0)
    seen = {cur.sample().id for _ in range(2000)}
    assert seen == {lvl.id for lvl in pool}


def test_easy2hard_path_length_increases():
    pool = make_pool(100, seed=5)
    cur = Easy2Hard(pool, total_steps=1000, seed=0)
    lengths = []
    for _ in range(100):
        lvl = cur.sample()
        lengths.append(lvl.path_len)
        cur.update(lvl, False, 0.0, steps_used=10)
    assert np.mean(lengths[:10]) < np.mean(lengths[-10:])
    assert max(lengths[:10]) < max(lvl.path_len for lvl in pool)


def test_plr_buffer_bounded_and_prioritised():
    pool = make_pool(30, seed=5)
    cur = PLRLite(pool, seed=0, buffer_size=5, p_replay=1.0)
    for i, lvl in enumerate(pool):
        cur.update(lvl, solved=False, td_error=float(i), steps_used=1)
    assert len(cur.buffer) == 5
    kept = {k: v[1] for k, v in cur.buffer.items()}
    assert kept == {pool[i].id: float(i) for i in range(25, 30)}
    draws = [cur.sample().id for _ in range(1000)]
    assert draws.count(pool[29].id) > draws.count(pool[25].id)
    assert set(draws) <= set(kept)


def test_plr_without_replay_samples_pool():
    pool = make_pool(30, seed=5)
    cur = PLRLite(pool, seed=0, buffer_size=5, p_replay=0.0)
    cur.update(pool[0], solved=False, td_error=9.0, steps_used=1)
    draws = [cur.sample().id for _ in range(300)]
    assert set(draws) == {lvl.id for lvl in pool}  # uniform over the pool, not the buffer
    assert draws.count(pool[0].id) < 40
    cur = PLRLite(pool, seed=0, score="unsolved")
    cur.update(pool[1], solved=True, td_error=9.0, steps_used=1)
    assert cur.buffer[pool[1].id][1] == 0.0


def _run(tmp_path, *args):
    return train_main(["--limit", "1", "--steps-per-ckpt", "500", "--runs", str(tmp_path), *args])


def _rows(run):
    return [json.loads(line) for line in (run / "samples.jsonl").read_text().splitlines()]


def test_train_script_records_curriculum_seed_and_is_deterministic(tmp_path):
    a = _run(tmp_path, "--curriculum", "plr", "--seed", "3")
    b = _run(tmp_path, "--curriculum", "plr", "--seed", "3")
    c = _run(tmp_path, "--curriculum", "plr", "--seed", "4")
    cfg = json.loads((a / "config.json").read_text())
    assert cfg["curriculum"] == "plr"
    assert cfg["seed"] == 3
    assert json.loads((c / "config.json").read_text())["seed"] == 4
    assert _rows(a) == _rows(b)  # full rows: steps, solve_rate and per_level all match
    assert len(_rows(a)) == 2
    assert [r["steps"] for r in _rows(a)] != [
        r["steps"] for r in _rows(c)
    ]  # seed changes the trajectory
    e2h = _run(tmp_path, "--curriculum", "easy2hard")
    assert json.loads((e2h / "config.json").read_text())["curriculum"] == "easy2hard"
    assert e2h.name.startswith("gridworld_easy2hard__")
