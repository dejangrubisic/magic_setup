@CONTRIBUTING.md

## Commands
| `make install` | once per clone | | `make check` | lint + test, same as CI |
| `make fix N` | branch + worktree + draft PR; prints the path to `cd` into | | `make review N` | the CI reviewer, locally; APPROVE before `gh pr ready` |
| `uv run pytest tests/test_x.py::test_y -x` | one test | | `uv add <pkg>` | add a dependency (re-locks) |

## Skills
`/plan-issues <task>` -> one `/fix-issue N` agent per ready issue -> `/review-pr` (used by `make review` and CI).
Read the skill file before acting on one.

## Gotchas
- Nobody commits to `main`, the owner included; every change is issue -> `make fix N` -> PR -> squash.
- A pre-commit auto-fix fails the commit and leaves it un-made: re-run `git commit`, check `git log -1`.
- Branch every issue from `origin/main`, never from another issue branch; if it depends on one, wait
  for that PR to merge. Issue amendments live on the issue, never in the implementing branch.
- `data/` and `runs/` are gitignored; download once in the main checkout (`make fix` symlinks `data/`).
  Never write `NaN` into JSON outputs; keep scratch files inside your own worktree.
- `uv run` re-syncs the env on every call; a stale `uv.lock` fails `make lint` (`uv lock` fixes it).
- `make review` and the CI `review` job share your subscription window; three parallel agents is the
  practical ceiling. On a rate limit, wait for the reset and resume from the worktrees.
