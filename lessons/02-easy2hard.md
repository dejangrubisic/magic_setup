# 02 — easy2hard (E2H-GSM8K difficulty prediction, residuals, curriculum)

T0 = 2026-09-02 20:16 PDT. Worktree `.claude/worktrees/practice-easy2hard`, branch `practice-easy2hard`
(sub-branches `practice-easy2hard-issue-0{1,2,3,4}`, each in its own worktree so reviews could run
concurrently). Deliverable: `dev/practice/easy2hard/REPORT.md` on `practice-easy2hard`.

## Timeline
| milestone | min from T0 |
|---|---:|
| worktree ready (`make wt`, includes `uv sync`) | 0.5 |
| data loaded (HF download of both configs, columns inspected; ran while reading docs) | 1 |
| docs skimmed (CONTRIBUTING, CLAUDE, 3 skills, all of `src/magic`) | 3 |
| epic + 4 issue files committed | 2 |
| issue 01 code + tests green (two real bugs caught by tests, see below) | 5 |
| first baseline number (length-only Spearman 0.261 [0.135, 0.374]) | 16 |
| first analysis table (3 models + residuals-by-quantile + 10 worst, issue 02 green) | 18 |
| curriculum curves with 5 seeds (issue 03 green) | 20 |
| first review passed (01 APPROVE) | 20 |
| 02 APPROVE, 03 REQUEST_CHANGES (legit), 03 fixed + rerun | 27 |
| REPORT.md + LOG entry committed (04) | 29 |
| done (03 re-review + 04 review, merges, lessons) | DONE_MIN |

Coding was ~12 minutes of the total; the rest was waiting for the reviewer (4-5 min per round,
run in parallel where possible) and recovering from two environment collisions (below).

## What helped
- `make wt I=<name> BASE=<ref>` with named worktrees: one worktree per sub-issue meant three
  reviews (each runs `make test` on its working tree) could run concurrently without stepping on
  each other. This is the single biggest wall-clock saver.
- `magic.stable_split`, `magic.bootstrap_ci`, `magic.RunDir`, `magic.write_jsonl/read_jsonl`,
  `magic.to_markdown` covered every I/O and stats need; no new dependency was needed.
- The 60-row fixture pattern (`head -60 data/raw/... > tests/fixtures/...jsonl`, allowed by
  `.gitignore`) made every script testable end to end in ~3 s without network.
- Tests-first caught two real bugs in issue 01 within seconds: the sentence regex split "$1.50"
  into two sentences, and the bootstrap Spearman CI went NaN on constant resamples.
- The review skill's obligations table is precise enough that a REQUEST_CHANGES is actionable in
  one read (it quoted the exact line and the reproduction).
- `datasets.load_dataset` for a <5 MB dataset is instant; the "inspect columns first" step in the
  brief was the right call (AMC has different column names: problem/solution).

## What got in the way
- **Squash-merging chained sub-branches gives add/add conflicts.** issue-02 was branched from
  issue-01; after squash-merging 01 into the base, `git merge --squash issue-02` conflicted on
  every file both touched. Resolution (`git checkout --theirs`) is trivial but undocumented; a
  `-X theirs` or a rebase step belongs in the skill.
- **The scratchpad directory is shared between sibling practice agents.** My `review02.txt` got
  another run's (gridworld) verdict appended, and my `REPORT.md` draft was overwritten by the
  livebench run. Lost ~3 min and could have shipped wrong numbers. Prefix scratch files or use a
  per-run subdirectory.
- **Auto-format hook + text replacement**: a formatter re-wrapped `write_config(...)` between my
  edits, so a scripted replace silently matched nothing and the subsample fix was a no-op on the
  first try (caught only because I looked at samples.jsonl). CLAUDE.md warns about this; the
  warning is right, but a replace that matches nothing should be an error in my tooling.
- `tasks/` is not importable: every script and test needs `sys.path.insert(0, ROOT)` plus
  `# noqa: E402` on the imports. Pure boilerplate, repeated in 6 files.
- `magic.bootstrap_ci` takes a 1-D array; a paired statistic (Spearman over items) needs the
  index-array trick (`bootstrap_ci(np.arange(n), stat=lambda idx: rho(y[idx], p[idx]))`), which
  is non-obvious and produced NaNs when a resample was constant (`np.percentile`, not
  `nanpercentile`).
- `magic.plots` has bar and heatmap only; a learning-curve line plot with CI bands had to be
  written by hand in the script.
- `ruff RUF001` rejects a literal `×` in a regex character class; needed `×` escapes.
- Reviewer verification runs leave `runs/easy2hard_*` directories in the worktree (gitignored,
  harmless, but they clutter `ls runs/` and the reviewer itself flagged it).

## What was missing
- Utility: `magic.stats.bootstrap_ci` should accept a `stat` over row indices (or a
  `paired_bootstrap(stat, *arrays)`) and use `nanpercentile`.
- Utility: `magic.plots.lines_with_ci(x, {name: (mean, lo, hi)}, path=)` for learning curves.
- Doc line (CLAUDE.md Gotchas): "`tasks/` is not on `sys.path`; scripts/tests start with
  `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` + `# noqa: E402`", or better a
  `pythonpath = ["."]` under `[tool.pytest]` and `tasks/__init__.py` so it is importable.
- Skill step (implement-issue / practice procedure): after the parent issue merges, rebase the
  child sub-branch onto the base before `merge --squash`, or squash with `-X theirs`.
- Makefile target: `make merge-issue B=<branch> N=<nn> MSG=...` doing switch + squash + commit.
- Skill step (plan-issues): when the target metric is a function of the ordering key (here:
  difficulty label vs easy->hard order), say so in the issue so the reviewer/implementer does not
  treat degenerate curves as a bug.
- Practice brief: state that the scratchpad is shared across concurrent practice agents.
