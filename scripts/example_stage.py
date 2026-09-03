"""Template pipeline stage. Copy to scripts/<task>_<stage>.py. Every stage: --limit, resumable RunDir, table.

uv run python scripts/example_stage.py --data tests/fixtures/example.jsonl --limit 10
"""

from __future__ import annotations

import argparse

from magic import RunDir, bootstrap_ci, by_slice, load_runs, to_markdown
from magic.tasks.example import extract_strict, load_rows, score


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--run-dir", default=None, help="resume into an existing run dir")
    ap.add_argument("--runs-root", default="runs")
    args = ap.parse_args()

    run = RunDir(args.run_dir) if args.run_dir else RunDir.new(args.runs_root, "example")
    run.write_config(vars(args))
    done = run.done_ids()
    for row in load_rows(args.data, args.limit):
        if row["id"] in done:
            continue
        pred = extract_strict(row["input"])
        run.append({**row, "pred": pred, "score": score(pred, row["target"])})

    scores = [s["score"] for s in run.samples()]
    point, lo, hi = bootstrap_ci(scores)
    run.write_summary({"n": len(scores), "score": point, "lo": lo, "hi": hi})
    _, samples = load_runs(args.runs_root)
    print(to_markdown(by_slice(samples[samples["run"] == run.path.name], "metadata.category")))


if __name__ == "__main__":
    main()
