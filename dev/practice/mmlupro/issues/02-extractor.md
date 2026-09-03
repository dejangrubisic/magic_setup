# 02: Strict/lenient answer extractor, agreement with provided pred, format-failure rate, per-category accuracy

## Goal
Re-score model CoT text with our own extractor so "wrong format" is separated from "wrong answer".
Report per model: strict accuracy, lenient accuracy, agreement with the provided `pred`, and the
format-failure rate (strict returns None). Also per-category accuracy (using `pred`) with Wilson CIs.

## Acceptance criteria
- [ ] `tasks/mmlupro_extract.py` exposes `extract_strict(text) -> str|None` matching
      `answer is (X)` / `answer is X` / `Answer: (X)` (case-insensitive, X in A-J, last match wins)
      and `extract_lenient(text) -> str|None` returning the last standalone capital letter A-J
      (word-boundary, optionally in parentheses) in the text, falling back to None.
- [ ] `score_extractors(outputs_df)` returns a per-model DataFrame with columns
      `n, acc_pred, acc_strict, acc_lenient, agree_strict_pred, agree_lenient_pred, format_fail`
      where `format_fail` = fraction with strict None, and `acc_*` are accuracies treating None as wrong.
- [ ] `category_accuracy(outputs_df)` returns rows `category, model, n, acc, lo, hi` (Wilson).
- [ ] `uv run pytest tests/test_mmlupro_extract.py` passes with hand-written strings covering: strict
      hit, strict miss + lenient hit, no letters, letter inside a word (must not match), lowercase.
- [ ] `uv run python scripts/mmlupro_extract.py --limit 200` runs on real data, writes a run dir via
      `magic.RunDir`, prints the per-model extractor table and a category x model accuracy table.
- [ ] `make lint && make test` pass.

## Out of scope
Changing the loader (01). Error clustering (03). Plots.

## Files expected to change
tasks/mmlupro_extract.py, scripts/mmlupro_extract.py, tests/test_mmlupro_extract.py

## Depends on
#01
