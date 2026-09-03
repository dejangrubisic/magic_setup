# 02: Slice analysis: MAP@25 by SubjectName / ConstructName with CIs, hardest constructs

## Goal
From a finished `runs/eedi_baseline__*` directory (samples.jsonl has per-row `ap`, `SubjectName`,
`ConstructName`), print MAP@25 per SubjectName and per ConstructName with bootstrap CIs and n, and
the 10 hardest constructs (lowest MAP@25 among constructs with n >= 3).

## Acceptance criteria
- [ ] `uv run pytest tests/test_eedi_slices.py::test_slice_table` passes: given a tiny samples
      DataFrame, the table has one row per slice value plus ALL, columns n, map25, lo, hi, and
      map25 equals the hand-computed mean per slice.
- [ ] `uv run pytest tests/test_eedi_slices.py::test_hardest_filters_min_n` passes: slices with
      n < min_n are excluded and the result is sorted ascending by map25 with at most `top` rows.
- [ ] `uv run python scripts/eedi_slices.py --run <run dir> --limit 20` prints three markdown
      tables (by subject, by construct, hardest constructs) and writes them to `<run dir>/slices.md`.
- [ ] `make lint && make test` pass.

## Out of scope
- Confusion analysis and plots (03); report prose (04). Re-running the baseline.
- Changes to `tasks/eedi.py`, `src/magic/`, `pyproject.toml`, `Makefile`.

## Files expected to change
scripts/eedi_slices.py, tests/test_eedi_slices.py

## Depends on
#01
