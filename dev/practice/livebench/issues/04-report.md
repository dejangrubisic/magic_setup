# 04: REPORT.md and LOG entry

## Goal
Write `dev/practice/livebench/REPORT.md` from the run outputs of issues 01-03 and append a dated
entry to `dev/LOG.md`.

## Acceptance criteria
1. REPORT.md contains: the data adaptation note; per-task accuracy table for the top 10 models with
   Wilson CIs; 15 hardest items; 5 negative-discrimination suspects; strict/lenient agreement;
   taxonomy counts; 3-5 concrete findings about failure modes / difficulty / curriculum.
2. Every number cites the run directory it came from.
3. `dev/LOG.md` has a dated entry pointing at the runs.

## Out of scope
Code changes.

## Files expected to change
`dev/practice/livebench/REPORT.md`, `dev/LOG.md`

## Depends on
02, 03
