# 02: Curricula: easy-to-hard and PLR-lite

## Goal
Add two level curricula over the same 500-level training pool and expose them through
`scripts/gridworld_train.py --curriculum {random,easy2hard,plr}`, so that all three can be run
with the same budget, eval schedule and seeds. Artifact: one `runs/gridworld_<curriculum>__*/` per
(curriculum, seed) with the same sample schema as issue 01.

## Acceptance criteria
- [ ] `uv run pytest tests/test_gridworld_curricula.py` passes and asserts:
  - `Easy2Hard` yields levels in non-decreasing shortest-path length over the budget: the mean
    path length of the first 10% of sampled levels is < the mean of the last 10%.
  - `PLRLite` with buffer size B never holds more than B levels; after scoring, the level with the
    highest score is sampled more often than the level with the lowest score (over 1000 draws,
    with the replay probability forced to 1.0); with replay probability 0.0 it always returns a
    fresh random pool level.
  - `RandomCurriculum` draws are uniform over the pool: over 2000 draws every pool level of a pool
    of 20 is drawn at least once.
- [ ] `uv run python scripts/gridworld_train.py --curriculum plr --limit 2` and
  `--curriculum easy2hard --limit 2` each finish in < 30 s and write a run dir whose
  `config.json` records `curriculum` and `seed`.
- [ ] `--seed S` is recorded in `config.json`, and two runs with the same seed and curriculum
  produce identical `samples.jsonl` solve-rate columns.
- [ ] `make lint && make test` pass.

## Out of scope
- Plots, CIs, aggregation across seeds, report (issue 03).
- Changing the env, level generator or agent update rule.

## Files expected to change
- tasks/gridworld.py (add curricula classes)
- scripts/gridworld_train.py (add --curriculum, --seed)
- tests/test_gridworld_curricula.py (new)

## Depends on
#01
