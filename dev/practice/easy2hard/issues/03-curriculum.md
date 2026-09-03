# 03: Curriculum learning curves — predicted vs true vs random easy->hard ordering

## Goal
Measure whether ordering training items easy->hard by predicted rating, by true rating, or at
random changes the learning curve of a simple learner proxy. Learner: logistic regression on
hand features + TF-IDF predicting `rating_quantile >= median` (median from train). For each
ordering and prefix size in a fixed grid, fit on the prefix and score accuracy on the held-out
stable test split; 5 seeds (random ordering resampled per seed; the learner seed also varies).
Artifact: learning-curve figure with mean and 95% bootstrap CI across seeds, plus summary table.

## Acceptance criteria
- [ ] `tasks/easy2hard_curriculum.py` exposes `orderings(train_df, pred_col, seed) -> dict[str, np.ndarray]` with keys `pred_easy2hard, true_easy2hard, random`, each a permutation of `range(len(train_df))`; test asserts they are permutations, that `true_easy2hard` sorts `rating` ascending and `random` differs across seeds.
- [ ] `tasks/easy2hard_curriculum.py` exposes `learning_curve(train_df, test_df, order, prefix_sizes, seed) -> list[float]` (test accuracy per prefix); test on the tiny fixture asserts length == len(prefix_sizes) and values in [0, 1], and that the same seed gives identical output.
- [ ] `uv run python scripts/easy2hard_curriculum.py --data tests/fixtures/easy2hard_tiny.jsonl --seeds 2 --limit 60` writes `runs/easy2hard_curriculum__*/summary.json` with, per ordering and prefix size, `mean, lo, hi` over seeds, and saves `curve.png` in the run dir. The predicted rating used for `pred_easy2hard` is out-of-fold (5-fold cross_val_predict of the ridge model on train) so the curriculum never sees the test set.
- [ ] `make lint && make test` pass.

## Out of scope
Changing the difficulty models, report writing, AMC.

## Files expected to change
tasks/easy2hard_curriculum.py, scripts/easy2hard_curriculum.py, tests/test_easy2hard_curriculum.py.

## Depends on
#01 (#02 only for the ridge model name; if 02 is unmerged, use `build_models()["ridge_hand_tfidf"]` once available, else the length-only baseline).
