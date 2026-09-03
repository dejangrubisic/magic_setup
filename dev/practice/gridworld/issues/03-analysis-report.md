# 03: Analysis: learning curves with CIs, final table, failure analysis, REPORT

## Goal
Run all three curricula for 5 seeds, aggregate the runs, and produce: (a) a learning-curve figure
(held-out solve rate vs steps, mean with bootstrap CI over seeds, one line per curriculum), (b) a
final table (curriculum x final solve rate with bootstrap CI over seeds, plus mean AUC), (c) a
failure analysis of held-out levels never solved by any seed of a curriculum and what they have in
common (path length, wall density, size). Artifact: `dev/practice/gridworld/REPORT.md` with the
tables and figure, and a dated `dev/LOG.md` entry.

## Acceptance criteria
- [ ] `scripts/gridworld_analyze.py --runs runs` reads all `runs/gridworld_*` dirs via
  `magic.results.load_runs`, writes `runs/analysis_gridworld/curves.png`, `final_table.md`,
  `never_solved.md`, and prints the final table. `--limit N` restricts to the first N run dirs.
- [ ] `uv run pytest tests/test_gridworld_analyze.py` passes on a tiny fixture of two fake run
  dirs (created in tmp_path) and asserts: the final table has one row per curriculum, CIs bracket
  the point estimate, and the never-solved list contains exactly the level ids with solve 0 in
  every checkpoint of every seed.
- [ ] `dev/practice/gridworld/REPORT.md` contains the final table, the curves figure path, the
  never-solved analysis, and 3-5 findings. `dev/LOG.md` has a dated entry with the table.
- [ ] Total runtime of 15 training runs + analysis < 10 min on a laptop CPU (record the actual time
  in REPORT.md).
- [ ] `make lint && make test` pass.

## Out of scope
- New curricula, env changes, hyper-parameter search.

## Files expected to change
- scripts/gridworld_analyze.py (new), tests/test_gridworld_analyze.py (new)
- dev/practice/gridworld/REPORT.md (new), dev/LOG.md (append)
- runs/ is gitignored except the figure copied to dev/practice/gridworld/curves.png

## Depends on
#02
