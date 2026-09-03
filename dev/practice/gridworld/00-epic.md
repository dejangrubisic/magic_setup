# Epic: gridworld curriculum RL (practice run 5)

Goal: on a procedurally generated gridworld, compare three level curricula (random, easy-to-hard by
shortest path, PLR-lite) for a tabular Q-learning agent with a fixed env-step budget. Metric: solve
rate on a fixed held-out set of 30 hard 9x9 levels vs training steps, 5 seeds, bootstrap CIs.
Deliverable: dev/practice/gridworld/REPORT.md with tables, learning curves and failure analysis.

Constraints: numpy only, no model calls, < 10 min total runtime on a laptop CPU.

| # | Title | Depends on | Files | AC (one line) |
|---|-------|-----------|-------|---------------|
| 01 | Env + levels + Q-learning + random-curriculum baseline (vertical slice) | none | tasks/gridworld.py, scripts/gridworld_train.py, tests/test_gridworld.py | `scripts/gridworld_train.py --limit 2` prints a solve-rate table on held-out levels |
| 02 | Curricula: easy-to-hard and PLR-lite | 01 | tasks/gridworld.py, scripts/gridworld_train.py, tests/test_gridworld_curricula.py | `--curriculum {random,easy2hard,plr}` runs; each writes a runs/ dir with learning curve |
| 03 | Analysis: curves with CIs, final table, failure analysis, REPORT | 02 | scripts/gridworld_analyze.py, dev/practice/gridworld/REPORT.md, dev/LOG.md, tests/test_gridworld_analyze.py | REPORT.md has final table with CIs, curve figure, never-solved level analysis |

Waves: 01 -> 02 -> 03 (sequential; each depends on the previous).
