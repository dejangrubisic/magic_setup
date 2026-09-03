# Experiment log

One entry per experiment, newest first, including negative results. Numbers come from
`magic.results` tables, not from memory.

## 2026-09-03: MMLU-Pro error clustering + label-error suspects (positive) — practice epic `dev/practice/mmlupro`, runs `mmlupro_baseline__20260903-093400__ddcce5`, `mmlupro_extract__20260903-093403__e93aa8`, `mmlupro_errors__20260903-093410__0fcfd9`
- what changed: first analysis of 7 models' per-question MMLU-Pro outputs; own strict/lenient extractor; all-fail items with heuristic label-error flags.
- result: acc (Wilson 95%) sonnet-3.5 0.761 [0.753, 0.769], gpt-4o 0.747 [0.739, 0.754], deepseek-v2.5 0.658, llama-3-70b 0.577 (re-keyed, n=10860), llama-3-8b 0.401, gemma-7b 0.324, qwen1.5-7b 0.264 (rows without a `pred` count as wrong). Format-failure 21% (Qwen) / 13% (gemma) vs <= 1.3% (API models); 47% runaway generation on Llama-3. All-fail 1,242/12,032; 7/20 sampled look like label errors.
- keep: loader re-keys Llama-3-70B by question text (its ids are positional); strict extractor = first match (official rule). Drop: dup-option and index-mismatch heuristics (fired 0 times).

## YYYY-MM-DD: <idea> (positive | negative | inconclusive) — issue #N, run `runs/<id>`
- what changed
- result vs baseline (table)
- keep / drop, and why
