# One vocabulary for humans, agents, pre-commit and CI. Every recipe goes through `uv run`,
# so it works identically in any worktree with no activation step.
.DEFAULT_GOAL := help
SHELL := /bin/bash

# Claude CLI: on PATH, or the binary bundled with the IDE extension.
CLAUDE ?= $(shell command -v claude 2>/dev/null || ls -t $(HOME)/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)

.PHONY: doctor
doctor: ## Day-one readiness check (uv, claude, gh auth, secrets, ruleset)
	@scripts/doctor.sh

.PHONY: install
install: ## Sync the env and install git hooks (run once per clone; worktrees share hooks)
	uv sync
	uv run pre-commit install --install-hooks

.PHONY: format
format: ## Auto-format and auto-fix lint
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ## Check format, lint, and that uv.lock matches pyproject (what CI runs)
	uv run ruff format --check
	uv run ruff check
	uv lock --check

.PHONY: test
test: ## Fast tests, parallel, no coverage (what CI runs)
	uv run pytest -n auto --durations=5

.PHONY: test-cov
test-cov: ## Tests with a coverage report on src/ (advisory)
	uv run pytest -n auto --cov --cov-report=term-missing:skip-covered

.PHONY: check
check: lint test ## Everything CI checks, locally

.PHONY: review
review: ## Local CI-agent review: make review N=<pr> | make review BRANCH=<name> ISSUE=<n|file> [BASE=<ref>]
	CLAUDE="$(CLAUDE)" BASE="$(BASE)" scripts/review_pr.sh $(if $(N),$(N),$(BRANCH)) $(ISSUE)

.PHONY: wt
wt: ## Create a worktree for an issue: make wt I=<issue-number|name> [BASE=<ref>]
	scripts/wt.sh new $(I) $(BASE)

.PHONY: wt-rm
wt-rm: ## Remove a merged issue worktree: make wt-rm I=<issue-number>
	scripts/wt.sh rm $(I)

.PHONY: gh-setup
gh-setup: ## One-time GitHub config: labels, merge settings, branch ruleset (needs `gh auth login`)
	scripts/gh_setup.sh

.PHONY: clean
clean: ## Remove caches (not data/ or runs/)
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
