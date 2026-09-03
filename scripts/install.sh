#!/usr/bin/env bash
# make install: local env + git hooks; when gh is authenticated, the idempotent repo setup too.
set -euo pipefail
uv sync
uv run pre-commit install --install-hooks
if ! gh auth status >/dev/null 2>&1; then
  echo "gh not authenticated: run 'gh auth login', then 'make install' again for the repo setup"; exit 0
fi
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh label create task --description "One unit of work, one PR" --color 0E8A16 --force >/dev/null
gh repo edit --enable-auto-merge --delete-branch-on-merge --allow-update-branch \
  --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false >/dev/null
# main: PRs only, squash only, four required checks, no bypass for anyone.
ruleset='{"name":"main","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}},"bypass_actors":[],
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"},
  {"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":true,
   "require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":false,
   "allowed_merge_methods":["squash"]}},
  {"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":false,"do_not_enforce_on_create":false,
   "required_status_checks":[{"context":"lint","integration_id":15368},{"context":"test","integration_id":15368},
    {"context":"pr-links-issue","integration_id":15368},{"context":"review","integration_id":15368}]}}]}'
id=$(gh api "repos/$repo/rulesets" --jq '.[] | select(.name=="main") | .id' 2>/dev/null || true)
if [[ -n "$id" ]]; then
  printf '%s' "$ruleset" | gh api --method PUT "repos/$repo/rulesets/$id" --input - >/dev/null && echo "ruleset updated"
elif printf '%s' "$ruleset" | gh api --method POST "repos/$repo/rulesets" --input - >/dev/null 2>&1; then
  echo "ruleset created"
else
  echo "ruleset NOT created (private repo on a free plan?): make the repo public, or rely on the fix-issue skill's merge gate"
fi
gh secret list 2>/dev/null | grep -q CLAUDE_CODE_OAUTH_TOKEN || echo "missing secret for CI review: 'claude setup-token', then 'gh secret set CLAUDE_CODE_OAUTH_TOKEN'"
echo "ready"
