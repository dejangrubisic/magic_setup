# Epic: MMLU-Pro per-question outputs — error clustering and label-error suspects

Goal: from 7 models' per-question MMLU-Pro outputs (TIGER-AI-Lab eval_results zips) and the HF
question set, produce (1) an item x model correctness matrix with per-model / per-category accuracy
and Wilson CIs, (2) an independent strict/lenient answer extractor and per-model format-failure rate,
(3) error clustering by category and a label-error suspect list with heuristic checks, reported in
`dev/practice/mmlupro/REPORT.md`.

Data (gitignored): `data/raw/mmlupro/questions.parquet` (HF `TIGER-Lab/MMLU-Pro` test, 12032 rows)
and `data/raw/mmlupro/<model>/model_outputs_<model>.json` (list of rows; keys `question_id` (str),
`pred`, `answer`, `answer_index` (str), `category`, `options` (stringified list), CoT under
`model_outputs` OR `generated_text`; one model has duplicate rows).

| # | Title | Depends on | Files | AC (one line) |
|---|-------|-----------|-------|---------------|
| 01 | Vertical slice: load, correctness matrix, per-model accuracy with Wilson CI | none | tasks/mmlupro.py, scripts/mmlupro_baseline.py, tests/test_mmlupro.py, tests/fixtures/mmlupro* | `uv run python scripts/mmlupro_baseline.py --limit 50` prints a per-model accuracy table with CIs and writes runs/ |
| 02 | Strict/lenient answer extractor, agreement with pred, format-failure rate, per-category table | 01 | tasks/mmlupro_extract.py, scripts/mmlupro_extract.py, tests/test_mmlupro_extract.py | script prints per-model strict/lenient/pred agreement and per-category accuracy table |
| 03 | Error clustering: distractor distribution per category, all-fail items, label-error heuristics | 01 | tasks/mmlupro_errors.py, scripts/mmlupro_errors.py, tests/test_mmlupro_errors.py | script prints distractor-index table per category and 20 sampled suspects with heuristic flags |
| 04 | REPORT.md + dev/LOG.md entry | 02, 03 | dev/practice/mmlupro/REPORT.md, dev/LOG.md | report has all tables with CIs and 3-5 findings |

Waves: 01 -> (02 || 03) -> 04. Run sequentially here (single agent).
