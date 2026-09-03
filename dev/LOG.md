# Experiment log

One entry per experiment, newest first, including negative results. Numbers come from
`magic.results` tables, not from memory.

## 2026-09-03: LiveBench reasoning re-scored, 1PL IRT, zebra failure taxonomy (positive) — issues #01-#05, runs `runs/livebench_baseline__20260903-083616__fdcd92`, `runs/livebench_irt__20260903-083617__c76890`, `runs/livebench_taxonomy__20260903-093342__a89f78`
- what changed: model x question strict/lenient score matrix from raw `model_answer` (no reasoning rows in `model_judgment`); 1PL IRT via sklearn on one-hot(model)+one-hot(item); taxonomy `correct|wrong_answer|format_failure|truncation|no_answer`; issue 05 let the spatial extractor accept shape names and required >= 200 chars for `truncation`.
- result vs baseline: strict mean over all cells 0.256 (`runs/livebench_baseline__20260902-203705__f14030`, before #05) -> 0.275; o1-mini spatial 0.380 -> 0.500 [0.366, 0.634]; the 7 zero-pass "hardest" spatial items disappear; zebra truncation 661 -> 290 rows (371 were one-word answers). Strict/lenient exact agreement 0.945, 240 lenient rescues; most negative discrimination proxy -0.07 (no label-error signal).
- keep: extractor fixes (#05) and the report `dev/practice/livebench/REPORT.md`. Drop: nothing. Practice-run notes: #02 and #05 were squash-merged before their 2026-09-03 re-reviews returned (time budget); verdicts in `.claude/worktrees/practice-livebench-issue-0{2,5}/runs/reviews/`.

## YYYY-MM-DD: <idea> (positive | negative | inconclusive) — issue #N, run `runs/<id>`
- what changed
- result vs baseline (table)
- keep / drop, and why
