# 04 — mmlupro (MMLU-Pro per-question outputs: error clustering, extractor, label-error suspects)

T0 = 2026-09-02 20:20:36 PDT (first commit on `practice-mmlupro`, `1ca7666`; the epic/issue plan was
committed on `main` 2 min earlier). Worktree `.claude/worktrees/practice-mmlupro`, branch `practice-mmlupro`,
sub-branches `practice-mmlupro-issue-0{1,2,3,4}` each in its own worktree. Data: 188 MB of TIGER-AI-Lab
`eval_results` zips + HF `questions.parquet`, downloaded into the practice worktree (not the main checkout).
Deliverable: `dev/practice/mmlupro/REPORT.md` on `practice-mmlupro`.

Two agents: agent A ran T+0..T+30 and was killed by the session rate limit (its issue-04 review was
`Terminated: 15` at 20:50:24); agent B (this file's author) resumed the next morning, 2026-09-03.
Timestamps are from `git log --date=iso`, `git reflog`, the `runs/` directory names and the saved review
transcripts in the shared scratchpad (`mmlupro_review0N_rM.txt`, first line = start, mtime = end).

## Timeline
| milestone | min from T0 |
|---|---:|
| worktree ready + data loaded (188 MB unzipped, first `--limit 50` baseline run dir `20260902-202012` exists before the first commit) | -0.5 |
| issue 01 code + tests committed (`1ca7666`) | 0 |
| first baseline number (`--limit 50`, 7 models, Wilson CIs) | 0 |
| issue 02 extractor committed on a branch chained off issue-01 | 2.5 |
| first analysis table (extractor table + category x model, `--limit 200`, run `202212`) | 2 |
| issue 03 errors committed (also chained off issue-01) | 7.5 |
| full-data baseline (run `3aace0`, sonnet 0.762) | 7 |
| full-data extract + errors runs (`158e91`, `1b1c46`) | 8 |
| issue 01 review r2 REQUEST_CHANGES (spec edited in-branch: 99% -> 90% id threshold) | 13 |
| issue 02 review r1 APPROVE (first review passed) | 14 |
| issue 03 review r1 REQUEST_CHANGES (data not visible to the reviewer, see below) | 15 |
| REPORT.md + LOG entry committed on issue-04 (`4feda10`), branched from the *old* base | 14 |
| issue 03 review r2 APPROVE | 20 |
| issue 01 review r3 REQUEST_CHANGES (real defect: NaN tokens in samples.jsonl) | 21 |
| issue 01 fix `cfc1624` (pred None) | 22 |
| issue 01 review r4 APPROVE | 26 |
| 01, 02, 03 squash-merged into `practice-mmlupro` (`9d1a07c`, `9a7c7e3`, `6404eaf`) | 30 |
| cut-off: issue-04 review killed (`make: *** [review] Terminated: 15`) | 30 |
| resume (agent B): state mapped, docs diffed, tests green on the merged branch | R+0..R+3 |
| issue-04 rebased onto `practice-mmlupro` (clean, 1 commit) | R+3 |
| all three scripts re-run on full data with the merged code (14 s total) | R+4 |
| REPORT numbers corrected (see "real problems caught" below), committed `9f18667` | R+5 |
| issue-04 review round (agent B) started 09:35:05; still running at 09:40 when the orchestrator forced completion | R+6..R+11+ |
| 04 squash-merged WITHOUT a completed review verdict (round still running), lessons written, done | R+12 |

Agent A's wall clock: 30 min from T0 (plus ~4 min of planning before T0), of which roughly 20 min were
coding/data archaeology and the rest waiting on 6 completed review rounds (24 reviewer-minutes, up to
3 in parallel). Agent B: about 2 min at 08:34 (state mapping) and then a continuous block from 09:34;
active minutes are counted in the summary, the gap in between is not.

## What helped
- **Inspect the data before slicing.** Agent A found in the first minutes that one file
  (`Meta-Llama-3-70B`) has positional `question_id`s (0% agreement with HF) and duplicate rows, and
  that HF has since edited ~2% of question texts. The re-key-by-text loader was the single most
  important piece of code: without it the all-fail set was under-counted by 53% (582 vs 1,242).
- One worktree per sub-issue: reviews for 01, 02 and 03 ran concurrently (20:28-20:35), and the
  killed run left every branch intact and trivially resumable the next day.
- `magic.wilson_interval`, `magic.RunDir`, `magic.to_markdown` covered all stats/IO; zero new
  dependencies. The full-data pipeline (3 scripts, 84k rows) runs in 14 s, so re-verifying every
  number in the report after the resume cost nothing.
- Saved review transcripts in the scratchpad (`mmlupro_review0N_rM.txt`, with the start time on line 1)
  made the reviewer-behaviour reconstruction below possible. The new `runs/reviews/<target>__*.json`
  from `review_pr.sh` will do this properly.
- The issue files' "Files expected to change" line is what let the reviewer catch the in-branch spec
  edit (01 r2/r3); the amendment procedure now in `implement-issue` step 1 encodes the fix.
- Local markdown issues + `ISSUE=<file>` in `review_pr.sh`: no GitHub needed.

## What got in the way
- **Report numbers drifted from the code.** The REPORT's per-model table was pasted from run `3aace0`
  (T+7, before the `cfc1624` "keep missing pred as None" fix), which silently dropped ~275 no-`pred`
  rows per open model (n=11,757). The table listed n=12,032 with the 11,757-row accuracies
  (sonnet 0.762 vs 0.761, deepseek 0.661 vs 0.658, qwen 0.266 vs 0.264). The extractor table in the
  same report already had the right numbers, so the report contradicted itself by 0.1-0.3 points and
  nobody noticed. Also the gpt-4o row was missing from the extractor table (7 models in
  `summary.json`, 6 pasted). Fix took agent B 5 min *because the scripts are fast*; the lesson is that
  the report must be generated after the last code merge, from run ids that exist on the base branch.
- **Chained sub-branches.** 02 and 03 were branched off issue-01, and 04 off the base before the
  merges. That meant an extra rebase step for 03 (commit `ed92186`) and for 04 (agent B), and the
  reviewer for 02/03 was pointed at `BASE=practice-mmlupro-issue-01`, i.e. reviewed against an
  unmerged, later-changed base.
- **Data lived in the practice worktree, not the main checkout.** `review_pr.sh` symlinks
  `$root/data` from the worktree it is run in; issue-03's worktree had no `data/`, so review 03 r1
  returned REQUEST_CHANGES with "data/raw/mmlupro does not exist" (5 min lost, 1 round wasted).
  CLAUDE.md now says "download once, in the main checkout"; for this run it was not done.
- **In-branch spec edit** (99% -> 90% id-agreement threshold) cost two review rounds on issue 01
  (r2 and r3 both blocked on it) before it was ratified on the base (`f523720`) and the branch
  rebased. The amendment rule was added to `implement-issue` after this run.
- **Review latency**: 4-8 min per round; issue 01 needed 4 rounds (26 min of the 30). The rate-limit
  kill hit while the 04 review was running, at the very end, so a whole review round was lost.
- **Unexplained wall-clock gap on resume**: agent B's first `date` was 08:34:21 and the next tool
  call ran at 09:34:04 with nothing in between; only active minutes are reported.
- Cosmetic but repeated in 3 review notes: `magic.to_markdown` prints integer `n` as `12032.000`.

## What was missing
- Utility: `magic.to_markdown` should keep integer columns as integers (3 reviewer notes, every
  table in the REPORT has `12032.000`).
- Utility: a `rekey_by_text(outputs, questions, keys=[...])` helper in `magic` (or a documented
  pattern): matching model outputs to a benchmark by text is the standard fix when ids do not agree
  and was hand-written here.
- Doc line (CLAUDE.md Gotchas): "Paste report tables only from runs whose id is reproducible on the
  merged base branch; re-run the scripts after the last merge before writing REPORT.md."
- Skill step (implement-issue, report issue): "Before writing the report, `git rebase` onto the
  base with all dependencies merged and re-run every script; name the new run ids."
- Skill step / script guard (review_pr.sh): if `$root/data` does not exist, look for it in the main
  checkout (`git rev-parse --git-common-dir`/..) before declaring a data-dependent criterion
  unverifiable; or `make wt` should always symlink `data/` (it does now, per CLAUDE.md, but only when
  the data is in the main checkout).
- Makefile target: `make merge-issue B=<branch> N=<nn>` doing rebase-onto-base + squash + commit,
  which is the step every run in this batch got wrong at least once.
- Practice brief: state that the scratchpad is shared across concurrent agents (agent A's review
  transcripts survived only because they were prefixed `mmlupro_`).

## Reviewer behaviour
Rounds (start -> end from the saved transcripts; r1 of issue 01 was not saved):

| review | start | min | verdict | what it said |
|---|---|---:|---|---|
| 01 r2 | 20:28:00 | 5.5 | REQUEST_CHANGES | out-of-scope spec edit (99% -> 90%) in the branch; 3 notes (float `n`, fixture count, dropped-row count not printed) |
| 02 r1 | 20:30:03 | 4.3 | APPROVE | notes: `IGNORECASE` lets a lowercase `a` shadow the answer; pronoun `I` matches lenient; `n` uses max across models |
| 03 r1 | 20:30:06 | 5.3 | REQUEST_CHANGES | real-data criterion unverifiable: no `data/` visible to the reviewer (setup false positive); note: KeyError on empty frame; `--limit` before load marks every model rekeyed |
| 01 r3 | 20:34:03 | 7.9 | REQUEST_CHANGES | spec edit again + **real defect**: missing `pred` written as bare `NaN` in samples.jsonl under pandas 3 str dtype (verified 5,954 float NaNs) |
| 03 r2 | 20:36:05 | 4.3 | APPROVE | notes: `p in LETTERS` substring test; dup_option internal whitespace |
| 01 r4 | 20:42:43 | 3.7 | APPROVE | notes only (float `n`; 20/348 null preds counted wrong in `--limit 50`) |
| 04 r1 | 20:42:46 | killed at 7.6 | none | `make: *** [review] Terminated: 15` (rate limit) |
| 04 r2 (agent B) | 09:35:05 | >5, unfinished | none at hard stop | log: `.claude/worktrees/practice-mmlupro-issue-04/runs_review_04.log`; verdict JSON will land in that worktree's `runs/reviews/` if the process finishes |

Totals: 6 completed rounds, 31 reviewer-minutes (mean 5.2), 3 blocking verdicts of which 2 were
legitimate (spec edit; NaN JSON) and 1 was a setup artefact (data not visible). Plus 1 killed round
and agent B's round, which the 50-minute hard stop cut off before a verdict: issue 04 was merged unreviewed and a human should read the verdict file before trusting REPORT.md.

- Real problems caught: (1) NaN tokens in `samples.jsonl` (invalid JSON, pandas 3 `str` dtype
  subtlety), with the exact count and a verified reproduction; (2) unratified spec edit in the
  branch; (3) `distractor_distribution` KeyError on an empty frame and `--limit`-before-load marking
  every model re-keyed, both fixed in `ed92186` although filed as notes.
- False positives: 03 r1's "no data" block (environment, not the PR). 01 r2 could have been avoided
  if the amendment rule had existed (it now does).
- False negatives: no reviewer round looked at whether the REPORT's numbers matched a run on the
  merged base (04 was never reviewed by agent A; agent B's round is the first). The 02 r1 note about
  `IGNORECASE` shadowing the answer (`the answer is a prime ... answer is (C)`) is a genuine bug that
  stayed a note because the issue text said "case-insensitive"; the issue was wrong, not the review.
- Style: every finding cited `file:line` and, for the defect, a reproduction on real data;
  obligations tables were complete (8-10 rows) and notes were capped at three. Duration correlates
  with diff size, not with verdict.

## Setup changes proposed
1. `scripts/review_pr.sh`: resolve `data/` from the main checkout (`git rev-parse --git-common-dir`)
   when the worktree has none, and print "data: <path>" in the header, so a missing dataset is a
   setup message, not a REQUEST_CHANGES (03 r1).
2. `.claude/skills/implement-issue/SKILL.md` step 4/7 for report issues: "rebase onto the base with
   all dependencies merged, re-run every script, paste from those run ids" (would have caught the
   0.762 vs 0.761 drift and the missing gpt-4o row).
3. `Makefile`: `make merge-issue B=<branch> N=<nn>` = `git rebase <base>` + `merge --squash` +
   commit with `<type>: <what> (#N)`; every run in the batch hit the chained-branch conflict.
4. `src/magic/results.py` `to_markdown`: leave integer columns unformatted (3 reviewer notes, all
   report tables).
5. `CLAUDE.md` Gotchas: "`data/` must be downloaded in the main checkout; a worktree-only `data/` is
   invisible to `make review`" (the existing line says download there, not why).
6. `review_pr.sh`: on `Terminated`/rate limit, write a `runs/reviews/<target>__*.json` with
   `verdict: null, reason: killed` so a resumed agent can see that a round happened (04 r1 left only a
   one-line scratch file).
7. Practice brief / `plan-issues`: when a sub-issue depends on another, say "branch from the base
   after the dependency merges" explicitly; chained branches cost a rebase in 3 of 4 issues here.
8. `src/magic`: `rekey_by_text(outputs, questions, on=[...])` helper with a test, since
   id-mismatch between model dumps and the benchmark is the norm, not the exception.
