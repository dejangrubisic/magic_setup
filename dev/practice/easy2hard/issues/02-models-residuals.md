# 02: Full difficulty models (hand feats + TF-IDF; Ridge, GradientBoosting) and residual analysis

## Goal
Extend the predictor with two real models and analyse where they mis-rank. Metric: Spearman with
95% bootstrap CI per model on the stable test split; residual table by true rating quantile bin.

## Acceptance criteria
- [ ] `tasks/easy2hard.py` exposes `build_models() -> dict[str, Pipeline]` with keys `length_only`, `ridge_hand_tfidf`, `gbr_hand`; each is an sklearn estimator that `fit(rows_df, y)`s on a DataFrame with the hand-feature columns plus `question` text (TF-IDF over `question` for the ridge model).
- [ ] `uv run python scripts/easy2hard_predict.py --data tests/fixtures/easy2hard_tiny.jsonl` prints a table with the three model rows (`spearman, lo, hi, n_test`), and `samples.jsonl` has one row per (model, test item) with `id, model, y_true, y_pred, rating_quantile`.
- [ ] `tasks/easy2hard.py` exposes `residual_table(samples_df, n_bins=5) -> DataFrame` indexed by quantile bin with columns `n, mean_abs_err, mean_signed_err` (signed = pred - true); `uv run pytest tests/test_easy2hard_models.py` asserts the values on a 10-row hand-made frame.
- [ ] `tasks/easy2hard.py` exposes `worst_examples(samples_df, k=10) -> DataFrame` sorted by |pred - true| desc; test asserts ordering and k.
- [ ] `uv run python scripts/easy2hard_residuals.py --run <run dir>` prints the residual table and the 10 worst test items (question truncated to 120 chars, y_true, y_pred) for `ridge_hand_tfidf`.
- [ ] `make lint && make test` pass.

## Out of scope
Curriculum, hyper-parameter search, AMC, report writing.

## Files expected to change
tasks/easy2hard.py, scripts/easy2hard_predict.py, scripts/easy2hard_residuals.py, tests/test_easy2hard_models.py.

## Depends on
#01
