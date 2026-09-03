# 01: Vertical slice — load LiveBench reasoning, score answers, per-task accuracy table

## Goal
Load the three local parquet tables, join reasoning answers with ground truth, score each answer
with a strict and a lenient extractor, and print per-task accuracy for the top 10 models with
Wilson CIs. Provides the model x question score matrix that issues 02 and 03 build on.

## Acceptance criteria
1. `tasks/livebench.py` exposes `load_reasoning(raw_dir)` returning one row per (model, question)
   with columns `question_id, task, model, answer, ground_truth`; only reasoning rows; questions
   without ground truth are dropped; duplicate (model, question_id) rows (the raw table has 45,
   same text, different `answer_id`) are collapsed to the latest `tstamp`, so `n` counts questions. Tested on the fixture (`tests/test_livebench.py`).
2. `extract_answer(text, task, mode)` with `mode in {"strict","lenient"}` implements the answer
   formats the prompts in the public answer table actually request (checked against data/raw:
   0/4350 zebra answers contain `<solution>`, the loaded zebra questions are the single-answer
   generation): `spatial` -> bold integer `**4**`, `web_of_lies_v2` -> bold yes/no list
   `**yes, no, yes**`, `zebra_puzzle` -> triple-bold `***answer***`. Strict requires the exact
   format (last occurrence); lenient falls back, in order, to the last integer anywhere (spatial)
   / the last comma-separated yes-no run anywhere (web_of_lies_v2), then the last bold span, then
   the last non-empty line. Returns `None` if nothing found. Tests cover each task,
   strict-vs-lenient divergence, and the `None` case.
3. `score_answer(text, ground_truth, task, mode) -> float` in [0,1]: exact normalized match for
   spatial and web_of_lies_v2; for zebra_puzzle the fraction of comma-separated fields matching
   (LiveBench partial credit). Tested with a known-partial zebra case (2/4 -> 0.5).
4. `score_matrix(df, mode) -> DataFrame` models x question_id of scores (NaN where missing). Tested.
5. `scripts/livebench_baseline.py --limit N` writes `runs/livebench_baseline__*/{config.json,
   samples.jsonl,summary.json}` via `magic.RunDir` and prints a markdown table: top 10 models
   (by overall strict mean) x task with `mean [lo, hi]` Wilson CIs (n = questions in task),
   strict mode; `--limit` restricts the number of questions. `per_task_table` is tested on the
   fixture frame (`tests/test_livebench.py`).
6. `make lint && make test` pass; tests never read `data/raw`.

## Out of scope
IRT (02), taxonomy (03), plots, any other category than reasoning.

## Files expected to change
`tasks/livebench.py`, `scripts/livebench_baseline.py`, `tests/test_livebench.py`,
`tests/fixtures/livebench_answers.jsonl`, `tests/fixtures/livebench_reasoning.jsonl`, `tasks/__init__.py` (new, empty), `pyproject.toml` (only: `pythonpath = ["."]` under `[tool.pytest]` so tests can import `tasks/`).

## Depends on
none

## Amendments
- 2026-09-02 (practice run, recorded on the base branch before the code): answer formats corrected to what the data contains; lenient chain spelled out; `pyproject.toml` pythonpath line; `per_task_table` test; dedupe rule (from review round 2).
