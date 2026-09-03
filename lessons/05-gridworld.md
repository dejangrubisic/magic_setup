# Practice run 5: gridworld curriculum RL

Worktree `.claude/worktrees/practice-gridworld`, branch `practice-gridworld`. T0 = 2026-09-02 20:16 PDT.
Report: `dev/practice/gridworld/REPORT.md` (in the worktree). Five practice runs were executing
concurrently on the same machine (6 `claude` processes), which matters for the reviewer section.

## Timeline (minutes from T0)
| milestone | min | note |
|---|---|---|
| worktree ready | 0.3 | `make wt I=practice-gridworld` just works |
| docs skimmed, epic + 3 issues written | 1.5 | issues written by heredoc; no template file to copy from |
| data loaded (500-level pool + 30 held-out generated, tests green) | 3 | procedural, nothing to download |
| first baseline number | 3.5 | held-out solve rate 0.000 at 20k steps (useless); 6 min for 0.133 at 400k steps after redefining the held-out set |
| issue 01 review round 1 returned | 9.5 | verdict was for a DIFFERENT practice run (mmlupro), see below |
| first review passed (issue 01, round 2) | 17.7 | 7.6 min review wall-clock |
| first analysis table (3 curricula x 5 seeds, CIs) | 20 | 15 runs took 65 s; ran in scratchpad while review 02 was in flight |
| issue 02 merged (2 rounds) | 28 | |
| issue 03 (analysis + REPORT + LOG) committed, review started | 29 | |
| done (issue 03 merged, lessons written) | DONE_MIN | REVIEW03_NOTE |

Coding time was ~12 minutes of the total; the rest was waiting on `make review` (~REVIEW_TOTAL min across
REVIEW_ROUNDS rounds) and diagnosing why the baseline was 0.

## What helped
- `make wt`, `make lint`, `make test`, `make review BRANCH=... ISSUE=<file> BASE=<ref>` all worked
  first time; the review script accepting a local markdown issue file made the no-GitHub stand-in trivial.
- `magic.RunDir` + `magic.results.load_runs` + `bootstrap_ci` + `to_markdown` covered the whole
  results pipeline; the analysis script is 100 lines and its only custom part is the line plot.
- The reviewer's structured JSON verdict (obligations table) is easy to parse and act on; both
  REQUEST_CHANGES verdicts pointed at exactly one concrete line.
- Ruff `PT018` / `RUF046` nags are cheap to fix and the format hook keeps diffs tidy.
- The pre-commit hook rewrote `dev/LOG.md` (trailing whitespace) and failed the commit, which is
  correct, but see "got in the way".

## What got in the way
- `tasks/` is not importable from tests (`--import-mode=importlib`, no `pythonpath`) nor from
  `python scripts/x.py`. Cost ~2 min to probe, then a `pyproject.toml` edit that the reviewer (rightly)
  flagged as an out-of-scope shared-file change because the branch itself amended the issue. Had to
  land the issue amendment on the base branch and re-review: +8 min.
- Review wall-clock: 3.3 / 7.6 / 4.6 / 4.9 / REVIEW03_MIN min per round. With 5 concurrent runs on one
  laptop every review is slow, and I could not edit the worktree while a review was reading it, so I
  drafted the next issue's files in the scratchpad and copied them in afterwards (works, but fragile:
  the format hook rewrote an import block and dropped my `# noqa`, breaking the script until fixed).
- A failed pre-commit hook (whitespace auto-fix) silently left the commit un-made; the review I
  launched immediately afterwards would have reviewed an empty diff. Caught it by checking `git log`.
- The spec's held-out set (density 0.25-0.35, path >= 12) is unlearnable by a memoryless tabular
  agent: 0.000 for every curriculum, budget and observation variant tried. Spent ~4 min of
  ad-hoc sweeps to find a held-out definition with signal; that exploration lives nowhere in git
  except a paragraph in the REPORT.
- Review verdict cross-talk (see below) cost one full review round.

## What was missing
- utility: `pythonpath = ["."]` in `[tool.pytest]` and a documented way for `scripts/*.py` to import
  `tasks.*` (either `python -m scripts.x` with `scripts/__init__.py`, or a one-line `sys.path` idiom
  in the scaffold's example script). Every practice run will hit this.
- utility: `magic.plots.line_with_ci(x, mean, lo, hi, by=...)` for learning curves; `bar_with_ci`
  and `heatmap` do not cover "metric vs steps per group".
- utility: `magic.results.curves_by_group(samples_df, group, x, y)` -> bootstrap CI per (group, x);
  I wrote it inline. Also `load_runs` does not load `config.json`; I needed held-out ids from it.
- utility: a `magic.stats.bootstrap_ci` that accepts 5 values without silently giving a degenerate
  interval is fine, but a helper that says "n<10, CI is unreliable" in the table would prevent
  over-reading 5-seed intervals.
- doc line (CLAUDE.md Gotchas): "a pre-commit auto-fix hook fails the commit; re-run `git commit`"
  and "the format hook reorders imports and removes `# noqa` comments: do not put `sys.path` hacks
  above imports, use the module idiom".
- doc line: "Issue amendments must land on the base branch before the branch that needs them, or
  the reviewer blocks the shared-file change" (this is correct behaviour; it should be written down).
- Makefile target: `make review` should refuse to run when `git status` is dirty or when the branch
  has no commits over BASE (would have caught the failed-commit case), and print the elapsed time.
- Makefile target: `make sweep CMD=... ARGS="--seed {0..4}"` or a `scripts/sweep.py` pattern for
  "run one script over seeds x configs into runs/" (I wrote a bash for-loop; fine, but every run
  will).
- skill step (plan-issues): a local issue template file to copy (`dev/issue_template.md`), since
  `gh` is not available; I re-typed the template fields.
- skill step (implement-issue): "before `make review`, confirm the commit landed (`git log -1`)".

## Reviewer behaviour
- Rounds: issue 01: 2 (round 1 invalid, round 2 APPROVE); issue 02: 2 (REQUEST_CHANGES -> APPROVE);
  issue 03: REVIEW03_ROUNDS. Minutes per round: 3.3, 7.6, 4.6, 4.9, REVIEW03_MIN.
- **Cross-talk / wrong-branch verdict (severe):** issue 01 round 1 returned a full verdict for
  `practice-mmlupro-issue-01` (another concurrent practice run's branch, from another worktree),
  including its obligations table and blocking findings. The command line clearly named
  `practice-gridworld-issue-01`. Most likely cause: concurrent `claude -p` processes started from
  sibling worktrees of the same repo share session state, or the CLI resolved the repo root instead
  of the worktree. Exit code 2 (make error), so a script would not have treated it as a verdict, but
  a human skimming it would. Needs investigating before `make review` is trusted in parallel.
- False positives: none in rounds that reviewed the right branch. The pyproject.toml block on issue
  01 was technically correct (branch-authored issue amendment); resolved by landing the amendment on
  the base branch first.
- False negatives: the reviewer approved issue 01 without a test for `scripts/gridworld_train.py`
  (it noted it as non-blocking, which matches the issue text). It did not notice that the
  `test_generated_levels_are_solvable_and_far_enough` manhattan check only runs on one level.
- Real problems caught: (1) the seed-determinism test was vacuous (all solve rates 0.0 at a 500-step
  budget, so equality could not fail) - a genuine test-as-evidence failure I would have shipped;
  (2) the p_replay=0 test was too weak; (3) a modelling note that max-steps timeouts are treated as
  terminal in the Q update (correct and useful, reported as non-blocking). The reviewer also ran the
  scripts itself and reported wall-clock times and the 0.000 -> 0.133 curve, which is real evidence.
- The reviewer's notes cited exact `file:line` every time and never commented on style.

## Setup changes proposed (ranked)
1. `pyproject.toml`: add `pythonpath = ["."]` under `[tool.pytest]` and ship `tasks/__init__.py`
   plus one example `scripts/example_stage.py` showing the import idiom, so `tasks/NAME.py` works
   from tests and scripts on day one.
2. `scripts/review_pr.sh`: investigate/prevent verdict cross-talk between concurrent runs (pass the
   worktree path explicitly, `--session-id` per invocation or isolate config dir); refuse to run on a
   dirty tree or an empty diff vs BASE; print elapsed seconds and the branch/base it diffed.
3. `src/magic/plots.py`: add `line_with_ci(df, x, y, lo, hi, group, path)` for learning curves;
   `src/magic/results.py`: add `ci_by_group(df, group_cols, value_col)` returning point/lo/hi per group.
4. `CLAUDE.md` Gotchas: (a) auto-fix pre-commit hooks fail the commit, re-run it and check `git log`
   before `make review`; (b) the format hook drops `# noqa` and reorders imports; (c) issue
   amendments that add shared files must land on the base branch before the implementing branch.
5. `dev/issue_template.md` + `dev/epic_template.md` mirroring `.github/ISSUE_TEMPLATE`, so offline
   runs and `plan-issues` can copy the fields instead of re-typing them.
6. `src/magic/results.py::load_runs`: also return per-run `config.json` (flattened, prefixed
   `config.`) so scripts do not need `RunDir(...).config()` per directory.
7. `lessons/00-practice-problems.md`: for problem 5, state up front that a memoryless tabular
   agent cannot learn detours, so "hard held-out" must be defined as long-but-direct paths (or the
   agent needs memory); this run lost ~5 min rediscovering it.
