---
name: fix-issue
description: Implement one GitHub issue end to end. Load this first, run `make fix N`, work in the printed worktree, get a local APPROVE, then the PR through CI to a squash merge.
disable-model-invocation: true
---
# Fix issue #$ARGUMENTS

One issue, one worktree, one PR. Stop and ask a human (label `needs-human`, comment why) rather than
guess when the issue is ambiguous, impossible, or contradicts the code.

1. **Read.** `gh issue view $ARGUMENTS`. "Depends on" issues must be closed. If the data or code
   contradicts a criterion, do not edit the issue text in your branch: amend it where it lives
   (`gh issue edit` plus a comment starting `Amendment:` with the reason), then implement.
2. **Start.** `make fix $ARGUMENTS` creates branch `issue-$ARGUMENTS`, the worktree, a draft PR, and
   prints the worktree path. `cd` there; every command below runs inside it, with absolute paths.
3. **Plan** (only if more than one file changes): a short comment on the issue with the files, what
   is not being done, and how each criterion will be verified.
4. **Test first.** For each criterion write the failing test, then the code. Real inputs and outputs;
   mock only network or paid APIs. No placeholders: if you cannot finish, leave the failing test and
   say so in the PR. Touch only the files the issue lists; new behaviour goes in new files.
5. **Green.** `make lint && make test`. Fix root causes; never skip, weaken or delete a test. Commit
   after each green run with a message that says why, and check `git log -1` (a hook can fail a commit).
6. **Local review, mandatory.** `make review $ARGUMENTS` reviews a checkout of your committed branch,
   so keep working meanwhile. Fix every blocking finding and re-run until `VERDICT: APPROVE`. Do
   not mark the PR ready before that.
7. **PR.** `git fetch origin && git rebase origin/main && make test`, `git push`, then edit the PR
   body to the template (`Closes #$ARGUMENTS`, what and why, the commands you ran with their
   output) and `gh pr ready`.
8. **CI.** `gh pr checks --watch --fail-fast`. If `review` fails, read its `VERDICT:` comment, fix,
   push. After three rounds stop: label `needs-human` and report. Only a human overrides a verdict.
9. **Merge.** Only when every check is green: `gh pr merge --auto --squash` (or `--squash` if
   auto-merge is unavailable). Poll `gh pr view --json state` until merged.
10. **Clean.** From the main checkout: `git worktree remove .claude/worktrees/issue-$ARGUMENTS`,
    `git branch -d issue-$ARGUMENTS`. Append a `dev/LOG.md` entry if the issue produced a result.
11. **Report.** PR URL, review rounds, and anything the reviewer caught that an agent should have
    known; propose it as one line for the Gotchas in `CLAUDE.md` (do not edit it yourself).
