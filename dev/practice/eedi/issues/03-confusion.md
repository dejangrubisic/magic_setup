# 03: Confusion between misconceptions + plot

## Goal
From a finished `runs/eedi_baseline__*` directory (samples.jsonl has `true_id` and `top25` ids)
and `misconception_mapping.csv`, find which wrong misconceptions most often rank above the true
one: a table of (true name, confused-with name, count) for the top 15 pairs, and the 15
misconceptions most often ranked above a true one ("distractor" frequency). Save one figure:
bar chart of MAP@25 with CI per SubjectName for the 12 largest subjects
(`magic.plots.bar_with_ci`) to `<run dir>/map_by_subject.png`.

## Acceptance criteria
- [ ] `uv run pytest tests/test_eedi_confusion.py::test_confused_pairs` passes: for a tiny
      samples list, pairs are counted only for ids ranked strictly above the true id, and a row
      whose true id is rank 1 contributes no pairs.
- [ ] `uv run pytest tests/test_eedi_confusion.py::test_distractor_counts` passes: counts per
      distractor id equal the hand-computed values.
- [ ] `uv run python scripts/eedi_confusion.py --run <run dir> --limit 20` prints the two tables
      with misconception names, writes `<run dir>/confusion.md` and `<run dir>/map_by_subject.png` (file exists, > 0 bytes).
- [ ] `make lint && make test` pass.

## Out of scope
- Slice tables (02); report prose (04). Changes to `tasks/eedi.py`, `src/magic/`, `pyproject.toml`, `Makefile`.

## Files expected to change
scripts/eedi_confusion.py, tests/test_eedi_confusion.py

## Depends on
#01
