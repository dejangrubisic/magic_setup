#!/usr/bin/env bash
# make fix N: branch issue-N linked to issue #N, worktree, synced env, data symlink, empty first
# commit and a draft PR ("Closes #N"). Prints the worktree path last; cd there and implement.
set -euo pipefail
n=${1:?usage: scripts/fix_issue.sh <issue-number>}
root=$(git rev-parse --show-toplevel); br="issue-$n"; dir="$root/.claude/worktrees/$br"
git -C "$root" fetch -q origin 2>/dev/null || true
if [[ ! -d "$dir" ]]; then
  mkdir -p "$root/.claude/worktrees"
  if git -C "$root" show-ref -q --verify "refs/heads/$br"; then
    git -C "$root" worktree add -q "$dir" "$br"
  elif gh auth status >/dev/null 2>&1; then
    gh issue develop "$n" --base main --name "$br" --checkout --worktree "$dir" >/dev/null
  else
    git -C "$root" worktree add -q -b "$br" "$dir" "$(git -C "$root" rev-parse -q --verify origin/main || git -C "$root" rev-parse main)"
  fi
fi
cd "$dir"
uv sync -q --locked
[[ -d "$root/data" && ! -e data ]] && ln -s "$root/data" data
[[ -f "$root/.env" && ! -e .env ]] && cp "$root/.env" .env
if gh auth status >/dev/null 2>&1; then
  if [[ -z "$(git log --oneline origin/main..HEAD 2>/dev/null)" ]]; then
    git commit -q --allow-empty -m "wip: start #$n" && git push -q -u origin "$br"
  fi
  if ! gh pr view "$br" --json number >/dev/null 2>&1; then
    gh pr create --draft --head "$br" --title "$(gh issue view "$n" --json title --jq .title) (#$n)" --body "Closes #$n" >/dev/null
  fi
fi
echo "$dir"
