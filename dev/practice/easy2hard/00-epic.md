# Epic: easy2hard — difficulty prediction, residuals, curriculum on Easy2Hard-Bench (E2H-GSM8K)

Goal: from human/model-derived IRT difficulty ratings on GSM8K items, (1) predict difficulty from
text features, (2) find where the predictor mis-ranks, (3) test whether predicted vs true vs random
easy->hard orderings change a simple learner's learning curve. Success artifact: dev/practice/easy2hard/REPORT.md
with Spearman (bootstrap CI) tables, residual table, learning-curve figure with CIs over 5 seeds.

Data: HF `furonghuang-lab/Easy2Hard-Bench` config `E2H-GSM8K`, split `eval`, 1319 rows, columns
rating, rating_std, rating_quantile, question, answer, model_avg_acc, unnorm_rating(_std).
Local copy data/raw/easy2hard/gsm8k.jsonl (gitignored). AMC is optional and out of scope for the practice run.

| # | Title | Depends on | Files | AC (one line) |
|---|-------|-----------|-------|---------------|
| 01 | Vertical slice: fetch, features, length-only Ridge baseline, Spearman+CI table | none | tasks/easy2hard.py, scripts/easy2hard_fetch.py, scripts/easy2hard_predict.py, tests/test_easy2hard.py, tests/fixtures/easy2hard_tiny.jsonl | `scripts/easy2hard_predict.py --limit 200` prints a markdown table with Spearman + 95% CI for the length-only baseline |
| 02 | Full models (hand feats + TF-IDF; Ridge, GBR) + residual analysis by quantile + 10 worst | 01 | tasks/easy2hard.py, scripts/easy2hard_predict.py, scripts/easy2hard_residuals.py, tests/test_easy2hard_models.py | table has 3 rows (baseline, ridge, gbr); residuals script writes per-quantile table + 10 worst |
| 03 | Curriculum learning curves (pred / true / random ordering, 5 seeds, CIs, plot) | 01 | tasks/easy2hard_curriculum.py, scripts/easy2hard_curriculum.py, tests/test_easy2hard_curriculum.py | script writes runs/<id>/summary.json + curve png; test checks curve shape and determinism |
| 04 | REPORT.md + LOG.md entry | 02, 03 | dev/practice/easy2hard/REPORT.md, dev/LOG.md | report contains the three tables, figure, 3-5 findings |

Waves: 01 -> (02 || 03) -> 04.
