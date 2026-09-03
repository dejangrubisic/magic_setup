# magic_setup

A repository prepared to move fast on a time-limited ML evaluation / curriculum / data-analysis
task with a human plus parallel Claude Code agents.

```
make install                      # uv env + git hooks (once)
make check                        # lint + test, same as CI
/plan-issues <task description>   # in Claude Code: write the epic + sub-issues together
/run-issues <epic>                # parallel agents, one worktree + PR per issue, CI agent reviews
```

- `CONTRIBUTING.md` is the contract for humans and agents; `CLAUDE.md` adds commands and gotchas.
- `.claude/skills/` holds the workflow procedures; `.claude/agents/reviewer.md` the fresh-context reviewer.
- `.github/workflows/claude-review.yml` is the CI agent: it judges every PR against its issue and
  fails the `review` check unless the verdict is APPROVE. `make gh-setup` configures the repo once.
- `src/magic/` has the utilities every such task needs: JSONL I/O, resumable run dirs, cached LLM
  calls, stable splits, bootstrap/Wilson intervals, results tables, two plots.
- `dev/LOG.md` is the experiment log; `lessons/` holds what practice runs taught us.
