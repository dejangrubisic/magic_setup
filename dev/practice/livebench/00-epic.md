# Epic: LiveBench reasoning — model x item matrix, IRT, failure taxonomy

Goal: from the public LiveBench tables build a model x question score matrix for the reasoning
category, report per-task accuracy with Wilson CIs, fit a 1PL IRT to get item difficulty and model
ability, flag label-error suspects, and classify failures (format vs wrong vs truncation).

Data finding (T+3 min): `livebench/model_judgment` (split `leaderboard`) contains NO reasoning rows
(only language, coding, instruction_following). `livebench/model_answer` has 13,095 reasoning
answers from 91 models over 150 questions, and `livebench/reasoning` carries ground truth for all of
them. Adaptation: the score matrix is derived by re-scoring raw answers against ground truth with our
own strict/lenient extractors (the "provided score" for reasoning does not exist in the public
tables; agreement is reported strict-vs-lenient and against the LiveBench scoring rules instead).

Raw data: `data/raw/livebench/{model_judgment,model_answer,reasoning}.parquet` (gitignored).

| # | Title | Depends on | Files | AC (one line) |
|---|-------|-----------|-------|---------------|
| 01 | Vertical slice: load, score, per-task accuracy table | - | tasks/livebench.py, scripts/livebench_baseline.py, tests/test_livebench.py, tests/fixtures/livebench_*.jsonl | script prints top-10 models x 3 tasks with Wilson CIs, writes runs/ |
| 02 | 1PL IRT: difficulty, ability, hardest items, label-error suspects | 01 | tasks/livebench_irt.py, scripts/livebench_irt.py, tests/test_livebench_irt.py | 15 hardest + 5 negative-discrimination items listed |
| 03 | Parser agreement + failure taxonomy for zebra_puzzle | 01 | tasks/livebench_taxonomy.py, scripts/livebench_taxonomy.py, tests/test_livebench_taxonomy.py | strict/lenient agreement + taxonomy counts on bottom-quartile items |
| 05 | Spatial extractor accepts shape names; truncation needs >=200 chars | 03 | tasks/livebench.py, tasks/livebench_taxonomy.py, tests | 7 zero-pass spatial items disappear |
| 04 | REPORT.md + dev/LOG.md | 02, 03, 05 | dev/practice/livebench/REPORT.md, dev/LOG.md | report contains all tables with CIs and 3-5 findings |

Waves: 01 -> (02 || 03) -> 05 -> 04.
