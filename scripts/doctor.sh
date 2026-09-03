#!/usr/bin/env bash
# Day-one readiness check. Prints one line per prerequisite; exits 1 if anything blocking is missing.
ok=0; warn=0
pass() { echo "  ok    $1"; }
fail() { echo "  MISSING $1"; ok=1; }
soft() { echo "  warn  $1"; warn=1; }

command -v uv >/dev/null && pass "uv $(uv --version | cut -d' ' -f2)" || fail "uv (https://docs.astral.sh/uv/)"
[[ -d .venv ]] && pass ".venv synced" || soft ".venv missing: run make install"
[[ -f .git/hooks/pre-commit || -f "$(git rev-parse --git-common-dir 2>/dev/null)/hooks/pre-commit" ]] && pass "git hooks installed" || soft "git hooks: run make install"

CLAUDE=${CLAUDE:-$(command -v claude || ls -t "$HOME"/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)}
[[ -x "$CLAUDE" ]] && pass "claude CLI $("$CLAUDE" --version 2>/dev/null | cut -d' ' -f1) ($CLAUDE)" || fail "claude CLI (needed for make review and agents)"

command -v gh >/dev/null && pass "gh $(gh --version | head -1 | cut -d' ' -f3)" || fail "gh CLI (brew install gh)"
if command -v gh >/dev/null; then
  if gh auth status >/dev/null 2>&1; then
    pass "gh authenticated as $(gh api user --jq .login 2>/dev/null)"
    repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null)
    if [[ -n "$repo" ]]; then
      pass "repo $repo"
      gh secret list 2>/dev/null | grep -qE 'CLAUDE_CODE_OAUTH_TOKEN|ANTHROPIC_API_KEY' && pass "CI reviewer secret set" || fail "CI reviewer secret: gh secret set CLAUDE_CODE_OAUTH_TOKEN (from: claude setup-token) or ANTHROPIC_API_KEY"
      gh api "repos/$repo/rulesets" --jq '.[].name' 2>/dev/null | grep -q '^main$' && pass "branch ruleset on main" || fail "branch ruleset: run make gh-setup"
      gh api "repos/$repo/installation" >/dev/null 2>&1 && pass "Claude GitHub App installed" || soft "Claude GitHub App: install at https://github.com/apps/claude (cannot verify without admin token)"
    else
      fail "no GitHub repo for this checkout (gh repo view)"
    fi
  else
    fail "gh not authenticated: gh auth login"
  fi
fi

[[ -n "${ANTHROPIC_API_KEY:-}" || -f .env ]] && pass "ANTHROPIC_API_KEY or .env present (for magic.llm)" || soft "no ANTHROPIC_API_KEY / .env: magic.llm calls will fail on cache miss"
[[ -d "$HOME/.cache/huggingface" ]] && pass "HF cache at ~/.cache/huggingface" || soft "no HF cache yet (first dataset download creates it)"
df -h . | awk 'NR==2 {print "  info  disk free " $4}'

echo
if [[ $ok -ne 0 ]]; then echo "BLOCKING items above must be fixed before running the issue workflow."; exit 1; fi
[[ $warn -ne 0 ]] && echo "Warnings are non-blocking."
echo "ready"
