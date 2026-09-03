# 05: Spatial extractor must accept shape-name answers; truncation needs a long response

## Goal
Issue 02 flagged 7 "impossible" spatial items with pass rate 0. Inspection shows their ground truth
is a shape name (`square pyramid`, `tetrahedron`, `triangle`) and the prompt asks for a bold
answer, while the strict spatial extractor only accepts a bold integer. Also, 3/4 of the answers
classified as `truncation` in issue 03 are one-word bare answers (`Tennis`, `2`) rather than cut-off
responses. Fix both so that hardest-item and taxonomy tables measure models, not our parser.

## Acceptance criteria
1. `extract_answer(text, "spatial", "strict")` returns the last bold span whatever its content
   (integer or words); lenient falls back to the last integer. Test: `"the shape is **square**"`
   -> strict `"square"`; `"so 4 pieces."` -> strict `None`, lenient `"4"`.
2. `score_answer("**Square Pyramid**", "square pyramid", "spatial") == 1.0` (normalised match).
3. `classify` returns `truncation` only when the strict extraction is None, the stripped text does
   not end with a terminator, and the text is at least 200 characters; shorter non-terminated
   texts fall through to `format_failure` / `no_answer`. Tests: a 10-char bare answer without bold
   is `format_failure` (zebra, lenient last line) and a 300-char unterminated text is `truncation`.
4. `make lint && make test` pass; existing tests updated only where the old behaviour is asserted.

## Out of scope
Any other task's format; the report.

## Files expected to change
`tasks/livebench.py`, `tasks/livebench_taxonomy.py`, `tests/test_livebench.py`,
`tests/test_livebench_taxonomy.py`

## Depends on
03
