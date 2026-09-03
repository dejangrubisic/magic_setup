"""Stage 2: 1PL IRT on the strict score matrix; hardest items and label-error suspects.

uv run python scripts/livebench_irt.py [--limit N] [--raw data/raw/livebench]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.livebench import load_reasoning, score_matrix
from tasks.livebench_irt import discrimination_proxy, fit_1pl

from magic import RunDir


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
    matrix = (
        (score_matrix(df, "strict") == 1.0).astype(float).where(score_matrix(df, "strict").notna())
    )
    ability, difficulty = fit_1pl(matrix)
    proxy = discrimination_proxy(matrix, ability)
    meta = df.drop_duplicates("question_id").set_index("question_id")[["task", "ground_truth"]]
    items = pd.DataFrame(
        {
            "task": meta["task"].reindex(matrix.columns),
            "difficulty": difficulty,
            "discrimination_proxy": proxy,
            "pass_rate": matrix.mean(),
            "ground_truth": meta["ground_truth"].reindex(matrix.columns),
        }
    )
    items.index.name = "question_id"
    hardest = items.sort_values("difficulty", ascending=False).head(15)
    negative = items[items["pass_rate"] > 0].sort_values("discrimination_proxy").head(5)

    run = RunDir.new(args.runs, "livebench_irt")
    run.write_config({"limit": args.limit, "raw": args.raw, "C": 1.0})
    for item, row in items.iterrows():
        run.append({"id": item, **row.to_dict()})
    run.write_summary(
        {
            "n_models": int(matrix.shape[0]),
            "n_items": int(matrix.shape[1]),
            "ability_top5": ability.sort_values(ascending=False).head(5).round(3).to_dict(),
            "difficulty_by_task": items.groupby("task")["difficulty"].mean().round(3).to_dict(),
            "hardest_15": hardest.reset_index().to_dict("records"),
            "negative_discrimination_5": negative.rename(columns={"discrimination_proxy": "proxy"})
            .reset_index()
            .to_dict("records"),
        }
    )
    print(f"run: {run.path}  models={matrix.shape[0]} items={matrix.shape[1]}")
    print("\n## 15 hardest items\n")
    print(hardest.drop(columns="ground_truth").to_markdown(floatfmt=".3f"))
    print("\n## 5 negative-discrimination suspects\n")
    print(negative.to_markdown(floatfmt=".3f"))


if __name__ == "__main__":
    main()
