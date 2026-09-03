# 04: REPORT.md + LOG.md entry

## Goal
Write `dev/practice/eedi/REPORT.md`: baseline MAP@25 with CI on the held-out split, per-subject
and per-construct tables (top rows), hardest-10 constructs, confusion tables, the figure, and
3-5 concrete findings about failure modes / difficulty / curriculum. Append a dated entry to
`dev/LOG.md`.

## Acceptance criteria
- [ ] `dev/practice/eedi/REPORT.md` exists, cites the run id, and contains the baseline table with
      CI, the by-subject table, the hardest-constructs table, a confusion table, the figure path, and a
      "Findings" section with 3-5 numbered items each citing a number from the tables.
- [ ] `dev/LOG.md` has a new dated entry naming the run and the baseline number.
- [ ] `make lint && make test` pass.

## Out of scope
- Any code change.

## Files expected to change
dev/practice/eedi/REPORT.md, dev/LOG.md, dev/practice/eedi/map_by_subject.png (copied figure)

## Depends on
#02, #03
