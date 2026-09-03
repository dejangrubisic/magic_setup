# 01: Vertical slice — fetch E2H-GSM8K, hand features, length-only baseline, Spearman table

## Goal
Land the end-to-end pipeline: download E2H-GSM8K to data/raw/easy2hard/gsm8k.jsonl, compute hand
features per item, split with `magic.stable_split`, fit a length-only Ridge baseline on train, and
print a markdown table with Spearman correlation (true rating vs predicted) on test with a 95%
bootstrap CI. Metric: Spearman rho on the stable test split.

## Acceptance criteria
- [ ] `uv run python scripts/easy2hard_fetch.py` writes `data/raw/easy2hard/gsm8k.jsonl` (one row per item, keys `id, question, answer, rating, rating_std, rating_quantile, model_avg_acc`) using `magic.write_jsonl`; `--limit N` writes at most N rows.
- [ ] `tasks/easy2hard.py` exposes `hand_features(row) -> dict` with keys `q_len_chars, q_len_words, n_numbers, n_operators, n_sentences, answer_magnitude, sol_len_lines`, and `uv run pytest tests/test_easy2hard.py` asserts exact values on a hand-written example.
- [ ] `tasks/easy2hard.py` exposes `spearman_ci(y_true, y_pred, seed) -> (rho, lo, hi)` using `magic.bootstrap_ci` over paired resamples; test asserts rho == 1.0 for a monotone pair and lo <= rho <= hi.
- [ ] `uv run python scripts/easy2hard_predict.py --data tests/fixtures/easy2hard_tiny.jsonl --limit 50` runs without network, writes `runs/easy2hard_predict__*/{config.json,samples.jsonl,summary.json}` via `magic.RunDir`, and prints a markdown table with a row `length_only` and columns `spearman, lo, hi, n_test`.
- [ ] Split is `magic.stable_split(id, test_pct=20)`; test asserts the same id always lands in the same split.
- [ ] `make lint && make test` pass.

## Out of scope
TF-IDF, GradientBoosting, residual analysis, curriculum, AMC config.

## Files expected to change
tasks/easy2hard.py, scripts/easy2hard_fetch.py, scripts/easy2hard_predict.py,
tests/test_easy2hard.py, tests/fixtures/easy2hard_tiny.jsonl (<= 60 rows, generated from real data).

## Depends on
none
