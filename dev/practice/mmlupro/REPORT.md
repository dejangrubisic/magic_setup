# MMLU-Pro per-question outputs: error clustering and label-error suspects

Practice run `mmlupro` (2026-09-02, resumed 2026-09-03 after a rate-limit cut-off; tables re-generated from the merged code). Seven models from `TIGER-AI-Lab/MMLU-Pro/eval_results`
(5-shot CoT) joined to the HF `TIGER-Lab/MMLU-Pro` test split (12,032 questions). All numbers are
from `scripts/mmlupro_{baseline,extract,errors}.py`; run ids are given per table. Uncertainty is a
Wilson 95% interval.

Data caveats found on the way (all handled in `tasks/mmlupro.py`):
- `Meta-Llama-3-70B-Instruct`'s file uses positional `question_id`s (0% agree with HF ids) and has
  duplicate rows; it is re-keyed by question text + first option (10,860 of 12,187 rows match; the
  rest are dropped). Before this fix the item x model matrix was wrong for that model and the
  all-fail set was under-counted by 53% (582 vs 1,242).
- The other six files agree with HF ids on 97.7-97.8% of rows: HF has since edited ~230 question
  texts and 506 questions carry a different `answer` letter than the files. Correctness below uses
  the label stored in each file (the label the eval was scored against).
- The CoT text lives under `model_outputs` (API models) or `generated_text` (open models).

## 1. Per-model accuracy (provided `pred`), run `mmlupro_baseline__20260903-093400__ddcce5`

Rows whose file has no `pred` (about 275 per open model, none for the API models) count as wrong,
as in the official scorer; an earlier draft of this table excluded them (n = 11,757) and was
0.1-0.3 points higher.

| model | n | acc | lo | hi |
|:--|--:|--:|--:|--:|
| claude-3.5-sonnet | 12030 | 0.761 | 0.753 | 0.769 |
| gpt-4o-2024-08-06 | 12032 | 0.747 | 0.739 | 0.754 |
| deepseek-chat-v2.5 | 12032 | 0.658 | 0.650 | 0.667 |
| Llama-3-70B-Instruct (re-keyed) | 10860 | 0.577 | 0.567 | 0.586 |
| Llama-3-8B-Instruct | 12032 | 0.401 | 0.392 | 0.410 |
| gemma-7b | 12032 | 0.324 | 0.315 | 0.332 |
| Qwen1.5-7B-Chat | 12032 | 0.264 | 0.257 | 0.272 |

These match the public leaderboard (gpt-4o 74.7, sonnet 76.1), so the join is right.

## 2. Own extractor vs provided `pred`, run `mmlupro_extract__20260903-093403__e93aa8`

strict = first `answer is (X)` / `Answer: (X)` (the official scorer's rule); lenient = last
standalone capital A-J; `format_fail` = strict finds nothing; `runaway` = first and last strict
matches differ (the model kept generating after answering).

| model                            |         n |   acc_pred |   acc_strict |   acc_lenient |   agree_strict_pred |   agree_lenient_pred |   format_fail |   runaway |
|:---------------------------------|----------:|-----------:|-------------:|--------------:|--------------------:|---------------------:|--------------:|----------:|
| Llama-3-70B-Instruct | 10860.000 |      0.577 |        0.577 |         0.130 |               0.950 |                0.159 |         0.050 |     0.472 |
| Llama-3-8B-Instruct  | 12032.000 |      0.401 |        0.401 |         0.100 |               0.926 |                0.113 |         0.074 |     0.472 |
| Qwen1.5-7B-Chat           | 12032.000 |      0.264 |        0.271 |         0.300 |               0.766 |                0.729 |         0.209 |     0.007 |
| claude-3.5-sonnet         | 12030.000 |      0.761 |        0.761 |         0.755 |               0.995 |                0.989 |         0.004 |     0.000 |
| deepseek-chat-v2_5        | 12032.000 |      0.658 |        0.657 |         0.658 |               0.987 |                0.993 |         0.013 |     0.000 |
| gemma-7b                  | 12032.000 |      0.324 |        0.324 |         0.328 |               0.868 |                0.866 |         0.131 |     0.001 |
| gpt-4o-2024-08-06         | 12032.000 |      0.747 |        0.746 |         0.747 |               0.987 |                0.991 |         0.012 |     0.001 |

Per-category accuracy (pred) x model:

| category         |    n | Llama-3-70B-Instruct   | Llama-3-8B-Instruct   | Qwen1.5-7B-Chat   | claude-3.5-sonnet   | deepseek-chat-v2_5   | gemma-7b      | gpt-4o-2024-08-06   |
|:-----------------|-----:|:-----------------------------------|:----------------------------------|:-------------------------|:---------------------------|:----------------------------|:---------------------|:---------------------------|
| biology          |  717 | 0.791 [0.760, 0.820]               | 0.662 [0.627, 0.696]              | 0.435 [0.399, 0.472]     | 0.886 [0.860, 0.907]       | 0.827 [0.798, 0.853]        | 0.498 [0.461, 0.534] | 0.893 [0.868, 0.913]       |
| business         |  789 | 0.598 [0.563, 0.632]               | 0.397 [0.363, 0.431]              | 0.259 [0.229, 0.290]     | 0.802 [0.773, 0.829]       | 0.736 [0.705, 0.766]        | 0.305 [0.274, 0.338] | 0.801 [0.772, 0.827]       |
| chemistry        | 1132 | 0.501 [0.467, 0.535]               | 0.255 [0.231, 0.281]              | 0.133 [0.115, 0.154]     | 0.773 [0.748, 0.796]       | 0.698 [0.670, 0.724]        | 0.211 [0.188, 0.236] | 0.727 [0.700, 0.752]       |
| computer science |  410 | 0.614 [0.566, 0.661]               | 0.422 [0.375, 0.470]              | 0.290 [0.248, 0.336]     | 0.798 [0.756, 0.834]       | 0.710 [0.664, 0.752]        | 0.356 [0.311, 0.404] | 0.783 [0.740, 0.820]       |
| economics        |  844 | 0.692 [0.660, 0.723]               | 0.532 [0.498, 0.565]              | 0.405 [0.373, 0.439]     | 0.825 [0.798, 0.849]       | 0.768 [0.738, 0.795]        | 0.431 [0.398, 0.465] | 0.816 [0.789, 0.841]       |
| engineering      |  969 | 0.433 [0.395, 0.473]               | 0.307 [0.278, 0.336]              | 0.162 [0.140, 0.187]     | 0.615 [0.584, 0.645]       | 0.517 [0.486, 0.548]        | 0.199 [0.175, 0.225] | 0.553 [0.522, 0.584]       |
| health           |  818 | 0.657 [0.621, 0.691]               | 0.489 [0.455, 0.523]              | 0.249 [0.221, 0.280]     | 0.753 [0.722, 0.781]       | 0.625 [0.591, 0.657]        | 0.359 [0.327, 0.393] | 0.760 [0.730, 0.788]       |
| history          |  381 | 0.592 [0.541, 0.641]               | 0.423 [0.374, 0.473]              | 0.286 [0.243, 0.333]     | 0.759 [0.713, 0.799]       | 0.556 [0.506, 0.606]        | 0.378 [0.331, 0.428] | 0.732 [0.686, 0.774]       |
| law              | 1101 | 0.411 [0.380, 0.442]               | 0.263 [0.238, 0.290]              | 0.185 [0.163, 0.209]     | 0.639 [0.610, 0.666]       | 0.371 [0.343, 0.400]        | 0.185 [0.163, 0.209] | 0.589 [0.560, 0.618]       |
| math             | 1351 | 0.527 [0.500, 0.554]               | 0.333 [0.308, 0.359]              | 0.277 [0.254, 0.301]     | 0.768 [0.745, 0.790]       | 0.754 [0.730, 0.776]        | 0.273 [0.250, 0.298] | 0.794 [0.772, 0.815]       |
| other            |  924 | 0.610 [0.578, 0.641]               | 0.459 [0.427, 0.491]              | 0.312 [0.283, 0.342]     | 0.785 [0.757, 0.810]       | 0.639 [0.607, 0.669]        | 0.405 [0.374, 0.437] | 0.795 [0.768, 0.820]       |
| philosophy       |  499 | 0.551 [0.507, 0.594]               | 0.401 [0.359, 0.444]              | 0.261 [0.224, 0.301]     | 0.747 [0.708, 0.784]       | 0.563 [0.519, 0.606]        | 0.381 [0.339, 0.424] | 0.703 [0.662, 0.742]       |
| physics          | 1299 | 0.501 [0.472, 0.529]               | 0.333 [0.307, 0.359]              | 0.179 [0.159, 0.201]     | 0.767 [0.743, 0.789]       | 0.705 [0.680, 0.729]        | 0.277 [0.253, 0.302] | 0.751 [0.726, 0.773]       |
| psychology       |  798 | 0.725 [0.693, 0.756]               | 0.594 [0.560, 0.628]              | 0.444 [0.409, 0.478]     | 0.822 [0.794, 0.847]       | 0.727 [0.695, 0.757]        | 0.524 [0.489, 0.558] | 0.827 [0.799, 0.852]       |

## 3. Error clustering, run `mmlupro_errors__20260903-093410__0fcfd9`

All-fail items (every model wrong): 1,242 / 12,032 (10.3%).

| category         |   all_fail |        n |   share |
|:-----------------|-----------:|---------:|--------:|
| biology          |     26.000 |  717.000 |   0.036 |
| business         |     61.000 |  789.000 |   0.077 |
| chemistry        |    105.000 | 1132.000 |   0.093 |
| computer science |     30.000 |  410.000 |   0.073 |
| economics        |     57.000 |  844.000 |   0.068 |
| engineering      |    169.000 |  969.000 |   0.174 |
| health           |    106.000 |  818.000 |   0.130 |
| history          |     58.000 |  381.000 |   0.152 |
| law              |    205.000 | 1101.000 |   0.186 |
| math             |     94.000 | 1351.000 |   0.070 |
| other            |     88.000 |  924.000 |   0.095 |
| philosophy       |     61.000 |  499.000 |   0.122 |
| physics          |    112.000 | 1299.000 |   0.086 |
| psychology       |     70.000 |  798.000 |   0.088 |

Distribution of wrong predictions per category (share of wrong rows; `share_pred_none` = no
answer extracted; `share_adjacent` = chosen letter is next to the correct one):

| category         |   n_wrong |   share_pred_none |   share_adjacent |     A |     B |     C |     D |     E |     F |     G |     H |     I |     J |
|:-----------------|----------:|------------------:|-----------------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| biology          |  1437.000 |             0.197 |            0.155 | 0.118 | 0.100 | 0.095 | 0.093 | 0.087 | 0.070 | 0.063 | 0.060 | 0.060 | 0.059 |
| business         |  2443.000 |             0.163 |            0.165 | 0.141 | 0.130 | 0.103 | 0.092 | 0.087 | 0.050 | 0.054 | 0.060 | 0.055 | 0.064 |
| chemistry        |  4043.000 |             0.347 |            0.132 | 0.109 | 0.087 | 0.085 | 0.071 | 0.055 | 0.060 | 0.047 | 0.045 | 0.051 | 0.043 |
| computer science |  1238.000 |             0.145 |            0.169 | 0.123 | 0.137 | 0.092 | 0.095 | 0.096 | 0.080 | 0.071 | 0.051 | 0.065 | 0.045 |
| economics        |  2131.000 |             0.071 |            0.219 | 0.146 | 0.122 | 0.105 | 0.112 | 0.096 | 0.084 | 0.061 | 0.082 | 0.063 | 0.057 |
| engineering      |  3881.000 |             0.149 |            0.168 | 0.208 | 0.147 | 0.103 | 0.087 | 0.065 | 0.055 | 0.042 | 0.051 | 0.047 | 0.044 |
| health           |  2498.000 |             0.082 |            0.184 | 0.122 | 0.107 | 0.107 | 0.135 | 0.084 | 0.086 | 0.072 | 0.084 | 0.075 | 0.044 |
| history          |  1243.000 |             0.070 |            0.195 | 0.126 | 0.111 | 0.088 | 0.131 | 0.101 | 0.109 | 0.101 | 0.064 | 0.043 | 0.057 |
| law              |  4731.000 |             0.045 |            0.219 | 0.103 | 0.103 | 0.117 | 0.121 | 0.104 | 0.088 | 0.090 | 0.084 | 0.090 | 0.056 |
| math             |  4407.000 |             0.278 |            0.151 | 0.103 | 0.080 | 0.079 | 0.069 | 0.073 | 0.071 | 0.057 | 0.067 | 0.066 | 0.057 |
| other            |  2757.000 |             0.058 |            0.213 | 0.130 | 0.124 | 0.110 | 0.120 | 0.094 | 0.075 | 0.074 | 0.074 | 0.071 | 0.069 |
| philosophy       |  1691.000 |             0.067 |            0.223 | 0.141 | 0.123 | 0.135 | 0.106 | 0.083 | 0.076 | 0.053 | 0.072 | 0.079 | 0.063 |
| physics          |  4466.000 |             0.203 |            0.160 | 0.127 | 0.116 | 0.092 | 0.088 | 0.083 | 0.063 | 0.049 | 0.056 | 0.067 | 0.055 |
| psychology       |  1856.000 |             0.028 |            0.199 | 0.108 | 0.139 | 0.110 | 0.146 | 0.102 | 0.072 | 0.069 | 0.073 | 0.077 | 0.075 |

### Label-error suspects: 20 sampled all-fail items (seed 0)

Heuristic flags over all 1,242 all-fail items: `dup_option` 0, `answer_index_mismatch` 0,
`consensus` (>= 80% of >= 3 models on one wrong letter) 262 (21%). In the sample of 20:
4 consensus-flagged, 0 for the other two heuristics.

| qid | category | label | label text | consensus (share) | consensus text | consensus flag |
|---:|:--|:--|:--|:--|:--|:--|
| 121 | business | F | 61.5 | E (0.43) | 50 |  |
| 324 | business | F | $4,651.25 | I (0.29) | $3,850.50 |  |
| 691 | business | F | Specific, measurable, achievable, rewarded an | D (0.86) | Specific, measurable, achievable, resourced a | yes |
| 1180 | law | A | Murder. | B (0.43) | No crime. |  |
| 1542 | law | B | the man is guilty of manslaughter only. | G (0.43) | the man is guilty of involuntary manslaughter |  |
| 1581 | law | J | No, because the insurance adjuster's statemen | D (0.50) | No, because the insurance adjuster did not ha |  |
| 2516 | psychology | H | 9 to 10 | D (0.57) | 10 to 12 |  |
| 2540 | psychology | G | Mechanistic, organismic, and psychoanalytic | A (0.71) | Biological, psychoanalytic, and social learni |  |
| 4219 | chemistry | D | 3.94 ×10^3 inches | H (0.71) | 0.003937 inches |  |
| 4367 | chemistry | C | 41mg/l | H (0.33) | 8mg/l |  |
| 4658 | chemistry | H | - 7.0K | C (0.57) | 13.5K |  |
| 5220 | other | G | (s)he experiences feelings of hopelessness an | B (0.57) | (s)he feels ashamed and regrets their behavio |  |
| 7133 | economics | C | The monetary multiplier is the ratio of total | H (0.57) | The monetary multiplier is the rate at which  |  |
| 7767 | math | F | 1.0 | H (0.43) | 0.0 |  |
| 9547 | physics | B | refraction. | G (1.00) | interference. | yes |
| 9709 | physics | I | 0.01696 amu | D (0.57) | 3.01603 amu |  |
| 10911 | philosophy | A | privacy. | J (1.00) | life. | yes |
| 11231 | philosophy | B | non-consensual. | I (1.00) | deliberately non-procreative. | yes |
| 11374 | engineering | I | (8 × 10^6)πN-m | A (0.67) | (16 × 10^6)πN-m |  |
| 11714 | engineering | J | Friction coefficient for the bearing is 0.004 | A (0.33) | Friction coefficient for the bearing is 0.003 |  |

Manual read of the 20 (question + options), label looks wrong in **7/20**: 4219 (option typo
`3.94 x 10^3` in for `10^-3`), 7767 (TheoremQA `1.0` = "True" conversion artifact), 9547 (beats
are interference, not refraction), 9709 (He-3 mass is 3.01603 amu), 10911 (Nathanson: right to
*life*), 11231 (Corvino/Aquinas: *non-procreative*), 4367 (8 mg/L is the O2 solubility in air;
borderline). 3 of the 4 consensus-flagged items are in this set (691 "SMART" is genuinely
ambiguous); 4 of the 7 label errors had consensus below 0.8 (0.33-0.71). Of the remaining 13,
about 6 are long numeric computations I could not verify in the time and 7 are ambiguous
converted-from-open-ended items (law hypotheticals, "list and define three approaches").

## Findings

1. **Format failures are a weak-model phenomenon, and the official scorer hides them.** Strict
   extraction fails on 21% of Qwen1.5-7B and 13% of gemma-7b outputs versus <= 1.3% for the API
   models; those rows count as wrong, so the weak models' accuracy is partly a formatting score.
   Lenient extraction recovers only +3 points for Qwen and +0.4 for gemma.
2. **Runaway generation: 47% of Llama-3 (8B and 70B) outputs keep going past the answer** and
   emit further fabricated questions with their own "answer is (X)". First-match extraction (the
   official rule) agrees with `pred` on 93-95% of rows; a last-match rule would drop Llama-3-70B
   from 0.577 to 0.297. Any re-scoring of these dumps must use first-match or cut at the stop token.
3. **All-fail rate is highest in law (18.6%), engineering (17.4%), history (15.2%), health (13.0%)**,
   and lowest in biology (3.6%). Chemistry/math/physics have the highest "no answer" share among
   wrong rows (35%/28%/20%): errors there are often truncated or unfinished computations rather than
   a wrong letter, i.e. a length/compute failure rather than a knowledge failure.
4. **Wrong answers skew towards early letters and near misses.** A is the most chosen wrong
   option in 9/14 categories (21% of engineering errors; D leads in health, history, law,
   psychology), and 15-22% of wrong answers are the letter adjacent to the correct one, i.e. the
   near-miss numeric distractors MMLU-Pro added do their job; position bias is real but small.
5. **Roughly a third of unanimous-wrong items are label errors.** 115 items have all answering
   models on the same wrong letter; in the sample, 3 of 4 such items were mislabelled, and 7/20 of
   random all-fail items were. Extrapolating, ~400 of the 1,242 all-fail items (3% of the
   benchmark) are likely label errors, which caps achievable accuracy around 97% and inflates
   the "hard" tail used for difficulty/curriculum ordering. A consensus threshold of 0.5 (not 0.8)
   plus "answer text appears in the CoT of a wrong model" would be a better first filter than the
   duplicate-option / index-mismatch checks, which fired zero times.
