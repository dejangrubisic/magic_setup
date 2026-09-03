# Practice problems

Five dry runs, each in its own worktree, to measure how fast the setup lets us go from
"here is a problem" to "baseline number + failure-mode analysis", and to find what is missing.
Every run writes its own `lessons/0N-<name>.md`; the setup changes they triggered are listed at
the bottom of this file.

Selection rule: data downloads without credentials, is under 500 MB, and the problem sits in
evaluation / failure modes / difficulty / curriculum / RL.

| # | Problem | Data (no auth) | Size | Exercises |
|---|---------|----------------|------|-----------|
| 1 | **Eedi: mining misconceptions in mathematics** (Kaggle 2024). Rank 2,587 misconceptions for a wrong answer, MAP@25. | GitHub mirror of the competition zip (`jimzijun/Eedi---Mining-Misconceptions-in-Mathematics`) | 0.3 MB | retrieval eval harness, error clustering by subject/construct |
| 2 | **Easy2Hard-Bench** (E2H-GSM8K, E2H-AMC). Items with IRT/Glicko difficulty ratings. | HF `furonghuang-lab/Easy2Hard-Bench` | < 5 MB per config | difficulty modelling, curriculum ordering, Spearman vs. ground truth |
| 3 | **LiveBench model judgments** (195 models x 18 tasks with ground truth). | HF `livebench/model_judgment`, `livebench/model_answer`, `livebench/reasoning` | ~60 MB | model x item matrix, IRT, failure taxonomy (format vs wrong vs truncation) |
| 4 | **MMLU-Pro per-question outputs of 51 models**. | HF `TIGER-Lab/MMLU-Pro` + GitHub `TIGER-AI-Lab/MMLU-Pro/eval_results/*.zip` | 4 MB + 3-7 MB per model | re-scoring with own parser, error clustering, label-error suspects |
| 5 | **Gridworld curriculum RL** (own environment, numpy). Random vs easy-to-hard vs regret-prioritised level replay. | none (procedural) | 0 | RL loop, curriculum construction, seeds, learning curves with CIs |

Alternates kept in reserve: LMSYS arena 55k human preferences (HF `lmarena-ai/arena-human-preference-55k`, 184 MB,
judge failure modes), RewardBench + per-model scores (`allenai/reward-bench-results`, download single files),
HelpSteer2 (`nvidia/HelpSteer2`, annotator disagreement), PRM800K phase 1 (first-error-step analysis),
EmbedLLM `test.csv` (112 models x 36k items correctness matrix, 269 MB), jaxued (PLR/ACCEL on mazes, needs JAX),
ARC-AGI-1 + H-ARC human solve rates.

Rejected: anything needing Kaggle credentials only (MAP student misunderstandings, ARC Prize, AIMO),
Docker execution (Konwinski/SWE-bench), or > 500 MB.

## What each run must report (`lessons/0N-<name>.md`)
- Timeline: minutes from start to (a) data loaded, (b) first baseline number, (c) first analysis table, (d) review passed.
- What in the scaffold helped, what got in the way, what was missing (utility, doc line, Makefile target, skill step).
- Reviewer behaviour: did `make review` push back correctly? False positives/negatives.
- Concrete setup changes proposed (one line each, ranked).

## Setup changes triggered by the runs
(filled in after the runs)
