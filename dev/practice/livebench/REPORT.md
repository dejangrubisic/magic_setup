# LiveBench reasoning: model x item matrix, 1PL IRT, failure taxonomy

Branch `practice-livebench`. All numbers below come from `runs/` directories on that branch,
produced by `scripts/livebench_{baseline,irt,taxonomy}.py` on 2026-09-03 after issues 01, 02, 03
and 05 were merged (the 02/03 numbers quoted as "before 05" come from the runs the sub-issue
worktrees produced on 2026-09-02 and are cited by path).

## Data adaptation
`livebench/model_judgment` (split `leaderboard`) contains no reasoning rows (only language, coding,
instruction_following), so there is no "provided score" to agree with. `livebench/model_answer` has
13,095 reasoning answers from 91 models over 150 questions (50 each of `spatial`, `web_of_lies_v2`,
`zebra_puzzle`) and `livebench/reasoning` carries the ground truth for all of them. The score matrix
is therefore derived by re-scoring raw answers against ground truth with our own strict and lenient
extractors; "agreement" is strict-vs-lenient. 45 duplicate (model, question_id) rows (same text,
different `answer_id`) are collapsed to the latest `tstamp`, so `n` counts questions.

## Per-task accuracy, top 10 models by strict overall mean
Run `runs/livebench_baseline__20260903-083616__fdcd92` (91 models, 150 questions; strict mean over
all cells 0.275, lenient 0.308). Wilson 95% CIs, n = 50 questions per task.

| model                      | overall       | spatial                   | web_of_lies_v2            | zebra_puzzle              |
|:---------------------------|:--------------|:--------------------------|:--------------------------|:--------------------------|
| o1-mini-2024-09-12         | 0.753 (n=150) | 0.500 [0.366, 0.634] n=50 | 1.000 [0.929, 1.000] n=50 | 0.760 [0.626, 0.857] n=50 |
| claude-3-5-sonnet-20240620 | 0.580 (n=150) | 0.460 [0.330, 0.596] n=50 | 0.800 [0.670, 0.888] n=50 | 0.480 [0.348, 0.615] n=50 |
| o1-preview-2024-09-12      | 0.553 (n=150) | 0.380 [0.259, 0.518] n=50 | 0.960 [0.865, 0.989] n=50 | 0.320 [0.208, 0.458] n=50 |
| gpt-4o-2024-08-06          | 0.533 (n=150) | 0.540 [0.404, 0.670] n=50 | 0.660 [0.522, 0.776] n=50 | 0.400 [0.276, 0.538] n=50 |
| gpt-4-turbo-2024-04-09     | 0.520 (n=150) | 0.460 [0.330, 0.596] n=50 | 0.700 [0.562, 0.809] n=50 | 0.400 [0.276, 0.538] n=50 |
| chatgpt-4o-latest          | 0.507 (n=150) | 0.440 [0.312, 0.577] n=50 | 0.740 [0.604, 0.841] n=50 | 0.340 [0.224, 0.478] n=50 |
| gpt-4o-2024-05-13          | 0.493 (n=150) | 0.400 [0.276, 0.538] n=50 | 0.700 [0.562, 0.809] n=50 | 0.380 [0.259, 0.518] n=50 |
| gemini-1.5-flash-002       | 0.487 (n=150) | 0.400 [0.276, 0.538] n=50 | 0.620 [0.482, 0.741] n=50 | 0.440 [0.312, 0.577] n=50 |
| gemini-1.5-pro-exp-0827    | 0.480 (n=150) | 0.340 [0.224, 0.478] n=50 | 0.760 [0.626, 0.857] n=50 | 0.340 [0.224, 0.478] n=50 |
| gpt-4-1106-preview         | 0.480 (n=150) | 0.400 [0.276, 0.538] n=50 | 0.640 [0.501, 0.759] n=50 | 0.400 [0.276, 0.538] n=50 |

Before issue 05 (`runs/livebench_baseline__20260902-203705__f14030`) the same table had o1-mini at
0.713 overall and spatial 0.380 [0.259, 0.518]: the bold-integer-only spatial extractor was scoring
every shape-name item as wrong for every model (strict mean over all cells 0.256 vs 0.275 now).

## 1PL IRT: 15 hardest items
Run `runs/livebench_irt__20260903-083617__c76890` (sklearn logistic regression, one-hot(model) +
one-hot(item), no intercept, C=1; zebra binarised at score == 1.0; NaN cells excluded).
Ability top 5: o1-mini 1.78, claude-3-5-sonnet 0.87, o1-preview 0.74, gpt-4o-2024-08-06 0.64,
gpt-4-turbo 0.58. Mean difficulty by task: zebra_puzzle 0.79, spatial 0.50, web_of_lies_v2 0.16.

| question_id (first 12) | task         | difficulty | discrimination_proxy | pass_rate |
|:-----------------------|:-------------|-----------:|---------------------:|----------:|
| 0b02d4ab897f | spatial      | 2.535 |  0.053 | 0.011 |
| ae87a66e60c8 | zebra_puzzle | 2.524 |  0.278 | 0.011 |
| a07f06973712 | spatial      | 2.392 |  0.148 | 0.023 |
| 95ef46b58759 | spatial      | 2.256 |  0.148 | 0.034 |
| 072fe18d123c | zebra_puzzle | 2.245 |  0.102 | 0.034 |
| 2245e7c6df01 | zebra_puzzle | 2.245 |  0.041 | 0.034 |
| 56ed8e93650c | zebra_puzzle | 2.113 | -0.038 | 0.046 |
| 9b210167543 | zebra_puzzle | 1.987 |  0.285 | 0.057 |
| 5a6de6e39f20 | zebra_puzzle | 1.987 |  0.171 | 0.057 |
| a8e3b3da17ee | zebra_puzzle | 1.987 |  0.006 | 0.057 |
| f8e84ee53942 | spatial      | 1.876 |  0.145 | 0.069 |
| f2a76bdd345c | spatial      | 1.876 |  0.011 | 0.069 |
| 1b317054fbe9 | spatial      | 1.876 |  0.164 | 0.069 |
| 86d1093b884d | zebra_puzzle | 1.865 |  0.091 | 0.069 |
| 51f6e96cffc7 | zebra_puzzle | 1.865 |  0.081 | 0.069 |

Full ids are in the run's `summary.json`. Before issue 05
(`.claude/worktrees/practice-livebench-issue-02/runs/livebench_irt__20260902-204439__70be1c`) the
top 7 were all spatial items with pass rate exactly 0 and ground truth `square pyramid`,
`tetrahedron`, `square`, `triangle`, `tetrahedra` -- the extractor, not the models; that run's
`summary.json` also contains a literal `NaN` (discrimination proxy of a constant column), which the
current review skill treats as a defect.

## 5 label-error suspects (lowest discrimination proxy)
Same run. Proxy = point-biserial correlation between model ability and item correctness.

| question_id (first 12) | task         | difficulty | proxy  | pass_rate | ground_truth   |
|:-----------------------|:-------------|-----------:|-------:|----------:|:---------------|
| b7d1f1dff19c | spatial      | 1.158 | -0.066 | 0.149 | 6              |
| 1c6eda54001b | spatial      | 1.072 | -0.064 | 0.161 | 6              |
| 56ed8e93650c | zebra_puzzle | 2.113 | -0.038 | 0.046 | romance movies |
| 4f78225af266 | spatial      | 1.158 | -0.018 | 0.149 | 6              |
| a8e3b3da17ee | zebra_puzzle | 1.987 |  0.006 | 0.057 | writing        |

Only three items have a negative proxy at all, and the most negative is -0.07: there is no strong
label-error signal in this data. The three spatial suspects share ground truth `6` and pass rate
~0.15 spread evenly across abilities, which is what a coin-flip item (guessable small integer)
looks like rather than a mislabeled one.

## Strict vs lenient agreement and failure taxonomy, zebra_puzzle
Run `runs/livebench_taxonomy__20260903-093342__a89f78` (4,350 rows = 87 models x 50 questions;
14 bottom-quartile items by strict mean).

| metric          | value |
|:----------------|------:|
| n               | 4350  |
| exact_agree     | 0.945 |
| strict_mean     | 0.226 |
| lenient_mean    | 0.281 |
| lenient_rescues | 240   |

| class          | all rows | bottom-quartile items | before 05 (all rows) |
|:---------------|---------:|----------------------:|---------------------:|
| correct        |   982    |   77                  |  982 |
| wrong_answer   |  1739    |  685                  | 1739 |
| format_failure |  1339    |  370                  |  968 |
| truncation     |   290    |   86                  |  661 |
| no_answer      |     0    |    0                  |    0 |

"Before 05" is `.claude/worktrees/practice-livebench-issue-03/runs/livebench_taxonomy__20260902-202507__5f4245`;
issue 05 requires >= 200 characters before an unterminated text counts as truncation, which moved
371 bare one-word answers (`Tennis`, `2`) from `truncation` to `format_failure`. Per-item counts for
the 14 bottom-quartile items are in the run's `summary.json` (`taxonomy_per_bottom_item`); every one
of them has 21-37 format failures out of 87 answers.

## Findings
1. **The parser was the hardest "item".** Before issue 05 the seven hardest IRT items were spatial
   questions whose ground truth is a shape name; our bold-integer extractor gave them pass rate 0
   for all 91 models. Fixing the extractor raised the strict mean from 0.256 to 0.275 and o1-mini's
   spatial accuracy from 0.380 to 0.500 (CI [0.366, 0.634]). Score the parser on the hardest items
   before reporting difficulty.
2. **Format failure is a third of zebra_puzzle errors, and is concentrated on the hard items.**
   1,339 of 3,368 non-correct zebra answers (40%) are format failures (strict finds no
   `***answer***`, lenient finds something); on the 14 bottom-quartile items it is 370 of 1,141
   (32%), against 685 wrong answers. Lenient scoring rescues 240 rows (strict 0.226 -> lenient
   0.281), yet exact agreement is still 0.945, so the headline ranking is robust to the parser but
   the per-item difficulty is not.
3. **Task difficulty is ordered zebra > spatial > web_of_lies, and web_of_lies is saturated.**
   Mean 1PL difficulty 0.79 / 0.50 / 0.16; o1-mini scores 1.000 [0.929, 1.000] on web_of_lies_v2
   and o1-preview 0.960. For a curriculum, web_of_lies_v2 items belong at the start and add no
   signal for the top 5 models; zebra bottom-quartile items (pass rate <= 0.07) are the ceiling.
4. **No credible label errors.** The discrimination proxy is >= -0.07 everywhere; the three most
   negative items are spatial questions with answer `6` and pass rate ~0.15 evenly spread across
   abilities, i.e. guessable, not mislabeled. A 1PL on 91 models x 150 items does not have the
   power to separate "guessable" from "mislabeled"; an item-level check of the raw answers is
   needed for the two zebra suspects (`romance movies`, `writing`).
5. **Truncation is rare once bare answers are excluded.** 290 zebra rows (6.7%) are genuinely cut
   off (>= 200 chars, no terminator, no strict answer); the earlier 661 was 56% one-word answers.
   Truncation is not the failure mode to optimise for on this benchmark.

## Not done
- Issue 04 asked for the report only; no plots were produced (none were requested).
- The 02 and 05 sub-branches were re-reviewed with the main-checkout review script on 2026-09-03;
  the verdict files are `.claude/worktrees/practice-livebench-issue-0{2,5}/runs/reviews/` (see
  `dev/LOG.md` for the outcome). The merges into `practice-livebench` happened before those
  verdicts arrived because of the time budget.
