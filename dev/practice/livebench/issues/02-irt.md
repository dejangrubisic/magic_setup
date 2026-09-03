# 02: 1PL IRT on the strict score matrix — difficulty, ability, hardest items, label-error suspects

## Goal
Fit a 1PL (Rasch) model to the binary strict score matrix from issue 01 with sklearn logistic
regression on one-hot(model) + one-hot(item) (no intercept), and derive item difficulty and model
ability. List the 15 hardest items and 5 label-error suspects with a negative discrimination proxy.

## Acceptance criteria
1. `tasks/livebench_irt.py::fit_1pl(matrix: DataFrame, C=1.0) -> (ability: Series, difficulty: Series)`
   where `matrix` is models x items with values in {0,1,NaN}; NaN cells are excluded. Difficulty =
   -item coefficient, ability = model coefficient. Test on a synthetic 6x8 matrix: a model that
   answers everything gets the highest ability; an item nobody answers gets the highest difficulty;
   difficulty ordering matches the item pass-rate ordering.
2. `discrimination_proxy(matrix, ability) -> Series` = point-biserial correlation between ability
   and item correctness across models (NaN skipped). Test: an item whose only passers are the two
   weakest models gets a negative value; an item passed only by the strongest gets a positive value.
3. `scripts/livebench_irt.py --limit N` loads the strict matrix (zebra scores binarised at 1.0),
   fits, writes `runs/livebench_irt__*/summary.json` with `hardest_15` (question_id, task,
   difficulty, pass_rate) and `negative_discrimination_5` (question_id, task, proxy, pass_rate,
   ground_truth) and prints both as markdown tables.
4. `make lint && make test` pass; tests never read `data/raw`.

## Out of scope
2PL/3PL, plots, taxonomy, report text.

## Files expected to change
`tasks/livebench_irt.py`, `scripts/livebench_irt.py`, `tests/test_livebench_irt.py`

## Depends on
01
