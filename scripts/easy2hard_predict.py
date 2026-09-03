"""Fit difficulty predictors on the stable train split and report Spearman (+CI) on test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.easy2hard import build_models, feature_frame, spearman_ci

from magic import RunDir, read_jsonl, to_markdown


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data/raw/easy2hard/gsm8k.jsonl")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--runs", default="runs")
    args = ap.parse_args()

    rows = read_jsonl(args.data)
    if args.limit is not None:
        rows = rows[: args.limit]
    df = feature_frame(rows)
    train, test = df[df.split == "train"], df[df.split == "test"]

    run = RunDir.new(args.runs, "easy2hard_predict")
    run.write_config({**vars(args), "n_train": len(train), "n_test": len(test)})
    results = []
    for name, model in build_models(args.seed).items():
        model.fit(train, train.rating)
        pred = model.predict(test)
        for row_id, yt, yp, q in zip(test.id, test.rating, pred, test.rating_quantile):
            run.append(
                {
                    "id": f"{name}:{row_id}",
                    "item_id": row_id,
                    "model": name,
                    "y_true": float(yt),
                    "y_pred": float(yp),
                    "rating_quantile": float(q),
                }
            )
        rho, lo, hi = spearman_ci(test.rating, pred, seed=args.seed)
        results.append({"model": name, "spearman": rho, "lo": lo, "hi": hi, "n_test": len(test)})
    table = pd.DataFrame(results).set_index("model")
    run.write_summary({"results": results})
    print(f"run: {run.path}")
    print(to_markdown(table))


if __name__ == "__main__":
    main()
