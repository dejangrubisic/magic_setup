"""Residual analysis for a predict run: error by rating-quantile bin and the worst test items."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.easy2hard import residual_table, worst_examples

from magic import RunDir, read_jsonl, to_markdown


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True, help="a runs/easy2hard_predict__* directory")
    ap.add_argument("--model", default="ridge_hand_tfidf")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--bins", type=int, default=5)
    args = ap.parse_args()

    run = RunDir(args.run)
    samples = pd.DataFrame(run.samples())
    samples = samples[samples.model == args.model]
    if samples.empty:
        sys.exit(f"no samples for model {args.model!r} in {run.path}")
    questions = {r["id"]: r["question"] for r in read_jsonl(run.config()["data"])}

    print(f"## residuals by rating quantile bin ({args.model})")
    print(to_markdown(residual_table(samples, n_bins=args.bins)))
    worst = worst_examples(samples, k=args.k)
    worst = worst.assign(question=[questions[i][:120] for i in worst.item_id])
    print(f"\n## {args.k} worst test items ({args.model})")
    print(to_markdown(worst[["item_id", "y_true", "y_pred", "rating_quantile", "question"]]))


if __name__ == "__main__":
    main()
