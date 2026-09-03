# 03: Error clustering — distractor distribution per category, all-fail items, label-error heuristics

## Goal
Characterise where models fail: per category, the distribution of the chosen (wrong) option index
relative to the answer index; items ALL models get wrong as label-error suspects, with a sample of
20 run through heuristic checks; report how many look like label errors.

## Acceptance criteria
- [ ] `tasks/mmlupro_errors.py` exposes `distractor_distribution(outputs_df)` -> DataFrame indexed by
      category with columns `n_wrong, share_pred_none, share_adjacent` (adjacent = |pred_idx -
      answer_idx| == 1) plus one column per pred letter A-J giving the share of wrong answers.
- [ ] `all_fail_items(outputs_df, questions_df)` returns question rows where every model with a row
      is wrong, with columns `question_id, category, answer, answer_index, options, n_models,
      consensus_pred, consensus_share` (most common wrong pred and its share).
- [ ] `label_error_flags(row)` returns dict of bools: `dup_option` (answer text appears twice in
      options, case/whitespace-insensitive), `consensus` (consensus_share >= 0.8 with >= 3 models),
      `answer_index_mismatch` (options[answer_index] letter != answer); and
      `suspect = any(flags)`.
- [ ] `uv run pytest tests/test_mmlupro_errors.py` passes on hand-built frames and asserts the
      distractor shares, the all-fail set, and each flag on a positive and a negative example.
- [ ] `uv run python scripts/mmlupro_errors.py --limit 500 --sample 20 --seed 0` runs on real data,
      writes a run dir with the 20 sampled suspects and their flags as samples, prints the distractor
      table and the suspects table with flag counts.
- [ ] `make lint && make test` pass.

## Out of scope
Extractor (02). Loader changes (01). Report prose (04).

## Files expected to change
tasks/mmlupro_errors.py, scripts/mmlupro_errors.py, tests/test_mmlupro_errors.py

## Depends on
#01
