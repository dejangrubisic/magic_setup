---
name: plan-issues
description: Turn a task description into a GitHub epic with ordered, parallelisable sub-issues that agents can implement without asking questions. Run together with the human before any code is written.
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
   - Data download/caching, evaluation harness, and analysis/report are separate issues.
3. **Review with the human.** Show the plan as a table (number, title, depends-on, files, one-line
   AC). Iterate until approved. Ask a fresh `reviewer` subagent to poke holes (ambiguity, missing
   criteria, hidden shared files) before the human sees it.
4. **Create.** `gh issue create --label epic ...` for the epic, then each task with
   `gh issue create --label task --title ... --body-file ...`. Link sub-issues:
   `gh api -X POST repos/{owner}/{repo}/issues/<epic>/sub_issues -F sub_issue_id=$(gh api repos/{owner}/{repo}/issues/<task> --jq .id)`.
   Post the dependency order and the parallel waves in the epic body.
5. **Hand off.** Print the ready queue (open issues whose dependencies are closed), grouped into
   waves that can run concurrently. Then `/run-issues <epic>`.
