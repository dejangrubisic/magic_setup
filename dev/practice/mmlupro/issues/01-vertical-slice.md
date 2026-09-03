# 01: Vertical slice — load data, item x model correctness matrix, per-model accuracy with Wilson CIs

## Goal
Load the HF question table and the per-model output JSONs, build a tidy item x model correctness
table (`question_id, model, category, pred, answer, correct`), and print per-model accuracy with
Wilson 95% CIs. Gives the baseline number everything else builds on.

## Acceptance criteria
- [ ] `tasks/mmlupro.py` exposes `load_questions(path)` (parquet or jsonl -> DataFrame with int
      `question_id`, `answer`, `answer_index`, `category`, `options` as a python list) and
      `load_model_outputs(dir)` -> DataFrame with columns `model, question_id (int), pred, answer,
      category, cot` where `cot` comes from `model_outputs` or `generated_text`, and duplicate
      `(model, question_id)` rows are dropped (first kept). When `questions` is passed and a
      model's `question_id`s agree with the HF ids on < 90% of rows (matched by question text +
      first option), that model is re-keyed by text to HF ids and unmatched rows are dropped;
      a `rekeyed` bool column says which rows were re-keyed.
- [ ] `correctness_matrix(outputs_df)` returns a DataFrame indexed by question_id with one bool column
      per model (NaN where a model has no row).
- [ ] `model_accuracy(outputs_df)` returns a DataFrame `model, n, acc, lo, hi` using `magic.wilson_interval`.
- [ ] `uv run pytest tests/test_mmlupro.py` passes on tiny fixtures in `tests/fixtures/` (3 models,
      6 questions incl. one duplicate row, one `generated_text` model, and one model with shifted ids) and asserts the exact
      accuracies and that the duplicate is dropped.
- [ ] `uv run python scripts/mmlupro_baseline.py --limit 50` runs on real data, writes
      `runs/mmlupro_baseline__*/{config.json,samples.jsonl,summary.json}` via `magic.RunDir`, and
      prints a markdown per-model accuracy table.
- [ ] `pyproject.toml` gains `pythonpath = ["."]` under `[tool.pytest]` so tests import `tasks/`;
      scripts add the repo root to `sys.path` themselves.
- [ ] `make lint && make test` pass.

## Out of scope
Own answer extraction (02). Error clustering (03). Plots.

## Files expected to change
tasks/mmlupro.py, scripts/mmlupro_baseline.py, tests/test_mmlupro.py, tests/fixtures/mmlupro_questions.jsonl, tests/fixtures/mmlupro/**/*.json, tasks/__init__.py, pyproject.toml (pytest pythonpath only)

## Depends on
none
