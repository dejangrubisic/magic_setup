---
name: plan-issues
description: Turn a task description into a GitHub epic with ordered, parallelisable sub-issues, then fan out one implement-issue agent per ready issue. Run together with the human before any code is written.
disable-model-invocation: true
---
# Plan issues for: $ARGUMENTS

The issues are the spec. Time spent here is the highest-leverage time in the project: a bad line in
an issue becomes hundreds of bad lines of code.

1. **Understand.** Read the task (inline text or file). Restate: goal, deliverables, deadline, the
   single metric or artifact that shows success, and the data involved. List open questions; ask the
   human now if any would change the plan.
2. **Slice.** Draft one epic and 4-10 task issues. Rules:
   - Issue 1 is a thin end-to-end vertical slice (load data -> run -> result table) that lands in
     under an hour and gives a baseline number. Everything after improves it.
   - Each issue: Goal, Acceptance criteria (observable, pass/fail, naming the test or command),
     Out of scope, Files expected to change, Depends on. Use the Task issue template body.
   - Files expected to change are disjoint across issues that can run in parallel. Shared files
     (`pyproject.toml`, `Makefile`, `conftest.py`, `CLAUDE.md`) change only in a dedicated issue.
   - Prefer more small issues over fewer big ones; an agent should finish one in 20-60 minutes.
   - Data download/caching, evaluation harness, and analysis/report are separate issues. Issue 1
     includes a 10-line inspection (shape, columns, join-key value counts, duplicates) recorded under
     `## Data findings` in the epic; schema surprises are the norm, not the exception.
   - "Files expected to change" always lists `tests/test_<module>.py` for every module it lists.
   - If the metric is a function of the ordering key (e.g. difficulty label used both to order a
     curriculum and to score it), say so in the issue so degenerate results are not treated as bugs.
   - Without GitHub (offline), an issue is a markdown file with the same five fields:
     `## Goal`, `## Acceptance criteria`, `## Out of scope`, `## Files expected to change`, `## Depends on`.
3. **Review with the human.** Show the plan as a table (number, title, depends-on, files, one-line
   AC). Iterate until approved. Ask a fresh `reviewer` subagent to poke holes (ambiguity, missing
   criteria, hidden shared files) before the human sees it.
4. **Create.** `gh issue create --label epic ...` for the epic, then each task with
   `gh issue create --label task --title ... --body-file ...` (the number is the tail of the printed
   URL: `| grep -oE '[0-9]+$'`). Link sub-issues:
   `gh api -X POST repos/{owner}/{repo}/issues/<epic>/sub_issues -F sub_issue_id=$(gh api repos/{owner}/{repo}/issues/<task> --jq .id)`.
   Post the dependency order and the parallel waves in the epic body.
5. **Run.** Ready set = open issues, not `blocked`/`needs-human`, dependencies closed, files disjoint
   from issues in flight. For each ready issue (at most three at a time) start a background agent whose
   whole prompt is: "Follow `.claude/skills/implement-issue/SKILL.md` for issue #N. Keep scratch files
   inside your worktree. Report the PR URL and the final verdict." When one finishes, record it in a
   status table (issue, PR, review rounds, state), recompute the ready set, launch the next. Escalate
   `needs-human` stops immediately and keep the others running; never touch an in-flight worktree. On a
   rate limit (`make review` exit 3 prints the reset time) stop launching and resume from the worktrees
   after the reset. When nothing is ready or in flight: post the status table on the epic and close it
   if every sub-issue is closed.
