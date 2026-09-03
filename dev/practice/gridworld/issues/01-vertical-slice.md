# 01: Gridworld env, level generator, Q-learning agent, random-curriculum baseline

## Goal
Thin vertical slice: an NxN gridworld with walls, a seeded level generator with difficulty knobs,
BFS solvability + shortest-path length, a tabular epsilon-greedy Q-learning agent, and a training
script that trains on randomly sampled levels from a pool and periodically evaluates on a fixed
held-out set of 30 hard levels (size 9, long shortest path). The artifact is a printed markdown
table of held-out solve rate vs training steps written to `runs/<id>/summary.json`.

## Acceptance criteria
- [ ] `uv run pytest tests/test_gridworld.py` passes and asserts:
  - env dynamics: moving into a wall or off-grid leaves the position unchanged; reaching the goal
    returns `done=True` and the goal reward; every non-goal step returns the step penalty; the
    episode ends with `done=True` after `max_steps` steps.
  - `make_level(level_id, size, wall_density, min_dist)` is deterministic: same args give equal
    grids/start/goal; different ids give different grids for at least one of 5 ids.
  - every generated level is solvable per `bfs_shortest_path` and its start-goal manhattan
    distance >= `min_dist`; BFS returns `None` on an unsolvable hand-made grid and the correct
    length on a hand-made open grid.
  - `QAgent` trained for a small budget on a single tiny level (size 5, no walls) solves it greedily.
- [ ] `uv run python scripts/gridworld_train.py --limit 2` finishes in < 30 s, creates
  `runs/gridworld_random__*/` with `config.json`, `samples.jsonl` (one row per eval checkpoint:
  `id`, `steps`, `solve_rate`, `per_level` list) and `summary.json`, and prints a markdown table
  (steps x solve_rate) via `magic.results.to_markdown`.
- [ ] `--limit N` caps the number of eval checkpoints (and thus training steps) so the smoke run is fast.
- [ ] `make lint && make test` pass.

## Out of scope
- easy-to-hard and PLR curricula (issue 02); plots, CIs, report (issue 03).
- Any non-tabular agent; any dependency beyond numpy/pandas.

## Files expected to change
- tasks/gridworld.py (new), tasks/__init__.py (new, empty)
- scripts/gridworld_train.py (new)
- tests/test_gridworld.py (new)
- pyproject.toml: add `pythonpath = ["."]` under `[tool.pytest]` so tests can import `tasks.*` (the scaffold has no such entry yet)

## Depends on
none
