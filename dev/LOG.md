# Experiment log

One entry per experiment, newest first, including negative results. Numbers come from
`magic.results` tables, not from memory.

## YYYY-MM-DD: <idea> (positive | negative | inconclusive) — issue #N, run `runs/<id>`
- what changed
- result vs baseline (table)
- keep / drop, and why

## 2026-09-03: Eedi practice run resumed after rate limit (inconclusive) — practice issues #02-#04, run `runs/eedi_baseline__20260902-203158__24b965`
- Reviewed the three pending sub-branches locally in parallel (verdicts in `runs/reviews/`): #02 APPROVE, #03 APPROVE, both squash-merged here.
- #04 (REPORT.md) went through 3 review rounds: round 1 blocked on a finding citing unscripted numbers (fixed), round 2 on an over-claimed CI non-overlap (fixed), round 3 on this LOG's own entry naming an unmeasured failure mode (fixed on the branch). Three rounds reached: **needs-human** — `practice-eedi-issue-04` (4 commits over this branch) is complete and unmerged; a human ratifies or asks for a 4th round. Merging it will conflict with this entry in `dev/LOG.md` (keep both).
- Baseline number unchanged: MAP@25 = 0.164 [0.144, 0.183] on 819 test rows; the report on the branch has 5 findings, all citing the subject/construct/confusion tables.
