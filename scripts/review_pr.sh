#!/usr/bin/env bash
# Local run of the CI reviewer, same procedure as .github/workflows/claude-review.yml.
#   scripts/review_pr.sh 12                 # review PR #12 (needs gh auth)
#   scripts/review_pr.sh issue-12 12        # review local branch issue-12 against issue #12
#   scripts/review_pr.sh issue-12 spec.md   # ... against an issue written in a local markdown file
# Exit 0 on APPROVE, 1 on REQUEST_CHANGES, 2 on no verdict. Full JSON verdict on stdout.
set -uo pipefail
target=${1:-}; issue=${2:-}
[[ -n "$target" ]] || { echo "usage: $0 <pr-number|branch> [issue-number|issue-file]"; exit 2; }
CLAUDE=${CLAUDE:-$(command -v claude || ls -t "$HOME"/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)}
[[ -x "$CLAUDE" ]] || { echo "claude CLI not found; set CLAUDE=/path/to/claude"; exit 2; }

if [[ "$target" =~ ^[0-9]+$ ]]; then
  args="$target"
else
  [[ -n "$issue" ]] || { echo "branch mode needs an issue number or file"; exit 2; }
  args="branch=$target issue=$issue"
fi

schema='{"type":"object","required":["verdict","obligations","blocking"],"properties":{"verdict":{"type":"string","enum":["APPROVE","REQUEST_CHANGES"]},"obligations":{"type":"array","items":{"type":"object","required":["text","status","evidence"],"properties":{"text":{"type":"string"},"status":{"type":"string","enum":["met","unmet","unverifiable"]},"evidence":{"type":"string"}}}},"blocking":{"type":"array","items":{"type":"string"}},"notes":{"type":"array","items":{"type":"string"}}}}'

out=$("$CLAUDE" -p "Read .claude/skills/review-pr/SKILL.md and follow its procedure exactly. Arguments: $args. This is a LOCAL pre-PR review: do not post anything to GitHub; put the summary in your final answer and return the JSON described by the schema." \
  --output-format json --json-schema "$schema" --max-turns 40 \
  --allowedTools "Read,Glob,Grep,Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(git fetch:*),Bash(gh pr view:*),Bash(gh pr diff:*),Bash(gh pr checks:*),Bash(gh issue view:*),Bash(make test),Bash(make lint),Bash(uv run pytest:*)" \
  2>/dev/null)
verdict_json=$(printf '%s' "$out" | python3 -c 'import json,sys
d=json.load(sys.stdin)
s=d.get("structured_output")
print(json.dumps(s, indent=2) if s else "")' 2>/dev/null)
if [[ -z "$verdict_json" ]]; then
  echo "NO VERDICT. Raw result:" >&2; printf '%s\n' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("result","")[:3000])' >&2; exit 2
fi
printf '%s\n' "$verdict_json"
[[ "$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')" == "APPROVE" ]]
