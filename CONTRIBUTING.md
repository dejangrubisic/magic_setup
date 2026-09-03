# Contributing

Rules for everyone who changes this repo: humans and agents alike. Principles, not implementation
details. If a rule here stops paying for itself, delete it.

## 1. The issue is the spec
- Every change starts as a GitHub issue with acceptance criteria that are observable and pass/fail.
  No issue, no PR. One issue, one worktree, one branch, one PR, `Closes #N` in the body.
- If the code and the issue disagree, fix the issue first (comment, get agreement), then the code.
- Ambiguous or impossible criterion: stop, comment on the issue, label `needs-human`. Do not guess.
- Anything the issue did not ask for is out of scope, even if it is an improvement. Open a new issue.
- Shared files (`pyproject.toml`, `Makefile`, `conftest.py`, `CLAUDE.md`, `.github/`, `.claude/`)
  change only in an issue that names them. New behaviour goes in new files where possible.

## 2. Definition of done
- `make lint` and `make test` pass locally and in CI.
- Every acceptance criterion has a test that fails if the behaviour is reverted.
- The PR "Testing" section contains the commands run and their actual output. "Should work",
  "probably passes", "tested manually" are not evidence.
- The CI reviewer's verdict is `APPROVE`. The reviewer is deliberately strict; the answer to a
  wrong verdict is a better issue or a better PR, not a weaker reviewer.

## 3. Tests are the reward function
- Test observable behaviour on small real inputs; assert on outputs. Mock only I/O boundaries
  (network, remote model APIs). Never mock the unit under test.
- A test with no assertion, or that asserts only on a mock, or that derives its expected value from
  the code under test, is not a test.
- Never delete, skip, xfail or weaken a test to go green. The only thing worse than a failing test is
  a reduction in test coverage. If a test is wrong, say so in the PR and let a human decide.
- No placeholder or stub implementations. If you cannot finish, leave the failing test and say so.
- Tests are deterministic (seeds), fast (seconds), and independent of network and API keys.

## 4. Evidence before claims
Before saying anything works: name the command that proves it, run it fresh, read the whole output
including exit code and failure counts, confirm it supports the claim, then say it with the output
attached. Fix root causes; do not suppress errors.

## 5. Simplicity
- Use libraries (pandas, numpy, sklearn, anthropic) directly. No wrapper layers, no config trees,
  no new abstraction or dependency without one sentence in the PR saying why.
- Plain functions, small dataclasses, one script per pipeline stage, one file per task.
- Delete code that is no longer used. Do not keep "just in case" branches.

## 6. Data and experiments
- `data/raw` is immutable and never committed. Everything else is regenerable from scripts.
  Only tiny test fixtures live in git.
- Results are produced only by scripts (never by notebooks) into `runs/<run>/`: the exact config,
  an append-only per-sample log, and a summary written last. Runs are resumable by sample id.
- Every model call is cached on disk. Every run records seed, git sha, model and prompt version.
- Score with both a strict and a lenient extractor when parsing model output, so "wrong format"
  is separated from "wrong answer".
- Report uncertainty (bootstrap or Wilson intervals) with every headline number.
- Append every experiment, including negative results, to `dev/LOG.md`: what changed, result vs
  baseline, keep/drop decision.

## 7. Working with agents
- One issue per session, in its own worktree (`make fix N`). Fresh context for the next issue.
- Corrected an agent twice on the same thing? Start over with a better first prompt.
- Every agent brief has: objective, output format, tools to use, and what is out of scope.
- Reviews happen in a fresh context (`make review N` locally, the `review` job in CI, same
  procedure). A local APPROVE precedes every `gh pr ready`. An agent never reviews its own diff in
  the context that wrote it.
- When the reviewer or a human catches a mistake an agent should not have made, the fix PR also
  adds one line to the Gotchas section of `CLAUDE.md`. Remove lines that stop earning their place.
- State lives in git, issues and files, never only in a conversation. Commit small and often.

## 8. Git
- Branch `issue-N`; rebase on `origin/main` before opening the PR; squash-merge; the PR title is the
  commit subject: `<type>: <what> (#N)`.
- Never force-push a shared branch, never commit directly to `main`, never commit data or secrets.
