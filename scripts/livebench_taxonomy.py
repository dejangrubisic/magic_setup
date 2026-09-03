"""Stage 3: strict vs lenient agreement and failure taxonomy for one reasoning task.

uv run python scripts/livebench_taxonomy.py [--task zebra_puzzle] [--limit N]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.livebench import TASKS, load_reasoning, score_rows
from tasks.livebench_taxonomy import (
    CLASSES,
    agreement,
    bottom_quartile_items,
    classify,
)

from magic import RunDir


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="zebra_puzzle", choices=TASKS)
    ap.add_argument("--limit", type=int, default=None, help="max questions")
    ap.add_argument("--raw", default="data/raw/livebench")
    ap.add_argument("--runs", default="runs")
    args = ap.parse_args(argv)

    df = load_reasoning(args.raw)
    df = df[df["task"] == args.task].reset_index(drop=True)
    if args.limit:
        keep = sorted(df["question_id"].unique())[: args.limit]
        df = df[df["question_id"].isin(keep)].reset_index(drop=True)
    df["strict"] = score_rows(df, "strict")
    df["lenient"] = score_rows(df, "lenient")
    df["cls"] = [classify(a, g, t) for a, g, t in zip(df["answer"], df["ground_truth"], df["task"])]

    agree = agreement(df)
    bottom = bottom_quartile_items(df)
    sub = df[df["question_id"].isin(bottom)]
    overall = df["cls"].value_counts().reindex(CLASSES, fill_value=0)
    bottom_counts = sub["cls"].value_counts().reindex(CLASSES, fill_value=0)
    per_item = (
        sub.pivot_table(index="question_id", columns="cls", values="model", aggfunc="count")
        .reindex(columns=CLASSES, fill_value=0)
        .fillna(0)
        .astype(int)
    )
    per_item["ground_truth"] = df.drop_duplicates("question_id").set_index("question_id")[
        "ground_truth"
    ]

    run = RunDir.new(args.runs, "livebench_taxonomy")
    run.write_config({"task": args.task, "limit": args.limit, "raw": args.raw})
    for _, r in df.iterrows():
        run.append(
            {
                "id": f"{r.model}|{r.question_id}",
                "model": r.model,
                "question_id": r.question_id,
                "strict": r.strict,
                "lenient": r.lenient,
                "cls": r.cls,
            }
        )
    run.write_summary(
        {
            "task": args.task,
            "agreement": agree,
            "bottom_quartile_items": bottom,
            "taxonomy_all": overall.to_dict(),
            "taxonomy_bottom_quartile": bottom_counts.to_dict(),
            "taxonomy_per_bottom_item": per_item.reset_index().to_dict("records"),
        }
    )
    print(f"run: {run.path}  task={args.task} rows={len(df)} bottom_quartile_items={len(bottom)}")
    print("\n## strict vs lenient agreement\n")
    print(pd.Series(agree).to_frame("value").to_markdown(floatfmt=".3f"))
    print("\n## taxonomy counts (all rows | bottom-quartile items)\n")
    print(pd.DataFrame({"all": overall, "bottom_quartile": bottom_counts}).to_markdown())
    print("\n## taxonomy per bottom-quartile item\n")
    print(per_item.to_markdown())


if __name__ == "__main__":
    main()
