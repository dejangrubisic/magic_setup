#!/usr/bin/env bash
# Reviewer signal: do the branch's new/changed tests PASS against the base WITHOUT the change?
# If they do, they do not exercise the change (tautological or over-mocked) and are not evidence.
#   scripts/tests_on_base.sh [base=origin/main] [head=HEAD]
set -uo pipefail
base=${1:-origin/main}; head=${2:-HEAD}
git rev-parse -q --verify "$base" >/dev/null 2>&1 || base=main
new=$(git diff --name-only --diff-filter=AM "$base...$head" -- tests/ | grep -E '\.py$' | grep -v conftest || true)
[[ -n "$new" ]] || { echo "NO_NEW_TESTS between $base and $head"; exit 0; }
tmp=$(mktemp -d)
git worktree add -q --detach "$tmp" "$base" 2>/dev/null || { echo "could not create base worktree"; exit 0; }
for f in $new; do mkdir -p "$tmp/$(dirname "$f")"; git show "$head:$f" > "$tmp/$f"; done
if (cd "$tmp" && uv run -q pytest -q -x -p no:cacheprovider $new > "$tmp/out.txt" 2>&1); then
  echo "SIGNAL_TAUTOLOGICAL: new/changed tests PASS against $base without the change: $new"
else
  echo "OK: new/changed tests fail or error against $base, as expected: $new"
fi
tail -12 "$tmp/out.txt"
git worktree remove --force "$tmp" 2>/dev/null
