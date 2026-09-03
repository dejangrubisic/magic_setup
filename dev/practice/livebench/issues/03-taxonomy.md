# 03: Strict vs lenient parser agreement and failure taxonomy for zebra_puzzle

## Goal
For the `zebra_puzzle` task re-derive scores with the strict and lenient extractors, report their
agreement, and classify every answer on bottom-quartile items (by strict mean score) into a failure
taxonomy with counts.

## Acceptance criteria
1. `tasks/livebench_taxonomy.py::classify(text, ground_truth, task) -> str` returns one of
   `correct | wrong_answer | format_failure | truncation | no_answer`:
   - `correct`: strict score == 1
   - `format_failure`: strict extraction is None but lenient extraction is not None
   - `truncation`: no extraction in either mode and the text is empty or does not end with a
     sentence terminator (`.`, `!`, `?`, `*`, `>`, `\``) after stripping whitespace
   - `no_answer`: no extraction in either mode, text ends with a terminator
   - `wrong_answer`: otherwise (extracted but wrong / partial)
   Tests cover all five classes.
2. `agreement(df) -> dict` with keys `n`, `exact_agree` (fraction of rows with equal strict and
   lenient score), `strict_mean`, `lenient_mean`, `lenient_rescues` (rows where strict==0 and
   lenient>0). Tested on a small frame.
3. `scripts/livebench_taxonomy.py --limit N --task zebra_puzzle` writes
   `runs/livebench_taxonomy__*/summary.json` with the agreement dict, the bottom-quartile item ids,
   and taxonomy counts (overall and per bottom-quartile item), and prints markdown tables.
4. `make lint && make test` pass; tests never read `data/raw`.

## Out of scope
IRT, report text, other tasks than the one passed via `--task`.

## Files expected to change
`tasks/livebench_taxonomy.py`, `scripts/livebench_taxonomy.py`, `tests/test_livebench_taxonomy.py`

## Depends on
01
