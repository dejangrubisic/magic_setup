# 01: Vertical slice: reshape, split, TF-IDF baseline, MAP@25 + CI

## Goal
Load `data/raw/eedi/train.csv` + `misconception_mapping.csv`, reshape to one row per
(QuestionId, wrong-answer letter) with a known MisconceptionId, split by QuestionId with
`magic.stable_split`, rank all 2,587 misconceptions with TF-IDF (word + char n-grams) cosine
similarity, and print MAP@25 with a bootstrap CI. Writes a run dir via `magic.RunDir` with one
sample per test row (id, QuestionId, letter, SubjectName, ConstructName, true id, top-25 ids, ap).

## Acceptance criteria
- [ ] `uv run pytest tests/test_eedi.py::test_reshape_rows` passes: reshape of the fixture yields
      exactly one row per non-null Misconception{A,B,C,D}Id, excludes the correct answer's letter,
      and has columns QuestionId, letter, QuestionText, AnswerText, ConstructName, SubjectName, MisconceptionId.
- [ ] `uv run pytest tests/test_eedi.py::test_split_is_by_question` passes: all rows of a
      QuestionId land in the same split.
- [ ] `uv run pytest tests/test_eedi.py::test_map_at_k` passes on hand-computed cases
      (true id at rank 1 -> 1.0, rank 3 -> 1/3, absent -> 0.0).
- [ ] `uv run pytest tests/test_eedi.py::test_rank_returns_topk_ids` passes: ranking returns
      k misconception ids per row, and a row whose text is identical to a misconception name ranks it first.
- [ ] `uv run python scripts/eedi_baseline.py --limit 50` runs in < 60 s, prints a markdown
      table with columns run, n, map25, lo, hi and writes `runs/eedi_baseline__*/{config.json,samples.jsonl,summary.json}`.
- [ ] `make lint && make test` pass.

## Out of scope
- Any per-slice analysis, plots, or report (issues 02-04).
- Any model beyond TF-IDF; no LLM calls; no dense embeddings.
- Changes to `pyproject.toml`, `Makefile`, `src/magic/`.

## Files expected to change
tasks/eedi.py, scripts/eedi_baseline.py, tests/test_eedi.py, tests/fixtures/eedi_train.csv,
tests/fixtures/eedi_misconceptions.csv

## Depends on
none
