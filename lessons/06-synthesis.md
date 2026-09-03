# 06 — Cross-run synthesis (5 runs, 2026-09-02, T0 = 20:16 PDT)

Written by a fresh-context agent from the five worktrees, the saved review verdicts and the lessons files;
the three runs marked AGENT DIED were cut off by the subscription session limit at T+34 and resumed later.
Changes 1-12 below were applied to the scaffold on 2026-09-03 except where noted in `00-practice-problems.md`.

All five agents were killed by the same event: `You've hit your session limit · resets 12:40am` at 20:50-20:51 (T+34-35). The three "AGENT DIED" summaries are that event, not agent bugs; their state is fully recoverable from the worktrees, saved review transcripts in the scratchpad, and commit timestamps, which is what the table below is built from.

## 1. Run table

| run | active min (wall / coding) | min to baseline | issues done / planned | review rounds (completed + killed) | review min | baseline metric | deliverable quality (1-5) |
|---|---|---|---|---|---|---|---|
| eedi | 35 / ~14 (all 4 issues coded by T+18.5) | 15 (`--limit 50`), 16 (full split) | 1 merged, 3 coded-unreviewed / 4 | 2 + 1 | 13.2 (7.0, 6.2) | MAP@25 0.164 [0.144, 0.183], n=819 | 4 - complete REPORT on `practice-eedi-issue-04` with 5 sharp findings, unreviewed |
| easy2hard | 35 / ~12 | 16 | 2 merged + 1 approved-unmerged + report committed / 4 | 4 + 1 | ~18 (4-5 each) | Spearman 0.261 [0.135, 0.374] (length-only); best 0.381 | 4 - reviewed through 03, correct negative result on curricula, 5-seed CIs over-read |
| livebench | 35 / ~23 (all 5 issues coded by T+23) | 5 | 2 merged (01 merged after an unreviewed fix), 2 in REQUEST_CHANGES, 04 not started / 5 | 11 + 0 (1 APPROVE total) | ~65 (11 x 5-9, 2-3 parallel) | strict mean 0.256; o1-mini 0.713 reasoning | 3 - REPORT draft complete but only in the shared scratchpad; sign-filter bug in 02 never fixed |
| mmlupro | 35 / ~20 | 4 | 3 merged, REPORT written T+18 (review killed) / 4 | 8 + 1 | ~45 | acc sonnet-3.5 0.762 [0.754, 0.770] (Wilson) | 4 - best data archaeology (positional ids, HF-edited texts), manual check of 20 suspects; unreviewed |
| gridworld | 35 / ~12 | 3.5 (0.000, useless); ~10 for 0.133 | 2 merged, 03 committed-unreviewed / 3 | 4 + 1 (round 1 was a wrong-branch verdict) | 20.4 (3.3, 7.6, 4.6, 4.9) | held-out solve 0.107 [0.067, 0.133] (random) | 3 - honest but no signal between curricula; held-out redefined mid-run |

Across runs: coding was 12-23 minutes of a 35-minute window; the rest was waiting on 29 completed review rounds (~160 reviewer-minutes) plus 4 killed ones. Every REPORT that exists has CIs on every headline number and 5 findings; none was reviewed end to end.

## 2. Cross-cutting findings

**Consistently helped**
- One worktree per sub-issue so reviews run concurrently (easy2hard, livebench, eedi via `chain.sh`, gridworld). Biggest wall-clock saver.
- `magic.{stable_split, bootstrap_ci, wilson_interval, RunDir, write_jsonl, to_markdown}` covered every stats/IO need; zero new dependencies in 5/5 runs.
- 60-row real-data fixtures under `tests/fixtures/` made every stage script testable in ~3 s offline (easy2hard, eedi, mmlupro, livebench); tests-first caught two real bugs in easy2hard within seconds.
- The reviewer's obligations table cited `file:line` every time and caught at least one real test-as-evidence failure per run (gridworld vacuous determinism test; eedi vacuous correct-letter check; livebench wrong positive-sign test; mmlupro NaN tokens in samples.jsonl; easy2hard curriculum curves with zero seed variance).
- Local markdown issues + `ISSUE=<file>` in `review_pr.sh` made the no-GitHub setup trivial (5/5).
- Inspecting the data before slicing: livebench found "no reasoning rows in model_judgment" at T+1.5 and re-planned; mmlupro found positional ids and HF-edited texts and re-keyed. Runs that skipped it (gridworld's unlearnable held-out set) lost 5+ minutes.

**Consistently hurt**
- `tasks/` not importable: 5/5 runs, 8-10 minutes each and one blocked review round each (eedi, gridworld, mmlupro, livebench amended `pyproject.toml` inside issue 01). Already fixed (`src/magic/tasks`).
- Self-amended issue files in the implementation branch: blocked eedi 01 r1, livebench 01 r1 (note) + 03 r1 + 03 r2, mmlupro 01 r2 + r3, gridworld 01. Seven review rounds (~40 reviewer-minutes) on a process gap: the reviewer is right, but the implement skill still says only "stop and ask", so every agent improvised.
- The reviewer occupies the working tree: agents could not edit while a review ran (gridworld, livebench), a review tested whatever branch the tree was on (eedi), and one verdict came back for another run's branch (gridworld r1). Reviews take 3-9 min per round; this idle time exceeded coding time in 4/5 runs.
- Session limit: 5 agents + up to 15 concurrent `claude -p` reviewers on one subscription exhausted it at T+34 (5/5).
- Chained sub-branches + squash merge = add/add conflicts (easy2hard); eedi wrote `chain.sh` (rebase `--onto`) to cope; livebench reviewed against `BASE=issue-01`. The "branch from main only" gotcha is now in CLAUDE.md, but waiting for a 6-minute review before starting dependent work is exactly the idle time above.
- `NaN` tokens in `summary.json` / `samples.jsonl` (livebench: 3 reviewer notes; mmlupro: 1 blocking round). `to_markdown` prints integer `n` as `819.000` (eedi, mmlupro, gridworld reports).
- Script `main()` untested: the reviewer noted it (non-blocking) in eedi, gridworld, livebench x4, easy2hard; CONTRIBUTING §2 makes it a criterion, so in CI this becomes a blocking round.
- Shared scratchpad: easy2hard's REPORT draft was overwritten by livebench; livebench's final REPORT only ever lived there. Gotcha already added.

## 3. Ranked setup changes still worth making

1. **`scripts/review_pr.sh`: review in a detached temporary worktree and read the issue from BASE.** Motivated by eedi, livebench, gridworld (wrong-branch verdict, wrong-tree tests, no editing during review) and the reviewer-run `runs/easy2hard_*` clutter. Expected gain: 4-9 min per round handed back to the agent (roughly halves wall-clock), and no cross-talk. Replace the branch-mode block and the `claude` call with:
   ```bash
   # branch mode: review a pristine checkout of the branch, never the caller's working tree
   tmp=$(mktemp -d); git worktree add -q --detach "$tmp" "$target" || { echo "cannot check out $target"; exit 2; }
   trap 'git worktree remove --force "$tmp" 2>/dev/null' EXIT
   [[ -f "$issue" ]] && { git show "$ref:${issue#"$(git rev-parse --show-toplevel)/"}" > "$tmp/.issue.md" 2>/dev/null && issue="$tmp/.issue.md"; }
   (cd "$tmp" && uv sync -q --locked && [[ -d "$(git rev-parse --show-toplevel)/data" ]] && ln -s "$(git rev-parse --show-toplevel)/data" data)
   out=$(cd "$tmp" && "$CLAUDE" -p "..." ...)
   ```
   Reading the issue from `$ref` is stricter, not looser: a branch cannot ratify its own spec edit, and the diff still shows the attempt.
2. **`scripts/review_pr.sh` + `run-issues` skill: recognise the session limit.** Motivated by 5/5. After the `NO VERDICT` check add: `printf '%s' "$out" | grep -q "hit your session limit" && { echo "RATE_LIMIT: $(printf '%s' "$out" | grep -o 'resets [^"]*')" >&2; exit 3; }`. In `run-issues` step 2 replace "wait for the reset and resume them" with "on exit 3 from `make review`, stop launching, record the reset time in the status table, and resume every agent from its worktree after it". Also set `ANTHROPIC_API_KEY` for reviews (`doctor.sh` already checks it) so reviewers do not share the agents' session window. Gain: the runs would have finished instead of losing 3 reports.
3. **`.claude/skills/implement-issue/SKILL.md` step 1: the amendment procedure.** Motivated by eedi, livebench, mmlupro, gridworld (7 rounds). Append to step 1: "If the data contradicts a criterion (missing column, different format, impossible threshold), do not edit the issue in your branch. Amend it where it lives: `gh issue edit` with a comment starting `Amendment:` and why, or for a local issue file a separate `docs: amend issue N` commit on the base branch, then rebase. Shared-file edits the amendment permits go in the same base commit. Only then implement." Gain: one review round (~6 min) per data surprise; every data run had one.
4. **`src/magic/runs.py` + `src/magic/io.py`: never write `NaN`.** Motivated by livebench, mmlupro. Add in `io.py`: `def _clean(o): return None if isinstance(o, float) and math.isnan(o) else str(o)` is wrong for the general case; instead pass `default=str` plus pre-sanitise: `json.dumps(payload, indent=2, default=str, allow_nan=False)` in `write_config`/`write_summary` and `json.dumps(row, ensure_ascii=False, default=str, allow_nan=False)` in `write_jsonl`, with a helper `nan_to_none(obj)` (recursive over dict/list; converts float NaN and pandas NA to None) applied first. Gain: removes one blocking round and every `jq`/JS consumer failure.
5. **`src/magic/results.py::to_markdown`: keep integers integer.** Motivated by eedi, mmlupro, gridworld. `return df.to_markdown(floatfmt=floatfmt, intfmt="d")` and cast columns named `n*` back to int when they are whole (`df = df.assign(**{c: df[c].astype(int) for c in df if c.startswith("n") and (df[c].dropna() % 1 == 0).all()})`). Gain: cosmetic but present in every report and every reviewer note list.
6. **`src/magic/results.py::ci_by_group`: `method="bootstrap"|"wilson"` and `min_n`.** Motivated by livebench (`per_task_table`, reviewer flagged the unguarded ranking twice), mmlupro (`model_accuracy`, `category_accuracy`), eedi (`slice_table`), gridworld (n<10 note). Signature: `ci_by_group(df, group_cols, value_col="score", method="bootstrap", min_n=0, n_boot=1000)`; for `wilson` use `wilson_interval(int(g[value_col].sum()), len(g))` and require values in {0,1}; rows with `n < min_n` get `lo = hi = NaN` and are sorted last. Gain: three runs wrote this by hand and two were asked to add the guard.
7. **`tests/test_tasks_example.py`: add the script-level test every task copies.** Motivated by eedi, gridworld, livebench, easy2hard (reviewer note each time; CI would block). Add:
   ```python
   def test_example_stage_writes_a_resumable_run(tmp_path, capsys):
       from scripts.example_stage import (
           main,
       )  # scripts/ is on ruff src; add scripts/__init__.py or use runpy

       sys.argv = [
           "x",
           "--data",
           "tests/fixtures/example.jsonl",
           "--limit",
           "5",
           "--runs-root",
           str(tmp_path),
       ]
       main()
       run = next(tmp_path.glob("example__*"))
       assert {p.name for p in run.iterdir()} == {"config.json", "samples.jsonl", "summary.json"}
       assert json.loads((run / "summary.json").read_text())["n"] == 5
       assert "ALL" in capsys.readouterr().out
   ```
   plus one line in `implement-issue` step 4: "a stage script's criterion is tested by calling its `main()` on the fixture into `tmp_path` (see `tests/test_tasks_example.py`)". Gain: removes the most repeated reviewer note.
8. **`scripts/wt.sh`: symlink `data/` into new worktrees.** Motivated by mmlupro (03 r1 blocked as "unverifiable: data/raw absent from this worktree"), eedi and livebench (re-downloaded per worktree), scenarios §3. After the `uv sync` line: `[[ -d "$root/data" && ! -e "$dir/data" ]] && ln -s "$root/data" "$dir/data"`. Gain: one blocked round and one download per worktree.
9. **`plan-issues` SKILL.md step 2: two lines.** (a) "Files expected to change always lists `tests/test_<module>.py` for every module listed" (livebench 03 r2 blocked on exactly this; eedi/mmlupro pre-empted it by luck). (b) "Before slicing, run a 10-line inspection (shape, columns, join-key value counts, duplicates) and record surprises under `## Data findings` in the epic" (livebench did; mmlupro found positional ids at T+11; gridworld's held-out set was unlearnable). Gain: one round per run.
10. **`implement-issue` SKILL.md step 6: chained work while a review runs.** Motivated by easy2hard (squash conflicts), eedi (`chain.sh`), livebench (`BASE=issue-01`). Add: "While your review runs you may start a dependent issue from your branch; before *its* review run `git rebase --onto origin/main <parent-branch>` once the parent has merged, then `make test`." This keeps the CLAUDE.md rule (nothing lands unrebased) and removes the idle wait. Gain: 5-8 min per dependent issue.
11. **`src/magic/io.py::fetch_hf(repo, config=None, split="train", out=None) -> pd.DataFrame`**: `load_dataset(...).to_pandas()`, write parquet to `data/raw/<name>.parquet` if `out`, print `shape` and `dtypes`. Motivated by easy2hard (`easy2hard_fetch.py`), livebench, mmlupro (identical 10 lines each). Modest gain (~3 min) but it is the "inspect columns" step made free; keep it to ~12 lines to respect CONTRIBUTING §5.
12. **`scripts/review_pr.sh` header + `implement-issue` step 6: exit-code note.** `make` returns 2 for any recipe failure, so the 0/1/2 contract only holds when calling `scripts/review_pr.sh` directly (eedi and mmlupro both mis-read this). One sentence in each; orchestrators should parse the saved `runs/reviews/*.json` instead.

**Rejected**
- `--model claude-sonnet-5` for local pre-reviews (scenarios §7): REJECTED - a weaker local gate trades fewer local minutes for extra CI rounds; the local reviewer is the one that catches test-as-evidence failures before push. Fix the latency with #1 and #2 instead.
- "Reviewer should compare against the branch's amended issue text and not treat the edit as blocking" (livebench, eedi variants): REJECTED as stated - it lets a branch ratify its own spec. #1 (issue read from BASE) and #3 (amend on base first) give the same throughput without loosening.
- "Solo runs ratify their own amendments" (eedi): REJECTED for the real task; a human ratifies on GitHub. Practice-only convention.
- `make sweep` (gridworld only), `magic.irt` (livebench only), `ap_at_k` (eedi only), `bar_with_ci` label wrapping (eedi only), `.gitignore` fixture subdirs (eedi only), `dev/issue_template.md` + `make issue` (gridworld, livebench): the last is two runs but `plan-issues` already lists the five fields and `.github/ISSUE_TEMPLATE/task.yml` exists; a new file adds a thing to keep in sync for a 30-second copy.

## 4. Reviewer calibration

**False positives:** none in rounds that reviewed the right branch. Every blocking finding cited `file:line` and a reproduction, and the four "process" blocks (self-amended issue: eedi, livebench x2, mmlupro x2; test file not in expected files: livebench 03 r2; data absent: mmlupro 03 r1) were correct under CONTRIBUTING even where they were expensive. Those costs are fixed upstream by changes #1, #3, #8, #9, not by the reviewer.

**False negatives / inconsistencies:**
- Severity drift on the same defect across rounds: livebench 02 reported the missing `proxy < 0` filter (suspect list padded with positive-proxy items) as a *note* in r1 and r2, then *blocking* in r3; NaN-in-JSON was a note three times in livebench and blocking in mmlupro 01 r3. The rule in step 9 already makes both blocking; the wording lets "narrow" defects slide.
- gridworld 01: the manhattan-distance test runs on one level only and `gridworld_train.py` has no test; both noted as non-blocking because the issue did not ask. Correct per rules; fix via #7 and #9.
- livebench 01 was merged after an unreviewed fix (r3 REQUEST_CHANGES at 20:41, fix at 20:41, merge at 20:44). Process, not reviewer; #2 and the `run-issues` status table make this visible.
- Cross-talk: gridworld 01 r1 returned a verdict for `practice-mmlupro-issue-01`. The `target` check now catches it; #1 removes the cause.

**Exact SKILL.md change** (`.claude/skills/review-pr/SKILL.md`, step 9, append one sentence):
> "A defect that meets this bar is blocking in every round including the first; never downgrade it to a note because the trigger is narrow, and treat an output file that is not valid JSON (`NaN`, `Infinity`) as a defect."

Nothing else in the skill should change; the three-note cap and "unverifiable counts as not met" both earned their keep.

## 5. Generic utilities re-implemented by two or more runs (not yet in `src/magic`)

- `ci_by_group(df, group_cols, value_col="score", method="bootstrap"|"wilson", min_n=0) -> DataFrame[n, mean, lo, hi]` - livebench `per_task_table`, mmlupro `model_accuracy`/`category_accuracy`, eedi `slice_table` (extend the existing function).
- `nan_to_none(obj) -> obj` used by `RunDir.write_config/write_summary` and `write_jsonl` with `allow_nan=False` - livebench, mmlupro.
- `to_markdown(df, floatfmt=".3f", intfmt="d")` - eedi, mmlupro, gridworld.
- `fetch_hf(repo, config=None, split="train", out=None) -> pd.DataFrame` printing shape and dtypes - easy2hard, livebench, mmlupro.
- Script-level test pattern `main()` on fixture into `tmp_path` (a test, not a helper) - eedi, gridworld, livebench, easy2hard.
- `extract(text, mode="strict"|"lenient", first=True)` returning `None` on format failure, with a `runaway` flag when first and last strict matches differ - mmlupro `extract_strict(last=)`, livebench `extract_answer(mode)`; the example task already has strict/lenient, so add `first: bool` and the runaway helper there rather than a new module.

Already present and used correctly by later runs: paired `bootstrap_ci`, `plots.line_with_ci`, `results.ci_by_group`, `load_runs` config columns, `magic.tasks`.

## 6. Scenario risks for the real task

1. **Subscription window exhausted** - 5 agents + 11-15 concurrent reviewers died at T+34 (5/5). Mitigation: reviews on `ANTHROPIC_API_KEY`, parallelism 3, `review_pr.sh` exit 3 on limit and the orchestrator pauses until the printed reset time.
2. **Reviewer runs on the working tree, not the branch** - wrong-branch verdict (gridworld), reviewed whatever the tree was on (eedi), agents frozen for 4-9 min per round (livebench, gridworld). Mitigation: change #1.
3. **`data/raw` is per worktree** - mmlupro 03 blocked as unverifiable; every worktree re-downloads. Mitigation: `wt.sh` symlink (#8); HF cache is already shared.
4. **Data schema surprises are the norm** - no reasoning judgments (livebench), positional ids + duplicates + HF-edited texts and answers (mmlupro), different column names per config (easy2hard), correct-answer rows with null labels (eedi), 45 duplicate (model, question) rows (livebench). Mitigation: data-findings step (#9) and `fetch_hf` printing the schema (#11); budget 15 minutes in issue 1.
5. **Self-amended specs** - 7 blocked rounds. Mitigation: #3; on GitHub the amendment is an issue comment plus `gh issue edit`, ratified by the human.
6. **Chained branches** - squash add/add conflicts (easy2hard); reviews against intermediate bases (livebench). Mitigation: #10 (`rebase --onto`) and short dependency chains in waves.
7. **Shared scratch directory** - overwritten REPORT (easy2hard), report only in scratch (livebench). Mitigation: already a CLAUDE.md gotcha; `run-issues` prompt says "scratch inside your worktree".
8. **Format hook rewrites files mid-edit** - dropped `# noqa`, reordered imports, silent no-op replacements (easy2hard, gridworld). Mitigation: gotcha present; the `sys.path` hack that triggered it is gone with `magic.tasks`.
9. **Degenerate metric or baseline** - held-out set unlearnable (gridworld 0.000), target is a function of the ordering key (easy2hard). Mitigation: plan-issues line present; the human fixes held-out definition and target before issue 2.
10. **Invalid JSON in run outputs** - `NaN` tokens break `jq` and downstream loaders (livebench, mmlupro). Mitigation: #4.
11. **Review latency under CPU contention** - 6 `claude` processes on one laptop gave 3.3-9 min per round; 29 rounds in 35 minutes. Mitigation: #1 (agents keep working), cap concurrency, script-level tests (#7) so first-round approvals rise (they were 4 of 15 first rounds here).
12. **`make review` exit code** - `make` returns 2 for both REQUEST_CHANGES and no-verdict; two orchestrating scripts mis-read it. Mitigation: parse `runs/reviews/<branch>__*.json` (#12).
13. **Small-n intervals over-read** - 5 seeds (easy2hard, gridworld), 30 held-out levels where one level is 0.033. Mitigation: `min_n` in `ci_by_group` (#6) and report AUC alongside the final checkpoint, as gridworld did.

Sources: `/Users/dejan/Desktop/work/magic_setup/lessons/{02-easy2hard,05-gridworld,scenarios}.md`; REPORTs at `/Users/dejan/Desktop/work/magic_setup/.claude/worktrees/practice-{easy2hard,gridworld}/dev/practice/*/REPORT.md`, `practice-mmlupro-issue-04/dev/practice/mmlupro/REPORT.md`, `git show practice-eedi-issue-04:dev/practice/eedi/REPORT.md`; dead-run drafts and all 29 verdicts under `/private/tmp/claude-501/-Users-dejan-Desktop-work-magic-setup/fc3f9cef-f4bc-4321-b5b7-87169c625939/scratchpad/` (`lessons-draft.md` = eedi, `lessons_head.md` + `setup_changes.md` + `REPORT.md` = livebench, `mmlupro_review0*_r*.txt`, `review0*-r*.json`, `chain.sh`).
