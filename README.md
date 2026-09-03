# magic_setup

A repository prepared to move fast on a time-limited ML evaluation / curriculum / data-analysis
task with a human plus parallel Claude Code agents.

```
make install                      # uv env + git hooks (once)
make check                        # lint + test, same as CI
/plan-issues <task description>   # in Claude Code: write the epic + sub-issues together
/run-issues <epic>                # parallel agents, one worktree + PR per issue, CI agent reviews
```

Before the first issue on a new repo: `gh auth login`, `make gh-setup` (labels, squash-only
auto-merge, ruleset requiring `lint`, `test`, `pr-links-issue`, `review`), the Claude GitHub App
(https://github.com/apps/claude), and one secret: `gh secret set CLAUDE_CODE_OAUTH_TOKEN`
(from `claude setup-token`) or `ANTHROPIC_API_KEY`.

- `CONTRIBUTING.md` is the contract for humans and agents; `CLAUDE.md` adds commands and gotchas.
- `.claude/skills/` holds the three procedures: plan issues, implement one issue, review a PR.
- `.github/workflows/claude-review.yml` is the CI agent: it judges every PR against its issue and
  fails the `review` check unless the verdict is APPROVE. `make review` runs the same procedure locally.
- `src/magic/` has the utilities every such task needs: JSONL I/O, resumable run dirs, cached LLM
  calls, stable splits and seeds, bootstrap/Wilson intervals, results tables, three plots;
  `magic/tasks/example.py` and `scripts/example_stage.py` are the templates to copy.
- `dev/LOG.md` is the experiment log; `LESSONS.md` is what the practice runs taught us.
