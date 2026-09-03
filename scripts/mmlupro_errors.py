"""Stage 3: distractor distribution per category, all-fail items, label-error suspect sample."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
from tasks.mmlupro import load_model_outputs, load_questions  # noqa: E402
from tasks.mmlupro_errors import (  # noqa: E402
    all_fail_items,
    distractor_distribution,
    label_error_flags,
)

from magic import RunDir, to_markdown  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data/raw/mmlupro"))
    ap.add_argument("--limit", type=int, default=None, help="keep the first N question ids")
    ap.add_argument("--sample", type=int, default=20, help="number of all-fail items to inspect")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--runs", default=str(ROOT / "runs"))
    args = ap.parse_args()

    questions = load_questions(Path(args.data) / "questions.parquet")
    outputs = load_model_outputs(args.data, questions)  # re-keying needs the full question table
    if args.limit:
        questions = questions.head(args.limit)
    outputs = outputs[outputs["question_id"].isin(set(questions["question_id"]))]

    dist = distractor_distribution(outputs)
    fails = all_fail_items(outputs, questions)
    sample = fails.sample(min(args.sample, len(fails)), random_state=args.seed).sort_values(
        "question_id"
    )
    flags = pd.DataFrame([label_error_flags(r) for _, r in sample.iterrows()], index=sample.index)
    sample = pd.concat([sample, flags], axis=1)

    run = RunDir.new(args.runs, "mmlupro_errors")
    run.write_config(
        {"data": args.data, "limit": args.limit, "sample": args.sample, "seed": args.seed}
    )
    for r in sample.to_dict("records"):
        run.append(
            {"id": int(r["question_id"]), **{k: v for k, v in r.items() if k != "question_id"}}
        )
    all_flags = pd.DataFrame([label_error_flags(r) for _, r in fails.iterrows()])
    run.write_summary(
        {
            "n_questions": len(questions),
            "n_all_fail": len(fails),
            "all_fail_by_category": fails["category"].value_counts().to_dict(),
            "sample_flag_counts": flags.sum().to_dict(),
            "all_fail_flag_counts": all_flags.sum().to_dict() if len(all_flags) else {},
            "distractor_distribution": dist.reset_index().to_dict("records"),
        }
    )
    print(f"run: {run.path}")
    print(f"\nall-fail items: {len(fails)} / {len(questions)} questions\n")
    print(
        to_markdown(
            pd.DataFrame(
                {
                    "all_fail": fails["category"].value_counts(),
                    "n": questions["category"].value_counts(),
                }
            ).assign(share=lambda d: d["all_fail"] / d["n"])
        )
    )
    print("\n## Distribution of wrong preds per category (share of wrong rows)\n")
    print(to_markdown(dist))
    print(f"\n## Sampled all-fail items (n={len(sample)}) with label-error flags\n")
    show = sample.assign(
        options=lambda d: d["options"].map(
            lambda o: " | ".join(f"{L}:{str(x)[:25]}" for L, x in zip("ABCDEFGHIJ", o))
        )
    )
    print(show.drop(columns=["answer_index"]).to_markdown(index=False))
    print("\nflag counts in sample:", flags.sum().to_dict())
    print("flag counts over all all-fail items:", all_flags.sum().to_dict())


if __name__ == "__main__":
    main()
