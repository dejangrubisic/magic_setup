# 01 — eedi (Kaggle Eedi 2024 misconception retrieval, TF-IDF MAP@25, failure modes)

T0 = 2026-09-02 20:18 PDT (epic commit `cf0529f`; branch created 20:16). Worktree
`.claude/worktrees/practice-eedi`, branch `practice-eedi`, sub-branches `practice-eedi-issue-0{1,2,3,4}`
all built in the *same* worktree as a chain (01 -> 02 -> 03 -> 04), no sibling worktrees. Deliverable:
`dev/practice/eedi/REPORT.md` on `practice-eedi`. Two agents: agent A (20:16-~20:50, killed by the API
rate limit), agent B (resume 2026-09-03 08:34, this file).

## Timeline
| milestone | min from T0 | evidence |
|---|---:|---|
| worktree ready (branch created 20:16:19) | -2 | reflog |
| data loaded (`data/raw/eedi/eedi.zip` downloaded *into the worktree*, 0.27 MB) | -1.5 | file mtime 20:16:50 |
| epic + 4 issue files committed | 0 | `cf0529f` |
| first baseline number (`--limit 50`, MAP@25 0.208 [0.132, 0.293]) | 13 | run dir 20:31:39 |
| full baseline (819 test rows, 0.164 [0.144, 0.183]) + no-construct ablation (0.109) | 14 | run dirs 20:31:58 / 20:32:00 |
| issue 01 committed (uncommitted while runs were made: config.json has sha `cf0529f`) | 14 | author date 20:32:13 |
| first analysis table (issue 02 committed, slices.md) | 15 | author date 20:33:07 |
| issue 03 (confusion + png) and 04 (REPORT.md, LOG.md) committed | 15.5 / 16.5 | author dates 20:33:40 / 20:34:43 |
| review round 1 on 01 -> REQUEST_CHANGES (reviewer's verification run at 20:34:50) | ~16-21 | run dir sha `6da5d5a` |
| issue 01 amendment on base (`pythonpath`, `python -m`), chain rebased, fix commit | 22 | 20:39:54-20:40:22 |
| review round 2 on 01 -> APPROVE (reviewer's verification run at 20:41:55) | ~22-28 | run dir sha `f0c37ff` |
| first review passed; 01 squash-merged; 02/03/04 rebased onto it | 28.5 | 20:46:44 |
| cut-off (rate limit while reviewing 02; no verdict saved anywhere) | ~29-35 | nothing after 20:46:44 |
| resume (agent B) | 736 wall / 35 active | 2026-09-03 08:34 |
| state mapped, lint+61 tests green on 04 tip, three reviews launched in parallel | 37 active | 08:35 |
| 02 APPROVE (3.5 min), 03 APPROVE (4.8 min), 04 REQUEST_CHANGES (4.2 min); 02 and 03 squash-merged | 45-46 active | 08:43-08:45 |
| 04 fixed (finding 5 rewritten, 12th subject row), round 2 launched | 47 active | 08:46 |
| 04 round 2 -> REQUEST_CHANGES (5.5 min): my new finding 5 over-claimed "CIs do not overlap" | 52 active | 08:51 |
| **harness stall**: no tool call returned between 08:46 and 09:33 (47 min wall, not agent time) | - | 09:33 |
| 04 fixed again, round 3 launched; lessons written | 53 active | 09:34 |
| 04 round 3 -> REQUEST_CHANGES (7.7 min) on a stale LOG phrase; fixed on the branch, **needs-human**, not merged | 62 active | 09:42 |
| done (LOG entry on practice-eedi, lessons) | 63 active | 09:43 |

Agent A: ~16 min from T0 to all four issues coded and the report written, then ~13 min of review
on issue 01 alone (two rounds), then killed. Agent B: 1 min to map state, ~1 min of actual editing, the rest waiting on 7 review runs (3 lost to a
script edit, 4 real) plus a 47-minute harness stall that is excluded from the active count.

## What helped
- The scaffold's `magic.stable_split` (by QuestionId), `bootstrap_ci`, `RunDir` (config/samples/summary),
  `to_markdown`, `plots.bar_with_ci` covered every need; zero new dependencies. The whole pipeline
  (reshape -> split -> TF-IDF over 2,587 names -> MAP@25 + CI) runs in 0.8 s, so ablations were free
  (the no-construct ablation, the single most useful number in the report, took one flag).
- Issue files with one-line, testable ACs: every AC in 01-03 maps to a named pytest, and the 04 AC
  ("each finding cites a number from the tables") shaped the report's Findings section directly.
- Tiny real fixtures (`tests/fixtures/eedi_train.csv`, 8 questions, 33 misconceptions) made the
  ranking tests run in 40 ms and let the reviewer verify ACs without touching the full data.
- Dependencies expressed as data files, not imports: 02 and 03 read `samples.jsonl` from a run dir,
  so they could be written and tested before 01 was even reviewed.
- Committing the amendment for 01 on the base branch and rebasing the chain (agent A did this at
  20:39-20:40) is exactly what the updated implement-issue skill now prescribes.
- On resume: the reflog reconstructed the whole first session (every rebase, amend, checkout with
  timestamps), and `config.json.git_sha` in the run dirs identified which runs were the reviewer's
  verification runs vs the agent's. Reviewing the three pending branches in parallel, each against
  its parent branch (`BASE=practice-eedi-issue-02` for 03, etc.), avoided re-reviewing chained diffs.

## What got in the way
- **Rate limit with nothing persisted.** Agent A spent ~13 of 35 min on two review rounds of one
  issue and hit the limit on the first review of 02; the old `review_pr.sh` printed the verdict to
  stdout only, so nothing survived. The new script writes `runs/reviews/<branch>__<ts>.json` and exits
  3 on rate limit; that would have made the resume a 30-second read instead of a reflog forensic job.
- **The report issue ate five review rounds across two agents and is still unmerged.** Each round found
  one real but small prose defect (unscripted numbers -> over-claimed CI non-overlap -> stale LOG phrase),
  and each fix I made introduced the next one. A docs-only issue with "every number must come from a
  table" as its AC needs the numbers scripted *first*; text-only fixes under time pressure regress.
- **Review latency dominates.** Coding all four issues took ~16 min; one review round took 5-6 min
  and they ran serially on a single chained worktree. The brief's "sibling worktrees per issue" never
  happened for eedi, so 02/03/04 could not be reviewed while 01 was.
- **The 01 amendment cost a round.** `tasks/` was not importable (no `pythonpath`), so the first
  version of 01 needed an amendment to touch `pyproject.toml`; round 1 of the review was spent on
  that plus a docstring and a missing test. CLAUDE.md now documents `pythonpath` and `python -m`;
  the *new* CLAUDE.md says task code belongs in `src/magic/tasks/<name>.py`, which contradicts the
  eedi epic (`tasks/eedi.py`) written against the old docs. Worktree copies of CLAUDE.md and both
  skills are older than main's (main adds: amendments procedure, pristine-checkout reviews,
  `runs/reviews/`, `tests_on_base.sh`, NaN-is-a-defect, `make doctor`).
- **Data landed in the worktree, not the main checkout** (`.claude/worktrees/practice-eedi/data/raw/eedi`),
  so a fresh worktree from main would have no data; the new CLAUDE.md line ("download once, in the
  main checkout; `make wt` symlinks it") did not exist when agent A started.
- **The state note handed to agent B was wrong** ("03 and 04 untouched"): both branches existed with
  full commits. Mapping state from git took 1 min and prevented redoing 2 issues; a resume brief
  should be generated from `git branch --contains` / reflog, not from memory.
- **Scripted text replacement that matches nothing is silent.** My finding-2 wording fix targeted a
  phrase that wraps across two lines in REPORT.md; the `str.replace` matched nothing and the commit
  claimed a change it did not contain (caught only by grepping afterwards). Same failure class as the
  easy2hard lesson; a replace helper that asserts one match would have caught both.
- **Harness stall on resume**: between 08:46 and 09:33 no tool call returned (the round-2 verdict had
  been sitting on disk since 08:51). 47 min of wall clock, zero agent activity; the 50-min hard stop
  passed during it. Counted as a rate-limit-style gap, not as agent time.
- `to_markdown` renders the integer `n` column as `819.000` in every slice table (pandas floatfmt
  applied to all columns); cosmetic but it is in the report.
- Chained sub-branches: three rebases of the 02-04 chain were needed (20:40:07, 20:40:22, 20:46:44)
  to keep it on top of a moving 01; each `git commit --amend` on 01 forced another.

## What was missing
- Utility: `magic.results.to_markdown` should format integer columns as integers (`intfmt`/per-column
  floatfmt) so `n` does not print as `819.000`.
- Utility: a `hit_at_k` / rank helper next to `bootstrap_ci` (the report's Hit@1/5/25 and Wilson CI
  were computed ad hoc and are not reproducible from any script).
- Doc line (CLAUDE.md or the practice brief): "data goes in the main checkout's `data/`; worktrees get a
  symlink" existed only after the run; and "task modules live in `src/magic/tasks/`" now contradicts
  every existing epic that says `tasks/<name>.py`; pick one and say what to do with the other.
- Skill step (implement-issue): "one worktree per sub-issue (`make wt I=<name>-issue-NN`) so reviews run
  concurrently; never chain 3 issues in one worktree" — the eedi run lost ~10 min of parallelism to this.
- Makefile target: `make review` should accept `BASE=<parent sub-branch>` explicitly in its help text
  (it works via the env var, but nothing says so) and `make merge-issue B=... N=...` for the
  switch + rebase + squash + commit dance.
- Review script: save the raw reviewer transcript (not only the verdict JSON) so a rate-limited or
  killed review leaves its partial obligations table behind.
- Practice brief for a resumed run: include `git log --format='%h %ci %s' <every practice-* branch>`
  and `git reflog --date=iso` output instead of a hand-written state note.

## Reviewer behaviour
Verdict files (agent B): `runs/reviews/practice-eedi-issue-0{2,3,4}__20260903-*.json` in the eedi worktree.
Agent A's two rounds on 01 left no file (old script); reconstructed from the reflog and the run dirs.

| review | round | minutes | verdict | real problems | false positives | false negatives |
|---|---:|---:|---|---|---|---|
| 01 (agent A) | 1 | ~5-6 (20:33->~20:39) | REQUEST_CHANGES | `tasks/` not importable -> amendment; docstring said `python scripts/x.py`; no test that the correct answer's letter is dropped | unknown (no file) | - |
| 01 (agent A) | 2 | ~5-6 (20:40->20:46) | APPROVE | - | - | - |
| 02 (agent B) | 1 | 3.5 (207 s, $1.48) | APPROVE, 7/7 obligations met | - | none; 3 notes, all accurate (`n` prints as `11.000`; mistyped `--run` silently creates an empty dir; `--min-n` flag not in issue) | - |
| 03 (agent B) | 1 | 4.8 (285 s, $2.22) | APPROVE, 6/6 met | - | none; caught a real latent bug I missed: 28-char label truncation makes two subject names collide and matplotlib merges the bars (not triggered at the default 12 subjects) | - |
| 04 (agent B) | 1 | 4.2 (254 s, $1.63) | REQUEST_CHANGES, 11/12 met | finding 5 cited four numbers (0.093/n=197, 0.199/n=249, 30 %, 1,604/2,587) that no table or script produces; "largest 12 subjects" table listed 11 (a `--limit 12` counting the ALL row) | the Hit@k / name-length note is fair but the numbers do reproduce from samples.jsonl (I checked) | the run-dir sha in REPORT.md is `cf0529f`, i.e. the run predates the code commit; not flagged |
| 04 (agent B) | 2 | 5.5 (328 s, $2.50) | REQUEST_CHANGES | my rewritten finding 5 said the low and high subject groups' CIs "do not overlap"; only BIDMAS and Area of Simple Shapes are actually separated. Correct and precise (listed every overlapping pair) | none; notes: finding 2 over-generalised ("answer is a number") for two algebraic-expression constructs (true); LOG tag "(baseline)" not in the template's vocabulary (pedantic but true) | - |
| 04 (agent B) | 3 | 7.7 (464 s, $3.03) | REQUEST_CHANGES | agent A's LOG entry still listed "frequent train labels scoring worst" after finding 5 (the only place it was measured, ad hoc) had been removed; the reviewer even re-measured it (0.081 vs 0.199) and said "measure, don't assert". Real, and a consequence of my round-1 fix | none; notes: leaderboard "~0.5+" figure unverifiable (true); per-construct "top rows" table from the Goal missing (correctly non-blocking) | - |

- The reviewer runs the exact AC commands on a scratch fixture in a pristine detached checkout
  (`runs/` and `data/` are empty there, which it correctly reported as "cannot check from this worktree"
  for the Hit@k numbers). Verification runs no longer pollute the working tree (agent A's reviewer left
  two `runs/eedi_baseline__*` dirs in the worktree).
- Notes were consistently useful and never blocking-inflated: the only blocking item in 5 verdicts was
  a literal AC violation ("each citing a number from the tables"). No false positives in agent B's rounds.
- A round costs 3.5-5 min and $1.5-2.2 regardless of diff size (a 98-line diff and a 124-line docs diff
  cost the same). Three reviews in parallel finished in 4.8 min wall instead of ~12.5 serial.
- The first launch of all three reviews was lost (3.7 min, ~$4) because `scripts/review_pr.sh` in the
  main checkout was edited *and committed* (ad87fb9, 08:36:58) by another session while bash was
  executing it; bash reads scripts lazily, so the process died with `syntax error near ')'` on line 47
  after the Claude run returned. Fix: `make review` should `cp` the script to a temp file (or `bash -c
  "$(cat ...)"`) before running it, and nobody should edit the shared checkout's scripts during runs.

## Setup changes proposed
1. **`scripts/review_pr.sh` / Makefile `review`**: run from a copy (`tmp=$(mktemp); cp "$0" "$tmp"; exec bash "$tmp" "$@"`
   guard at the top) so an edit to the main checkout cannot kill in-flight reviews; also save the raw
   `claude -p` JSON next to the verdict so a rate-limited run leaves its partial obligations behind.
2. **`.claude/skills/implement-issue/SKILL.md`**: "one worktree per sub-issue (`make wt I=<name>-issue-NN BASE=<parent>`);
   start the review of issue N before coding N+1 and let it run in parallel" (eedi lost ~10 min serialising).
3. **`CLAUDE.md`**: resolve the contradiction between "task code goes in `src/magic/tasks/<name>.py`" (new) and
   the epics/issues that say `tasks/<name>.py` with `pythonpath = ["."]`; say which one wins for existing branches.
4. **Practice/resume brief**: replace the hand-written state note with generated facts
   (`git for-each-ref --format='%(refname:short) %(committerdate:iso) %(subject)' refs/heads/practice-<name>*`
   and `git reflog --date=iso` of the worktree); the eedi note said 03/04 were untouched when both were fully committed.
5. **`src/magic/results.py::to_markdown`**: format integer columns as integers (`intfmt=""`/per-column floatfmt); `n = 819.000` is in every table.
6. **`src/magic/runs.py::RunDir.__init__`**: do not `ensure_dir` when opening an existing run for reading; raise
   `FileNotFoundError` on a mistyped `--run` (both reviewers flagged the silent empty dir).
7. **`src/magic/stats.py`**: add `hit_at_k(ranks, k)` and a Wilson interval next to `bootstrap_ci`, and have
   `eedi_baseline.py`-style scripts write them to summary.json, so report prose never needs ad-hoc numbers.
8. **`src/magic/plots.py::bar_with_ci`**: de-duplicate labels (or raise) instead of letting matplotlib merge bars
   with identical truncated names.
9. **`.claude/skills/plan-issues` (or the epic template)**: the REPORT issue AC "each finding cites a number from the
   tables" is good; add "any number in the report must come from a script's table or be labelled ad hoc" so agent A's
   Hit@k / seen-vs-unseen numbers would have had a home (a `--extra-stats` in 01 or a 5th issue).
