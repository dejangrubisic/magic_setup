# 04: REPORT.md and LOG.md entry

## Goal
Write dev/practice/easy2hard/REPORT.md from the real runs (full data, not fixtures): Spearman
table with CIs, residual-by-quantile table, 10 worst examples with a hypothesis, curriculum
summary table and figure, and 3-5 concrete findings. Append a dated entry to dev/LOG.md.

## Acceptance criteria
- [ ] `dev/practice/easy2hard/REPORT.md` exists and contains the run ids it was built from, the three tables (pasted from script output), a link to the curve figure copied into dev/practice/easy2hard/curve.png, and a "Findings" section with 3-5 bullets.
- [ ] `dev/LOG.md` has a new dated entry with result vs baseline and keep/drop.
- [ ] `make lint && make test` pass.

## Out of scope
New code, new experiments.

## Files expected to change
dev/practice/easy2hard/REPORT.md, dev/practice/easy2hard/curve.png, dev/LOG.md.

## Depends on
#02, #03
