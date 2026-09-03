#!/usr/bin/env bash
# Local run of the CI reviewer, same procedure as .github/workflows/claude-review.yml.
#   scripts/review_pr.sh 12                 # review PR #12 (needs gh auth)
#   scripts/review_pr.sh issue-12 12        # review local branch issue-12 against issue #12
#   scripts/review_pr.sh issue-12 spec.md   # ... against an issue written in a local markdown file
#   BASE=<ref> scripts/review_pr.sh ...     # diff against <ref> instead of origin/main
# Exit 0 on APPROVE, 1 on REQUEST_CHANGES, 2 on no verdict / precondition failure.
# The JSON verdict is printed and saved to runs/reviews/<target>__<timestamp>.json (gitignored).
set -uo pipefail
target=${1:-}; issue=${2:-}; base=${BASE:-}
[[ -n "$target" ]] || { echo "usage: $0 <pr-number|branch> [issue-number|issue-file]"; exit 2; }
CLAUDE=${CLAUDE:-$(command -v claude || ls -t "$HOME"/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)}
[[ -x "$CLAUDE" ]] || { echo "claude CLI not found; set CLAUDE=/path/to/claude"; exit 2; }

if [[ "$target" =~ ^[0-9]+$ ]]; then
  args="$target"; label="pr-$target"
else
  [[ -n "$issue" ]] || { echo "branch mode needs an issue number or file"; exit 2; }
  git rev-parse -q --verify "$target" >/dev/null || { echo "no such branch: $target"; exit 2; }
  ref=${base:-$(git rev-parse -q --verify origin/main >/dev/null 2>&1 && echo origin/main || echo main)}
  # Preconditions that have burned people: reviewing an empty diff (commit failed) or a dirty tree.
  if [[ "$(git branch --show-current)" == "$target" && -n "$(git status --porcelain)" ]]; then
    echo "working tree is dirty on $target; commit first (the reviewer reads committed state)"; exit 2
  fi
  n=$(git rev-list --count "$ref..$target"); [[ "$n" -gt 0 ]] || { echo "no commits on $target over $ref; nothing to review"; exit 2; }
  echo "reviewing $target ($n commits over $ref) against $issue" >&2
  args="branch=$target issue=$issue base=$ref"; label="$target"
fi

schema='{"type":"object","required":["target","verdict","obligations","blocking"],"properties":{"target":{"type":"string","description":"the PR number or branch you reviewed, verbatim from the arguments"},"verdict":{"type":"string","enum":["APPROVE","REQUEST_CHANGES"]},"obligations":{"type":"array","items":{"type":"object","required":["text","status","evidence"],"properties":{"text":{"type":"string"},"status":{"type":"string","enum":["met","unmet","unverifiable"]},"evidence":{"type":"string"}}}},"blocking":{"type":"array","items":{"type":"string"}},"notes":{"type":"array","items":{"type":"string"}}}}'

start=$(date +%s)
out=$("$CLAUDE" -p "Read .claude/skills/review-pr/SKILL.md and follow its procedure exactly. Arguments: $args. This is a LOCAL pre-PR review: do not post anything to GitHub; put the summary in your final answer and return the JSON described by the schema, with target set to '$target'." \
  --output-format json --json-schema "$schema" --max-turns 40 \
  --allowedTools "Read,Glob,Grep,Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(git fetch:*),Bash(gh pr view:*),Bash(gh pr diff:*),Bash(gh pr checks:*),Bash(gh issue view:*),Bash(make test),Bash(make lint),Bash(uv run pytest:*),Bash(scripts/tests_on_base.sh:*)" \
  2>/dev/null)
elapsed=$(( $(date +%s) - start ))
verdict_json=$(printf '%s' "$out" | python3 -c 'import json,sys
d=json.load(sys.stdin)
s=d.get("structured_output")
print(json.dumps(s, indent=2) if s else "")' 2>/dev/null)
if [[ -z "$verdict_json" ]]; then
  echo "NO VERDICT after ${elapsed}s. Raw result:" >&2; printf '%s\n' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("result","")[:3000])' >&2; exit 2
fi
mkdir -p runs/reviews
file="runs/reviews/${label}__$(date +%Y%m%d-%H%M%S).json"
printf '%s\n' "$verdict_json" | tee "$file"
verdict=$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')
got=$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("target",""))')
cost=$(printf '%s' "$out" | python3 -c 'import json,sys; print(round(json.load(sys.stdin).get("total_cost_usd",0),2))' 2>/dev/null)
echo "VERDICT: $verdict for $got in ${elapsed}s (~\$$cost) -> $file" >&2
[[ "$got" == "$target" ]] || { echo "WARNING: verdict target '$got' != requested '$target'; discard it" >&2; exit 2; }
[[ "$verdict" == "APPROVE" ]]
