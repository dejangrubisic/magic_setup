#!/usr/bin/env bash
# Worktree per issue. `scripts/wt.sh new 12` -> .claude/worktrees/issue-12 on branch issue-12 from origin/main.
# With gh authenticated the branch is created via `gh issue develop`, so GitHub links branch <-> issue.
# A non-numeric name (`scripts/wt.sh new practice-eedi [base]`) makes a plain named worktree/branch.
# `scripts/wt.sh rm <id>` removes the worktree and the local branch once the PR is merged.
set -euo pipefail
cmd=${1:-}; issue=${2:-}; from=${3:-}
[[ -n "$cmd" && -n "$issue" ]] || { echo "usage: $0 new|rm <issue-number|name> [base-ref]"; exit 2; }
root=$(git rev-parse --show-toplevel)
if [[ "$issue" =~ ^[0-9]+$ ]]; then branch="issue-$issue"; else branch="$issue"; fi
dir="$root/.claude/worktrees/$branch"

case "$cmd" in
  new)
    if [[ -d "$dir" ]]; then echo "$dir"; exit 0; fi
    mkdir -p "$root/.claude/worktrees"
    git -C "$root" fetch -q origin 2>/dev/null || true
    if git -C "$root" show-ref -q --verify "refs/heads/$branch"; then
      git -C "$root" worktree add -q "$dir" "$branch"
    elif [[ -z "$from" && "$issue" =~ ^[0-9]+$ ]] && gh auth status >/dev/null 2>&1 && gh issue view "$issue" --json number >/dev/null 2>&1; then
      gh issue develop "$issue" --base main --name "$branch" --checkout --worktree "$dir" >/dev/null
    else
      base=${from:-$(git -C "$root" rev-parse -q --verify origin/main 2>/dev/null || git -C "$root" rev-parse main)}
      git -C "$root" worktree add -q -b "$branch" "$dir" "$base"
    fi
    [[ -f "$root/.env" ]] && cp "$root/.env" "$dir/.env"
    (cd "$dir" && uv sync -q --locked)
    [[ -d "$root/data" && ! -e "$dir/data" ]] && ln -s "$root/data" "$dir/data"   # one download, all worktrees
    echo "$dir"
    ;;
  rm)
    git -C "$root" worktree remove --force "$dir" 2>/dev/null || true
    git -C "$root" branch -d "$branch" 2>/dev/null || git -C "$root" branch -D "$branch" 2>/dev/null || true
    git -C "$root" worktree prune
    echo "removed $dir"
    ;;
  *) echo "usage: $0 new|rm <issue-number|name> [base-ref]"; exit 2 ;;
esac
