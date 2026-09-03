# One vocabulary for humans, agents and CI. Everything runs through `uv run`, so it works in any worktree.
.DEFAULT_GOAL := help
ARG := $(word 2,$(MAKECMDGOALS))
%:            # lets `make fix 12` pass 12 as an argument
	@:

.PHONY: install
install: ## Once per clone: env, git hooks, and (with gh logged in) the repo setup
	@scripts/install.sh

.PHONY: format
format: ## Auto-format and auto-fix lint
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ## Format check, lint, lockfile check (what CI runs)
	uv run ruff format --check
	uv run ruff check
	uv lock --check

.PHONY: test
test: ## Fast parallel tests (what CI runs)
	uv run pytest -n auto

.PHONY: check
check: lint test ## Everything CI checks, locally

.PHONY: fix
fix: ## make fix <issue>: branch + worktree + draft PR; prints the worktree path
	@scripts/fix_issue.sh $(ARG)

.PHONY: review
review: ## make review <issue>: CI-agent review of branch issue-<issue> (also what CI runs)
	@scripts/review.sh $(ARG)

.PHONY: help
help: ## Show this help
	@grep -E '^[a-z]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'
