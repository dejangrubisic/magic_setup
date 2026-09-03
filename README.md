# magic_setup

A starting point for a time-limited ML evaluation / curriculum / data-analysis task, worked by a
human plus parallel Claude Code agents: issue in, reviewed PR out.

One-time, per repo:

```
gh auth login
claude setup-token && gh secret set CLAUDE_CODE_OAUTH_TOKEN   # the CI reviewer's login
make install                                                  # env, hooks, labels, merge policy, ruleset
```

Every day:

```
make fix 12       # branch + worktree + draft PR for issue #12; cd to the printed path
make check        # lint + test, same as CI
make review 12    # the CI reviewer, locally; get APPROVE before `gh pr ready`
```

In Claude Code: `/plan-issues <task>` writes the epic and sub-issues with you and fans out one
`/fix-issue N` agent per ready issue; `/review-pr` is the procedure `make review` and CI run.

`CONTRIBUTING.md` is the contract for humans and agents; `CLAUDE.md` adds gotchas. `src/magic/`
and `tests/` hold one placeholder each: replace them with the project's code.
