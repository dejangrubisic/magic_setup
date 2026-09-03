---
name: implement-issue
description: Implement one GitHub issue end to end in its own worktree, open a PR, get it through CI and the agent reviewer, merge, clean up. The standard unit of agent work.
disable-model-invocation: true
---
# Implement issue #$ARGUMENTS

Work in the issue's own worktree. One issue, one branch, one PR. Stop and ask a human (label
`needs-human`, comment why) rather than guess when the issue is ambiguous or blocked.

1. **Read.** `gh issue view $ARGUMENTS`. Check "Depends on" issues are closed. If any acceptance
   criterion is ambiguous, impossible, or contradicts the code, comment on the issue and stop.
   **Amendments.** If the data contradicts a criterion (missing column, different format, impossible
   threshold), never edit the issue text in your branch. Amend it where it lives: `gh issue edit` plus a
   comment starting `Amendment:` with the reason (a human ratifies), or for a local issue file a separate
   `docs: amend issue N` commit on the base branch, then rebase. Shared-file edits the amendment permits
   go in that same base commit. Only then implement.
2. **Worktree.** `make wt I=$ARGUMENTS` prints the path; `cd` there. Every command below runs inside it.
3. **Plan** (only if more than one file changes): post a short comment on the issue: files to
   touch, what is NOT being done, how each criterion will be verified. If the diff fits one sentence, skip.
4. **Test first.** For each criterion write the failing test, then the code. Real inputs, real
   outputs; mock only network/API. A stage script's criterion is tested by running its `main()` on a
   fixture into `tmp_path` (see `tests/test_tasks_example.py`). No placeholders or stubs: if you cannot finish, leave the failing
   test and say so in the PR. Touch only the files the issue lists; new behaviour goes in new files.
5. **Green.** `make lint && make test`. Fix root causes; never skip, weaken or delete tests.
   Commit after each green run with a message that says why, and confirm with `git log -1` (an
   auto-fix hook can fail the commit silently).
6. **Fresh-context review.** Run `make review BRANCH=issue-$ARGUMENTS ISSUE=$ARGUMENTS` (or ask the
   `reviewer` subagent). It reviews a pristine checkout of your branch, so keep working meanwhile. Fix
   every blocking finding; re-run until `VERDICT: APPROVE` (`make` exits 2 on any failure; the verdict
   JSON is in `runs/reviews/`). While a review runs you may start a dependent issue from this branch;
   before *its* review, once this one has merged, `git rebase --onto origin/main issue-$ARGUMENTS` and
   `make test`.
7. **PR.** `git fetch origin && git rebase origin/main && make test`, `git push -u origin issue-$ARGUMENTS`,
   then `gh pr create --title "<type>: <what> (#$ARGUMENTS)" --body-file <file>` using the PR
   template: `Closes #$ARGUMENTS`, what/why, and a Testing section with pasted command output.
8. **CI.** `gh pr checks --watch`. If `review` fails, read the reviewer's `VERDICT:` comment
   (`gh pr view --comments`), fix, push. No `VERDICT:` comment at all means the run died (auth, turns):
   `gh run rerun --failed` once. After three review rounds, stop: label `needs-human` and report.
   Only a human may override a verdict (`gh pr merge --admin`), and they log why in `dev/LOG.md`.
9. **Merge.** `gh pr merge --auto --squash`, then poll `gh pr view --json state,mergedAt` until merged.
10. **Clean.** `cd` back to the main checkout, `make wt-rm I=$ARGUMENTS`. If the issue produced an
    experimental result, append a dated entry to `dev/LOG.md` (in its own tiny PR or the same one if
    the issue asked for it).
11. **Report.** PR URL, review rounds, anything the reviewer caught that an agent should have known.
    Propose that as a one-line addition to the Gotchas in `CLAUDE.md` (do not edit it yourself).
