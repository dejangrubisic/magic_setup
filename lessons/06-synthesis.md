# 06 — Cross-run synthesis (five practice runs, written after the resumed runs finished)

# Practice runs: cross-run synthesis (five runs; three resumed on 2026-09-03)

Sources: `lessons/0{0..5}-*.md`, `lessons/06-synthesis.md` (first-pass synthesis; its changes 1-12 are on `main` as of `c9aba05`/`ad87fb9`), the three resume summaries, the current `CLAUDE.md`, `CONTRIBUTING.md`, `Makefile`, `.claude/skills/*/SKILL.md`, `scripts/*.sh`, `src/magic/**`, the saved verdicts under `.claude/worktrees/practice-{eedi,livebench-issue-02,livebench-issue-05}/runs/reviews/`, and each `dev/practice/<name>/REPORT.md` (eedi's via `git show practice-eedi-issue-04:dev/practice/eedi/REPORT.md`; it is not on the base branch).

## 1. Run table

| run | active min | min to baseline | issues done / planned | review rounds (completed + lost) | review min | baseline metric | deliverable quality (1-5) |
|---|---:|---:|---|---|---:|---|---|
| eedi | 53 (16 agent A coding, rest review + resume) | 13 (`--limit 50`), 14 (full) | 3 merged / 4; 04 complete on its branch, `needs-human` after 3 rounds | 7 + 3 (lost to the script edit) | 40 | TF-IDF MAP@25 0.164 [0.144, 0.183], n=819; no-construct 0.109 | 4: sharp, every finding cites a table, but unmerged and two numbers labelled ad hoc |
| easy2hard | 35 (killed at the limit, not resumed) | 16 | 2 merged / 4; 03 fixed, 04 written, both unreviewed since | 4 + 1 | ~18 | Spearman 0.261 [0.135, 0.374] length-only; best 0.381 | 4: clean tables, correct negative curriculum result; 5-seed CIs over-read |
| livebench | 51 (36 A + 15 B) | 7 | 3 / 5 merged clean; 02 and 05 merged with open REQUEST_CHANGES; 04 report on base | 8 + 2 (script edit) | 47 | strict mean 0.256 -> 0.275 after #05; o1-mini 0.753 | 3: well-cited report from re-runs, but two merged issues carry open blocking findings |
| mmlupro | 38 (30 A + 8 B) | 0 (`--limit 50` run predates the first commit) | 4 / 4; 04 merged with no verdict | 7 + 2 (r1 killed, r2 unfinished at hard stop) | 36 | sonnet-3.5 acc 0.761 [0.753, 0.769] Wilson, n=12,030 | 4: best analysis (re-key by text, 7/20 label errors hand-checked), never reviewed, `n` prints as 12032.000 |
| gridworld | 35 (killed, not resumed) | 3.5 (0.000, useless); ~10 for 0.133 | 2 merged / 3; 03 (analysis + report) committed, unreviewed | 4 + 1 (round 1 was a wrong-branch verdict) | 20 | held-out solve 0.107 [0.067, 0.133] random | 3: honest null result, held-out set redefined mid-run |

Coding was 12-23 min per run; reviewer wall-clock was 18-47 min per run (mean 5.2 min, $1.5-3.0 per round). In the three resumed runs the deliverable (REPORT) was the last thing in the chain and the first casualty of every kill.

## 2. Cross-cutting findings

**Consistently helped**
- One worktree per sub-issue and reviews in parallel: eedi's three resume reviews took 4.8 min wall instead of ~12.5 serial; easy2hard, livebench, mmlupro ran 2-3 rounds concurrently. (easy2hard, livebench, mmlupro, eedi-B)
- The `magic` utilities covered every stats/IO need with zero new dependencies (5/5), and full pipelines run in seconds (eedi 0.8 s, livebench 1-2 s, mmlupro 14 s, gridworld 65 s), so re-verifying every report number after a resume was free. (eedi, livebench, mmlupro)
- Small real fixtures plus tests-first: easy2hard caught two real bugs in seconds; eedi's ranking tests run in 40 ms and let the reviewer verify ACs without the full data. (easy2hard, eedi, mmlupro, livebench)
- Inspecting data before slicing and writing the finding into the epic: livebench (no reasoning rows) at T+3, mmlupro (positional ids, HF-edited texts; all-fail set under-counted 53% before the re-key). Runs that skipped it lost 5+ min (gridworld's unlearnable held-out set). (livebench, mmlupro, gridworld)
- Git as the only state: reflog, run-dir timestamps, `config.json.git_sha`, `(#NN)` squash subjects and amendments committed on the base branch let resumed agents map state in 1-2 min; the hand-written state note was wrong. (eedi, livebench, mmlupro)
- Reviewer precision: zero false positives in the 7 new-era verdicts read (eedi 5, livebench 2); every block cited `file:line` and a reproduction; it found latent bugs the authors missed (eedi label collision, livebench `fit_1pl` order, mmlupro NaN tokens, livebench "extracted" functions the script never calls). (eedi, livebench, mmlupro)

**Consistently hurt**
- Review latency dominated wall-clock: 3.5-8 min per round, 36-47 review-min in 38-53 active-min resumed sessions. (5/5)
- Nothing persisted at the kill: the old script printed verdicts to stdout; resume needed reflog forensics and the mmlupro 04 r1 round vanished entirely. (eedi, livebench, mmlupro)
- Editing `scripts/review_pr.sh` on `main` (commit `ad87fb9`, 08:36:58) while resumed agents were executing it killed 5 reviews (~25 min, ~$8). (eedi, livebench)
- The report last, and prose numbers with no scripted source: eedi's report issue ate 5 rounds across two agents on three different unscripted/over-claimed numbers; mmlupro's draft table came from a pre-fix run (0.1-0.3 pt drift, a model row missing); livebench's report did not exist when agent A died. (eedi, mmlupro, livebench)
- Chained sub-branches: add/add conflicts (easy2hard), three chain rebases (eedi), manual `rebase --onto` (livebench), 3 of 4 branches rebased and reviews pointed at an unmerged base (mmlupro). The skill and CLAUDE.md currently contradict each other on this. (easy2hard, eedi, livebench, mmlupro)
- Data downloaded into a worktree instead of the main checkout: one wasted 5-min round (mmlupro 03 r1) and per-worktree downloads. (mmlupro, eedi, livebench, easy2hard)
- Process violations under deadline: branches merged before their verdicts arrived (livebench 02/05, mmlupro 04); both livebench verdicts came back REQUEST_CHANGES with valid findings. (livebench, mmlupro)
- Silent no-op scripted text edits (a `replace` that matched nothing across a line wrap or after the format hook rewrapped the line) and hook rewrites dropping `# noqa`. (eedi, easy2hard, gridworld)
- A ~50 min harness stall (08:36-09:33) in all three resumed sessions, blowing every wall-clock budget with zero agent activity. (eedi, livebench, mmlupro)

## 3. Ranked setup changes still worth making

Already on `main`, not re-proposed: `src/magic/tasks`, paired `bootstrap_ci`, `plots.line_with_ci`, `results.ci_by_group` (Wilson, `min_n`), `load_runs` configs, `to_markdown` integer `n*`, `magic.io.dumps` NaN-safe, `fetch_hf`, detached-worktree review with issue read from base, saved verdicts + target check + dirty/empty guards + rate-limit exit 3, `wt.sh` data symlink, amendment procedure, `tests_on_base.sh`, the review-skill "narrow defects block / invalid JSON is a defect" lines, CLAUDE.md gotchas (hooks, failed commits, branch from main, worktree scratch, data in main checkout).

### 1. `scripts/review_pr.sh`: run from an in-memory copy (eedi, livebench)
Insert directly after the comment header, before `set -uo pipefail`:
```bash
# bash reads a script lazily: re-exec from an in-memory copy so an edit to this file cannot kill a running review.
[[ -n "${_REVIEW_PR_INMEM:-}" ]] || { _REVIEW_PR_INMEM=1 exec bash -c "$(cat "$0")" "$0" "$@"; }
```
Gain: removes the failure that cost 5 reviews (~25 min, ~$8) in one morning; folds in livebench's proposed CLAUDE.md gotcha, which is then unnecessary.

### 2. `scripts/review_pr.sh`: persist something on every exit path (eedi, mmlupro, livebench)
Replace the block from `start=$(date +%s)` to the `NO VERDICT` check with:
```bash
mkdir -p "$root/runs/reviews"
file="$root/runs/reviews/${label}__$(date +%Y%m%d-%H%M%S).json"; raw="${file%.json}.raw"
start=$(date +%s)
null_verdict() { printf '{"target": "%s", "verdict": null, "reason": "%s", "elapsed_s": %s}\n' "$target" "$1" "$(( $(date +%s) - start ))" > "$file"; echo "NO VERDICT ($1) after $(( $(date +%s) - start ))s -> $file" >&2; }
trap 'null_verdict killed; exit 2' TERM INT
out=$(cd "$workdir" && "$CLAUDE" -p "..." ... 2>/dev/null)     # unchanged
elapsed=$(( $(date +%s) - start ))
printf '%s\n' "$out" > "$raw"        # full transcript survives a rate limit, a bad verdict or a kill
if printf '%s' "$out" | grep -q "hit your session limit"; then
  null_verdict rate_limit; echo "RATE_LIMIT: $(printf '%s' "$out" | grep -o 'resets [^"]*' | head -1)" >&2; exit 3
fi
verdict_json=$(...)   # unchanged
[[ -n "$verdict_json" ]] || { null_verdict no_verdict; printf '%s\n' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("result","")[:3000])' >&2; exit 2; }
```
and delete the later `mkdir -p` / `file=` lines. Gain: a resumed agent reads one file instead of reconstructing rounds from reflog (1-3 min per resume, 3/3 runs) and a killed round leaves its partial obligations table (mmlupro 04 r1 left nothing). Livebench's "distinct exit codes 2 vs 4" is rejected: `make` flattens every failure to 2 anyway; orchestrators read the file.

### 3. `scripts/review_pr.sh` + `scripts/wt.sh`: resolve `data/` from the main checkout (mmlupro, eedi, livebench, easy2hard)
In `review_pr.sh` replace the `ln -s "$root/data"` line and the `echo "reviewing ..."` line with:
```bash
data="$root/data"; [[ -d "$data" ]] || data="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/data"
[[ -d "$data" && ! -e "$tmp/data" ]] && ln -s "$data" "$tmp/data"
echo "reviewing $target ($n commits over $ref) against $issue in $tmp; data: $data$([[ -d "$data" ]] || echo ' (MISSING)')" >&2
```
In `wt.sh` replace the data symlink line with:
```bash
main=$(dirname "$(git -C "$root" rev-parse --path-format=absolute --git-common-dir)")
[[ -d "$main/data" && ! -e "$dir/data" ]] && ln -s "$main/data" "$dir/data"   # one download per machine
```
Gain: one 5-min round (mmlupro 03 r1 "data/raw/mmlupro does not exist") and one download per worktree; a missing dataset becomes a header line, not a verdict. The CLAUDE.md line stays as is.

### 4. `plan-issues` + `implement-issue`: the report is scripted, skeletoned early, and regenerated last (eedi, mmlupro, livebench)
`plan-issues` step 2, add a bullet:
> - The report issue has fixed criteria: every number in `REPORT.md` and its `dev/LOG.md` entry is in a table written by a named script run on the base branch after the last dependency merged, with the run id cited; any other number is labelled `ad hoc` or removed. Statistics the report will want (Hit@k, per-group counts, extra CIs) are criteria of the issue that produces them and land in `summary.json`, never in prose.

`plan-issues` step 4, add:
> Commit `dev/<task>/REPORT.md` with the epic as a skeleton: one heading per issue naming the script and the table it will cite, no numbers. Only the report issue edits it afterwards, so it stays out of every other issue's "Files expected to change".

`implement-issue` step 4, add one sentence:
> A report issue starts with `git rebase origin/main` (all dependencies merged) and a fresh run of every script it cites; paste only from those run ids.

Gain: eedi's 5 report rounds (~25 min) become 1-2; mmlupro's drift and missing row cannot happen; a killed run leaves a partial report. Livebench's variant ("every issue appends its table to the report") is rejected: it makes `REPORT.md` a shared file across parallel issues.

### 5. `implement-issue` step 6: remove the contradiction with CLAUDE.md on chained branches (easy2hard, eedi, livebench, mmlupro)
Replace the last sentence of step 6 ("While a review runs you may start a dependent issue from this branch; ... `git rebase --onto origin/main issue-$ARGUMENTS` and `make test`.") with:
> While the review runs you may start another *independent* ready issue in its own worktree (`make wt`); a dependent issue waits for this one to merge (CLAUDE.md: branch from `origin/main` only).

Gain: every run paid 2-5 min per chained branch (conflicts, `rebase --onto`, reviews against an unmerged base); the reviewer reads CLAUDE.md, so the contradiction also risks a scope finding. This is a deletion of a permission, not new procedure; `run-issues` already defines "ready" as dependencies closed.

### 6. `Makefile` + `scripts/merge_issue.sh`: local squash-merge that requires a saved APPROVE (easy2hard, livebench, mmlupro, eedi)
```make
.PHONY: merge-issue
merge-issue: ## Local squash-merge of a reviewed branch into its base: make merge-issue B=<branch> N=<nn> MSG="<type>: <what>" [BASE=main] [FORCE=1]
	FORCE="$(FORCE)" scripts/merge_issue.sh $(B) $(N) "$(MSG)" $(BASE)
```
```bash
#!/usr/bin/env bash
# Local (no-GitHub) equivalent of gh pr merge --squash. Run from the branch's own worktree.
#   scripts/merge_issue.sh <branch> <nn> "<type>: <what>" [base=main]; FORCE=1 skips the verdict check (log why in dev/LOG.md)
set -euo pipefail
b=$1; n=$2; msg=$3; base=${4:-main}
[[ "$(git rev-parse --abbrev-ref HEAD)" == "$b" ]] || { echo "run from the worktree of $b"; exit 2; }
latest=$(grep -l '"verdict": "APPROVE"' $(ls -t runs/reviews/"$b"__*.json 2>/dev/null) 2>/dev/null | head -1)
[[ -n "$latest" || "${FORCE:-}" == 1 ]] || { echo "no APPROVE verdict for $b in runs/reviews/ (FORCE=1 to override, then log it)"; exit 2; }
git rebase "$base" && make test
bd=$(git worktree list --porcelain | awk -v r="refs/heads/$base" '$1=="worktree"{d=$2} $1=="branch"&&$2==r{print d}')
[[ -n "$bd" ]] || { echo "$base is not checked out in any worktree"; exit 2; }
git -C "$bd" merge --squash "$b" && git -C "$bd" commit -q -m "$msg (#$n)" && git -C "$bd" log -1 --oneline
```
Gain: 2-3 min per merge (four manual commands with a conflict trap in every run) and the unreviewed merges of livebench 02/05 and mmlupro 04 become an explicit `FORCE=1`. Unnecessary once GitHub auto-merge is in use; keep until the loop is tested end to end (scenarios.md, last section).

### 7. `Makefile`: `make status` (eedi, livebench, mmlupro)
```make
.PHONY: status
status: ## Resume map: issue branches by date, worktrees, latest saved verdicts: make status [P=issue-]
	@git for-each-ref --sort=committerdate --format='%(committerdate:short) %(refname:short)  %(subject)' "refs/heads/$(or $(P),issue-)*"
	@git worktree list
	@ls -t runs/reviews/*.json .claude/worktrees/*/runs/reviews/*.json 2>/dev/null | head -20
```
Gain: 1-3 min per resume in three runs, and it replaces the hand-written state note that said "03 and 04 untouched" when both were fully committed (would have cost two re-implemented issues).

### 8. `scripts/review_pr.sh` + `review-pr` SKILL step 1: local re-reviews see the previous verdict (eedi, mmlupro, livebench)
In branch mode, after the issue-file block:
```bash
prev=$(grep -l '"verdict": "' $(ls -t "$root/runs/reviews/${target}__"*.json 2>/dev/null) 2>/dev/null | head -1)
[[ -n "$prev" ]] && cp "$prev" "$tmp/.previous_verdict.json"
```
Skill step 1, append: "Branch mode: a `.previous_verdict.json` in the checkout is your earlier verdict on this branch; apply the same re-review rule." Gain: consistency with PR mode; rounds shorten (eedi 04 grew 4.2 -> 5.5 -> 7.7 min re-deriving everything). New blocking findings are still reported, so this does not loosen anything.

### 9. `src/magic/runs.py`: `RunDir(path)` opens, `RunDir.new` creates (eedi, flagged in two separate reviews; every `--run <id>` reader in every run has the same hole)
```python
def __init__(self, path: str | Path) -> None:
    self._path = Path(path)
    if not self._path.is_dir():
        raise FileNotFoundError(f"no such run dir: {self._path}")


@classmethod
def new(cls, root: str | Path = "runs", name: str = "run") -> RunDir:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return cls(ensure_dir(Path(root) / f"{name}__{stamp}__{secrets.token_hex(3)}"))
```
`tests/test_results.py` lines 18, 22, 95: wrap the path in `ensure_dir(...)`. Gain: a mistyped `--run` fails immediately instead of creating an empty dir that `load_runs` then picks up; removes a recurring reviewer note.

### 10. `CLAUDE.md` Gotchas, one line (eedi, easy2hard, gridworld)
> - A scripted edit (`str.replace`, `sed`) that matches nothing is silent, and the format hook rewraps lines between your edits: assert exactly one match, or `git diff` before committing a text fix.

Gain: two commits claimed changes they did not contain; caught only by grepping afterwards.

**REJECTED**
- Any loosening of the reviewer: "accept the branch's own amendment" (eedi, livebench variants), "downgrade narrow defects to notes", "skip data-dependent criteria when `data/` is absent" (implied by mmlupro 03 r1), "cheaper model for local reviews" (scenarios §7). The mmlupro block was an environment failure fixed by #3, not by telling the reviewer to pass unverifiable obligations; `unverifiable = not met` is the rule that caught the unscripted report numbers.
- One run only, no generalising reason: `hit_at_k` (eedi; #4 puts it in the task's `summary.json`), `bar_with_ci` label de-dup (eedi), `rekey_by_text` (mmlupro; a five-line normalised-text merge that belongs in the task module, with the id-agreement rate under Data findings), exit codes 2 vs 4 (livebench), CLAUDE.md reconciliation of `tasks/` vs `src/magic/tasks/` (eedi; practice branches only, the real task starts from `main`), "rebase the practice branch onto main before resuming" (livebench; real issues already rebase in step 7), a stall detector in the orchestrator (not a repo change; see risk 10).
- "One worktree per sub-issue" in `implement-issue` (eedi): already the design; eedi's chain was one agent doing four issues, which CONTRIBUTING §7 forbids.

## 4. Reviewer calibration

**False positives.** None in the 7 new-era verdicts (eedi 02/03 APPROVE with accurate notes; eedi 04 r1-r3 each blocked on one real prose defect; livebench 02 and 05 blocked on real problems). Environment-caused blocks: mmlupro 03 r1 (data invisible, fixed by #3); gridworld 01 r1 wrong-branch verdict (fixed by the detached worktree and target check). Pedantic-but-true notes: LOG tag vocabulary (eedi r2), unverifiable leaderboard figure (eedi r3), `--min-n` flag not in the issue (eedi 02). Nothing to change.

**False negatives.**
- eedi 04 r1: `REPORT.md` cites run `eedi_baseline__20260902-203158` whose `config.json.git_sha` is `cf0529f`, the epic commit, i.e. the run was produced by uncommitted code. Not flagged. The reviewer's checkout has no `runs/`, so it cannot check shas; #4 makes "run on the base after the last merge, cite the id" an obligation the reviewer can test by re-running the script, which the eedi r3 reviewer already did on its own (re-measured 0.081 vs 0.199).
- livebench 02 (agent A, r2): approved a commit claiming `item_table`/`binarise` were "extracted from the script" while the script still inlined the logic and never called them; agent B's reviewer caught it under the current skill (step 8, claims not backed by the diff). No wording change needed; the current skill already caught it.
- mmlupro 04: never reviewed; the 0.762 vs 0.761 drift and missing gpt-4o row were found by the resuming agent. Covered by #4 and #6 (merge requires a verdict).
- Severity drift on NaN (livebench notes vs mmlupro block) is closed by the step-9 wording already on `main`.
- The three-round cap worked as intended on eedi 04 (`needs-human`, three real findings); mmlupro 01 went to four rounds, i.e. agent A ignored the cap. No change.

**Exact SKILL.md wording change:** only the branch-mode re-review sentence in #8. The report-number rule goes into the issue template (#4), where the reviewer enforces it as an obligation, rather than into the skill; that keeps the skill short and the reviewer exactly as strict.

## 5. Generic utilities re-implemented by two or more runs (not yet in `src/magic`)

- `fmt_ci(point, lo, hi, n=None, digits=3) -> str` producing `0.500 [0.366, 0.634] n=50`: livebench per-task table, mmlupro category x model table, easy2hard curriculum table.
- `ci_pivot(df, index, columns, value_col="score", method="wilson", min_n=0) -> DataFrame` of `fmt_ci` strings (rows = index, cols = columns; `ci_by_group([index, columns])` then pivot): livebench (model x task), mmlupro (category x model).
- `RunDir` open-vs-create split (#9): eedi slices/confusion, livebench irt/taxonomy, gridworld analysis all open existing runs by id.
- Not worth wrapping (CONTRIBUTING §5), but worth one line under `plan-issues` Data findings: `df.sort_values(ts).drop_duplicates(keys, keep="last")` for duplicate (model, item) rows: livebench (45 rows), mmlupro (Llama-3-70B file).
- Not code: the "assert exactly one match" text-edit discipline (eedi, easy2hard) is #10.

Present already and used correctly by the later runs: paired `bootstrap_ci`, `wilson_interval`, `ci_by_group`, `line_with_ci`, `load_runs` configs, `fetch_hf`, `nan_to_none`/`dumps`, integer `n*` in `to_markdown`, strict/lenient/`runaway` extractors in `magic.tasks.example`, the script-level test in `tests/test_tasks_example.py`.

## 6. Scenario risks for the real task

1. **Session limit with N agents + reviewers**: 5 agents + up to 15 reviewers died at T+34 (5/5); the resumed mmlupro lost another round the same way. Mitigation: reviews on `ANTHROPIC_API_KEY`, parallelism 3, exit 3 handling in `run-issues`, and #2 so a killed round leaves a file.
2. **Editing `main`'s scripts or skills while agents run**: 5 reviews killed in one morning. Mitigation: #1; apply setup changes only between waves.
3. **The report dies with the run** (3/3 resumed runs). Mitigation: #4 skeleton with the epic; scenarios §10 (at T-30 only the report issue remains).
4. **Report numbers drift from merged code** (mmlupro; eedi ad hoc numbers). Mitigation: #4, and pipelines that run in seconds so regeneration is free.
5. **Chained branches** (5/5 paid a rebase or a conflict). Mitigation: #5 and `run-issues` waves; #6 for local merges.
6. **Data downloaded where the reviewer cannot see it** (mmlupro, eedi). Mitigation: #3.
7. **Schema surprises in every dataset** (no reasoning judgments, positional ids, HF-edited texts, duplicate rows, null-label correct answers, per-config column names). Mitigation: the Data-findings step and `fetch_hf`; budget 15 min in issue 1.
8. **Shared scratch directory** (easy2hard draft overwritten, livebench report only in scratch, mmlupro transcripts survived by prefix). Mitigation: gotcha and `run-issues` prompt already say worktree-only scratch.
9. **Silent no-op edits and hook rewrites** (eedi, easy2hard, gridworld). Mitigation: #10.
10. **Harness stall**: ~50 min with no tool output in all three resumed sessions in the same window (08:36-09:33), unrelated to any review. Mitigation: the orchestrator logs tool-call timestamps and budgets active minutes; agents commit before every long wait so a kill loses nothing.
11. **Merging under deadline without a verdict** (livebench 02/05 both came back REQUEST_CHANGES; mmlupro 04 never got one). Mitigation: #6 `FORCE=1` plus the existing `dev/LOG.md` override rule.
12. **Wrong hand-written resume state** (eedi). Mitigation: #7.
13. **Stale worktrees after setup changes**: branches forked before a fix keep the old `RunDir` (bare NaN in livebench's IRT summary), old skills and old scripts. Mitigation: in the real task every issue branches from `origin/main` at launch; apply setup changes between waves only.
14. **Degenerate baseline or coupled metric** (gridworld 0.000; easy2hard ordering key = label). Mitigation: plan-issues line present; a human fixes held-out and target before issue 2.
15. **Reviewer cost and latency**: ~44 rounds across five runs at 3.5-8 min and $1.5-3 each. Mitigation: first-round approvals via the script-level test pattern and the amendment rule; the three-round cap; #8 for shorter re-rounds.
