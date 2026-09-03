# Lessons

From five timed practice problems (misconception retrieval, difficulty modelling, multi-model
IRT, error clustering, RL curricula) run by parallel agents through this workflow. Full reports
live on the `practice-*` branches. Each line below changed the setup or the way we work.

## Planning
1. Issue 1 is a thin vertical slice that prints a baseline number. Every run had one in 4-16 minutes;
   everything after is comparison against it.
2. Data never matches its description. Budget 15 minutes of inspection in issue 1 and write the
   surprises into the epic (missing tables, positional ids, edited texts, renamed columns).
3. Say in the issue when the metric is a function of the ordering key, and fix the held-out
   definition before issue 2. Two runs lost time treating a degenerate result as a bug.
4. "Files expected to change" lists the test file for every module. The reviewer blocks otherwise.
5. Keep dependency chains short and file sets disjoint; run dependent issues in waves.

## Implementing
6. Never edit the issue in the implementing branch. Amend it where it lives (issue comment plus
   `gh issue edit`), then implement. Self-amended specs cost seven review rounds across five runs.
7. Branch from `origin/main` only. A branch off another issue branch conflicts on squash-merge;
   if unavoidable, `git rebase --onto origin/main <parent>` after the parent merges.
8. Confirm the commit landed (`git log -1`) before asking for a review: an auto-fix hook can fail a
   commit silently, and a review of an empty diff is wasted.
9. Test a stage script by running its `main()` on a 60-row fixture into `tmp_path`. The most repeated
   reviewer note was an untested script.
10. Write run outputs only through `magic.io` and `RunDir`: NaN is not JSON and broke two pipelines.
11. Download data once into the main checkout; worktrees get a symlink. Scratch files stay inside
    your own worktree; a shared temp dir overwrote one run's report with another's.

## Reviewing
12. The reviewer reads the issue, then the diff, then the PR text, and judges each obligation with
    `file:line` evidence. It caught a test-as-evidence failure in every run (tests that could not fail).
13. Fix false blocks upstream (a better issue or procedure), never by loosening the reviewer. Its
    only false positives were process violations that were correct under the contract.
14. Reviews take 1.5-9 minutes and run against a detached checkout, so keep working while one runs.
    Merge only on green checks; `make` exit code is not the verdict, `runs/reviews/*.json` is.

## Running many agents
15. Three parallel agents is the ceiling on one subscription; five plus their reviewers exhausted the
    session window in 34 minutes. On a rate limit, wait for the reset and resume from the worktrees;
    all state is in git.
16. Coding was 12-23 minutes of every 35-minute window; the rest was waiting on reviews. Parallel
    reviews per worktree and first-round approvals (script-level tests, exact file lists) are the levers.
