@CONTRIBUTING.md

## Commands
| `make install` | once per clone: env + git hooks | | `make lint` | format check + lint + lock check |
| `make test` | fast parallel tests | | `make check` | lint + test (what CI runs) |
| `make wt I=N` / `make wt-rm I=N` | worktree for issue N / remove it | | `make review BRANCH=issue-N ISSUE=N` | local CI-agent review |
| `uv run pytest tests/test_x.py::test_y -x` | one test | | `uv add <pkg>` | add a dependency (re-locks) |

## Workflow skills
`/plan-issues <task>` (plan, create, then fan out `/implement-issue N` agents) -> `/review-pr N`.
Run `make review` before every PR. Read the skill file before acting on one.

## Gotchas
- Task code goes in `src/magic/tasks/<name>.py` (importable everywhere); `scripts/` at the repo
  root is not on `sys.path`. Run `make format` before committing; the pre-commit hook fixes and
  then fails the commit if it had to change anything.
- A pre-commit auto-fix (whitespace, ruff) fails the commit and leaves it un-made: re-run `git commit`
  and check `git log -1` before `make review`; the review script refuses empty diffs and dirty trees.
- Branch every issue from `origin/main`, never from another issue branch; if it depends on one, wait
  for that PR to merge. Issue amendments that touch shared files land on `main` first.
- Parallel agents: use your own worktree (or `runs/`) for scratch files, never a shared temp dir.
  `data/` is symlinked into every worktree by `make wt`; download once, in the main checkout.
- Write run outputs through `magic.io`/`RunDir` only: they turn NaN into null (NaN is not JSON).
- `uv run` re-syncs the env on every call; a stale `uv.lock` fails `make lint` (`uv lock` fixes it).
- The Claude binary may not be on PATH; `make review` finds the IDE-bundled one automatically.
- `datasets.load_dataset` caches under `~/.cache/huggingface`; large downloads go in `data/raw` and
  are gitignored. Never commit `.parquet`, `.csv`, `.jsonl` outside `tests/fixtures`.
- pytest runs with `strict = true`: unknown markers and unregistered fixtures are errors; register
  markers in `pyproject.toml`.
