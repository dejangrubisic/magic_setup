# Epic: Eedi misconception retrieval baseline + failure-mode analysis

Goal: from the Kaggle 2024 Eedi data (train.csv, misconception_mapping.csv), build a retrieval eval
harness that ranks 2,587 misconceptions for each (question, wrong answer) pair, report MAP@25 with a
bootstrap CI for a TF-IDF cosine baseline on a stable held-out split, and analyse where it fails
(by subject, by construct, which misconceptions get confused).

Success artifact: `dev/practice/eedi/REPORT.md` with the baseline table, per-slice tables with CIs,
a confusion table, one figure, and 3-5 findings.

Data: `data/raw/eedi/{train,misconception_mapping}.csv` (gitignored, 0.3 MB).

| # | Title | Depends on | Files | AC (one line) |
|---|-------|-----------|-------|---------------|
| 01 | Vertical slice: reshape, split, TF-IDF baseline, MAP@25 + CI | none | tasks/eedi.py, scripts/eedi_baseline.py, tests/test_eedi.py, tests/fixtures/eedi_*.csv | `uv run python scripts/eedi_baseline.py --limit 50` prints a MAP@25 row with CI and writes runs/ |
| 02 | Slice analysis: MAP@25 by SubjectName / ConstructName with CIs, top-10 hardest constructs | 01 | scripts/eedi_slices.py, tests/test_eedi_slices.py | script prints two tables + hardest-10 from a run dir |
| 03 | Confusion between misconceptions + plot | 01 | scripts/eedi_confusion.py, tests/test_eedi_confusion.py | script prints top confused pairs and saves a png |
| 04 | REPORT.md + LOG.md entry | 02, 03 | dev/practice/eedi/REPORT.md, dev/LOG.md | report contains all tables + figure + findings |

Waves: [01] -> [02, 03 in parallel] -> [04].
