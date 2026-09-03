# Scenarios: what happens when the real task arrives, and what we do about it

Written after the research pass and five practice runs. Each scenario: what goes wrong, what the
setup already does, what remains for the humans in the room.

## 1. Minute zero: the task lands as a paragraph and a dataset link
- **Risk:** an hour lost to environment, credentials and "where does this code go".
- **Setup:** `make doctor` lists what is missing; `make install` is one command; utilities for
  JSONL, run dirs, cached model calls, splits, CIs, tables and plots exist and are tested; a template
  task (`src/magic/tasks/example.py`) and stage script (`scripts/example_stage.py`) show the shape.
- **Human:** run `/plan-issues` with the task text. The first issue is always the thin vertical
  slice that prints a baseline number. Do not let anyone start coding before issue 1 is written.

## 2. The data is not what the description says
- **Risk:** every practice run hit a schema surprise (missing category in a table, positional ids,
  edited question texts, column names differing between configs). This is the norm, not the exception.
- **Setup:** issues say "inspect columns first"; loaders live in one task module so the fix is in
  one place; fixtures are 60-row slices of the real file so tests catch the surprise early.
- **Human:** budget 15 minutes for data archaeology in issue 1 and write what you found into the
  epic (the livebench run did this well: "Data finding (T+3 min): ...").

## 3. Data needs credentials (Kaggle) or is huge
- **Risk:** blocked download, or a 2 GB file per worktree.
- **Setup:** the practice table lists no-auth mirrors for common competition data; `data/` is
  gitignored and the HF cache is shared across worktrees; `datasets` and `curl` patterns are in the
  lessons.
- **Human:** put `~/.kaggle/kaggle.json` in place before the task if Kaggle is likely; download once
  into the main checkout's `data/raw` and symlink from worktrees.

## 4. Parallel agents and the subscription window
- **Risk:** five agents plus five reviewers exhausted the session limit in ~35 minutes and every
  run died mid-issue. Agents that share a scratch directory overwrote each other's files.
- **Setup:** `run-issues` caps parallelism at three and says to resume, not restart; worktrees are
  the only scratch space; review verdicts are saved per branch and carry the branch name.
- **Human:** use an API key (not the subscription token) for CI so reviews do not compete with local
  agents; if a limit hits, wait for the reset and resume from the worktrees (state is all in git).

## 5. Chained issues
- **Risk:** issue 2 branched from issue 1's branch conflicts on squash-merge after issue 1 lands.
- **Setup:** CLAUDE.md gotcha and the implement skill: branch from `origin/main` only; wait for the
  dependency to merge; rebase before the PR.
- **Human:** in `/plan-issues`, keep dependency chains short and files disjoint; run dependent issues
  in waves.

## 6. The reviewer blocks something legitimate
- **Risk:** a shared-file edit (pyproject) that the issue did not name gets blocked; the agent
  fights the reviewer instead of fixing the issue.
- **Setup:** the reviewer is right by design; the fix is an issue amendment landed on `main` first,
  then re-review. Only a human can override (`gh pr merge --admin`, logged in `dev/LOG.md`).
- **Human:** treat every override as a signal to improve the issue template or the skill, not to
  loosen the reviewer.

## 7. The reviewer takes 3-8 minutes per round
- **Risk:** agents idle waiting; five concurrent reviews on one laptop are slow.
- **Setup:** reviews run in parallel per worktree; the review script prints elapsed time and cost;
  a local review before the PR means CI usually approves in one round.
- **Human:** while a review runs, the agent drafts the next issue's tests inside its worktree (never
  edit files the reviewer is reading). Consider `--model claude-sonnet-5` in `make review` for
  quick pre-checks and keep the CI reviewer on the strong model.

## 8. Tests that cannot fail
- **Risk:** agents ship tests that pass without the change (seen once: a determinism test where every
  value was 0.0). This is the highest-value catch the reviewer makes.
- **Setup:** `scripts/tests_on_base.sh` mechanically runs new tests against the base; the reviewer
  treats a pass as "not evidence".
- **Human:** when reading a PR, read the tests first and ask "what would make this fail".

## 9. The metric is degenerate or the baseline is zero
- **Risk:** a held-out set no baseline can solve (gridworld), or a metric that is a function of the
  ordering key (easy2hard). Agents burn time treating it as a bug.
- **Setup:** `/plan-issues` says to state such couplings in the issue; `dev/LOG.md` records the
  exploration so the next agent does not redo it.
- **Human:** decide the held-out definition and the target metric before issue 2 starts.

## 10. Time is almost up
- **Risk:** half-finished issues, no report.
- **Setup:** every stage script writes resumable run dirs and a summary table; `magic.results` turns
  them into markdown; the REPORT issue is always the last issue and has priority over extra analysis.
- **Human:** at T-60 minutes, stop opening new issues; at T-30, only the report issue remains.

## What still needs GitHub to be tested end to end
`gh auth login`, `make gh-setup`, one secret, the Claude GitHub App, then one throwaway issue and PR
to watch `lint`, `test`, `pr-links-issue` and `review` go green and auto-merge. Until then the whole
loop has only been exercised with local worktrees and the local reviewer.
