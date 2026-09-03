#!/usr/bin/env bash
# One-time GitHub configuration. Idempotent. Needs: gh auth login (repo admin).
set -euo pipefail
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
echo "Configuring $repo"

# Labels
for spec in "epic:Parent issue grouping sub-issues:5319E7" "task:One unit of work, one PR:0E8A16" \
            "blocked:Waiting on a dependency or a human:D93F0B" "needs-human:Agent stopped; a person must decide:FBCA04"; do
  IFS=: read -r name desc color <<<"$spec"
  gh label create "$name" --description "$desc" --color "$color" --force >/dev/null
done

# Merge policy: squash only, auto-merge, delete branches, keep PRs updatable.
gh repo edit --enable-auto-merge --delete-branch-on-merge --allow-update-branch \
  --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false >/dev/null

# Branch ruleset on main: PR required, required checks = CI jobs + agent review, squash only.
ruleset=$(cat <<'JSON'
{
  "name": "main", "target": "branch", "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [ { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" } ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false, "require_last_push_approval": false,
        "required_review_thread_resolution": true, "allowed_merge_methods": ["squash"] } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false, "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "lint", "integration_id": 15368 },
          { "context": "test", "integration_id": 15368 },
          { "context": "pr-links-issue", "integration_id": 15368 },
          { "context": "review", "integration_id": 15368 } ] } }
  ]
}
JSON
)
existing=$(gh api "repos/$repo/rulesets" --jq '.[] | select(.name=="main") | .id' 2>/dev/null || true)
if [[ -n "$existing" ]]; then
  printf '%s' "$ruleset" | gh api --method PUT "repos/$repo/rulesets/$existing" --input - >/dev/null && echo "ruleset updated"
else
  printf '%s' "$ruleset" | gh api --method POST "repos/$repo/rulesets" --input - >/dev/null && echo "ruleset created"
fi

# Reviewer auth secret
if gh secret list | grep -qE 'CLAUDE_CODE_OAUTH_TOKEN|ANTHROPIC_API_KEY'; then
  echo "reviewer secret present"
else
  cat <<MSG

MISSING reviewer secret. Pick one:
  subscription:  claude setup-token   ->  gh secret set CLAUDE_CODE_OAUTH_TOKEN
  API billing:   gh secret set ANTHROPIC_API_KEY
Then install the Claude GitHub App on this repo (run /install-github-app inside claude, or
https://github.com/apps/claude). Until then the 'review' check fails closed on every PR.
MSG
fi
echo "done"
