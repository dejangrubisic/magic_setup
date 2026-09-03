"""Stage 1: score LiveBench reasoning answers and print per-task accuracy for the top 10 models.

uv run python scripts/livebench_baseline.py [--limit N] [--raw data/raw/livebench]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.livebench import MODES, TASKS, load_reasoning, score_rows

from magic import RunDir, wilson_interval


def per_task_table(df: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Top `top` models by overall strict mean; cells are `mean [lo, hi]` Wilson intervals."""
    overall = df.groupby("model")["strict"].mean().sort_values(ascending=False)
    rows = []
    for model in overall.index[:top]:
        sub = df[df["model"] == model]
        row = {"model": model, "overall": f"{overall[model]:.3f} (n={len(sub)})"}
        for task in TASKS:
            s = sub.loc[sub["task"] == task, "strict"]
            p, lo, hi = wilson_interval(int((s == 1.0).sum()), len(s))
            row[task] = f"{p:.3f} [{lo:.3f}, {hi:.3f}] n={len(s)}"
        rows.append(row)
    return pd.DataFrame(rows).set_index("model")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="max questions")
    ap.add_argument("--raw", default="data/raw/livebench")
    ap.add_argument("--runs", default="runs")
    args = ap.parse_args(argv)

    df = load_reasoning(args.raw)
    if args.limit:
        keep = sorted(df["question_id"].unique())[: args.limit]
        df = df[df["question_id"].isin(keep)].reset_index(drop=True)
    for mode in MODES:
        df[mode] = score_rows(df, mode)

    run = RunDir.new(args.runs, "livebench_baseline")
    run.write_config({"limit": args.limit, "raw": args.raw, "n_rows": len(df)})
    for _, r in df.iterrows():
        run.append(
            {
                "id": f"{r.model}|{r.question_id}",
                "model": r.model,
                "question_id": r.question_id,
                "task": r.task,
                "strict": r.strict,
                "lenient": r.lenient,
            }
        )
    table = per_task_table(df)
    run.write_summary(
        {
            "n_models": int(df["model"].nunique()),
            "n_questions": int(df["question_id"].nunique()),
            "strict_mean": float(df["strict"].mean()),
            "lenient_mean": float(df["lenient"].mean()),
            "per_task_top10": table.reset_index().to_dict("records"),
        }
    )
    print(
        f"run: {run.path}  models={df['model'].nunique()} questions={df['question_id'].nunique()}"
    )
    print(table.to_markdown())


if __name__ == "__main__":
    main()
