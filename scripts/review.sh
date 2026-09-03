#!/usr/bin/env bash
# make review N: the CI-agent review of branch issue-N against issue #N, run locally or in CI (same
# procedure: .claude/skills/review-pr/SKILL.md). Reviews a detached checkout of the committed branch,
# so keep working meanwhile. Exit 0 APPROVE, 1 REQUEST_CHANGES, 2 no verdict, 3 rate limit.
# CI=true also posts the verdict as a PR comment.
set -uo pipefail
n=${1:?usage: scripts/review.sh <issue-number>}; br="issue-$n"
root=$(git rev-parse --show-toplevel)
base=$(git rev-parse -q --verify origin/main >/dev/null 2>&1 && echo origin/main || echo main)
git rev-parse -q --verify "$br" >/dev/null || { echo "no branch $br"; exit 2; }
[[ $(git rev-list --count "$base..$br") -gt 0 ]] || { echo "no commits on $br over $base"; exit 2; }
CLAUDE=${CLAUDE:-$(command -v claude || ls -t "$HOME"/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)}
[[ -x "$CLAUDE" ]] || { echo "claude CLI not found"; exit 2; }

tmp=$(mktemp -d); git worktree add -q --detach "$tmp" "$br" || exit 2
trap 'git -C "$root" worktree remove --force "$tmp" 2>/dev/null' EXIT
[[ -d "$root/data" ]] && ln -s "$root/data" "$tmp/data"

# Signal for the reviewer: new/changed tests that PASS on the base without the change are not evidence.
new=$(git diff --name-only --diff-filter=AM "$base...$br" -- tests | grep -E '\.py$' | grep -v conftest || true)
signal="NO_NEW_TESTS"
if [[ -n "$new" ]]; then
  b=$(mktemp -d); git worktree add -q --detach "$b" "$base"
  for f in $new; do mkdir -p "$b/$(dirname "$f")"; git show "$br:$f" > "$b/$f"; done
  if (cd "$b" && uv run -q pytest -q -x -p no:cacheprovider $new >/dev/null 2>&1); then
    signal="TAUTOLOGICAL: the new/changed tests pass on $base WITHOUT the change: $new"
  else
    signal="OK: the new/changed tests fail on $base, as expected: $new"
  fi
  git -C "$root" worktree remove --force "$b" 2>/dev/null
fi

schema='{"type":"object","required":["verdict","obligations","blocking"],"properties":{"verdict":{"type":"string","enum":["APPROVE","REQUEST_CHANGES"]},"obligations":{"type":"array","items":{"type":"object","required":["text","status","evidence"],"properties":{"text":{"type":"string"},"status":{"type":"string","enum":["met","unmet","unverifiable"]},"evidence":{"type":"string"}}}},"blocking":{"type":"array","items":{"type":"string"}},"notes":{"type":"array","items":{"type":"string"}}}}'
start=$(date +%s)
out=$(cd "$tmp" && uv sync -q --locked && "$CLAUDE" -p "Read .claude/skills/review-pr/SKILL.md and follow it exactly. Issue: #$n. Branch: $br. Base: $base. Tests-on-base signal: $signal. Do not post anything; return the JSON described by the schema." \
  --output-format json --json-schema "$schema" --max-turns 80 \
  --allowedTools "Read,Glob,Grep,Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(gh issue view:*),Bash(make test),Bash(make lint),Bash(uv run pytest:*)" 2>/dev/null)
elapsed=$(( $(date +%s) - start ))
if printf '%s' "$out" | grep -q "hit your session limit"; then echo "RATE_LIMIT: $(printf '%s' "$out" | grep -o 'resets [^"]*' | head -1)"; exit 3; fi
verdict_json=$(printf '%s' "$out" | python3 -c 'import json,sys
s=json.load(sys.stdin).get("structured_output"); print(json.dumps(s, indent=2) if s else "")' 2>/dev/null)
[[ -n "$verdict_json" ]] || { echo "NO VERDICT after ${elapsed}s"; printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("result","")[:2000])' 2>/dev/null; exit 2; }
printf '%s\n' "$verdict_json"
verdict=$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')
echo "VERDICT: $verdict for $br in ${elapsed}s" >&2
if [[ "${CI:-}" == "true" ]]; then
  body=$(printf '%s' "$verdict_json" | python3 -c 'import json,sys
d=json.load(sys.stdin); L=[f"VERDICT: {d[\"verdict\"]}", "", "| Obligation | Status | Evidence |", "|---|---|---|"]
L+=[f"| {o[\"text\"]} | {o[\"status\"]} | {o[\"evidence\"]} |" for o in d["obligations"]]
if d["blocking"]: L+=["", "**Blocking**"]+[f"- {b}" for b in d["blocking"]]
if d.get("notes"): L+=["", "Notes"]+[f"- {x}" for x in d["notes"]]
print("\n".join(L))')
  gh pr comment "$br" --body "$body" >/dev/null 2>&1 || echo "could not post the PR comment" >&2
fi
[[ "$verdict" == "APPROVE" ]]
