#!/usr/bin/env bash
# PostToolUse: auto-format the edited .py file and feed remaining lint errors back to Claude (exit 2).
f=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
case "$f" in *.py) ;; *) exit 0 ;; esac
[[ -f "$f" ]] || exit 0
cd "$(dirname "$f")" || exit 0
uv run -q ruff format "$f" >/dev/null 2>&1
uv run -q ruff check --fix "$f" >/dev/null 2>&1
out=$(uv run -q ruff check "$f" 2>&1) && exit 0
echo "ruff: $out" >&2
exit 2
