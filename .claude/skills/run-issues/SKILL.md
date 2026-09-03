---
name: run-issues
description: Orchestrate parallel agents to close an epic's ready issues one PR each, respecting dependencies and disjoint file ownership. Human stays in the loop through GitHub.
disable-model-invocation: true
---
# Run issues: $ARGUMENTS

Argument: an epic number, or a list of issue numbers. Default parallelism: 3.

1. **Ready set.** Open issues, not labelled `blocked`/`needs-human`, whose "Depends on" issues are
   closed, with "Files expected to change" disjoint from issues currently in flight.
2. **Launch.** For each ready issue up to the parallelism limit, start a background agent whose whole
   prompt is: "Follow `.claude/skills/implement-issue/SKILL.md` for issue #N. Report the PR URL and
   the final verdict. Keep all scratch files inside your worktree." The skill creates its own worktree;
   do not pre-create one. Never run two agents on issues that share a file. More than three concurrent
   agents plus CI reviews can exhaust a subscription's session window. `make review` exits 3 (script)
   on a rate limit and prints the reset time: stop launching, record it in the status table, and
   resume every agent from its worktree after the reset; never restart from scratch.
3. **Loop.** When an agent finishes, record its result in a status table (issue, PR, rounds, state),
   recompute the ready set, launch the next. Merges happen one at a time through `--auto --squash`;
   an agent whose PR conflicts rebases and re-runs tests before retrying.
4. **Escalate, do not guess.** An agent that stops with `needs-human` is reported immediately with the
   question; keep the others running. Never edit an in-flight agent's worktree.
5. **Finish.** When no issue is ready and none is in flight: post the status table on the epic, list
   proposed follow-up issues, and close the epic if all sub-issues are closed.
