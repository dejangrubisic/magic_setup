"""Download E2H-GSM8K from the HF hub into data/raw/easy2hard/gsm8k.jsonl."""

from __future__ import annotations

import argparse
from pathlib import Path

from datasets import load_dataset

from magic import write_jsonl

KEEP = ["question", "answer", "rating", "rating_std", "rating_quantile", "model_avg_acc"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/raw/easy2hard/gsm8k.jsonl")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    ds = load_dataset("furonghuang-lab/Easy2Hard-Bench", "E2H-GSM8K")["eval"]
    if args.limit is not None:
        ds = ds.select(range(min(args.limit, len(ds))))
    rows = ({"id": f"gsm8k-{i}", **{k: r[k] for k in KEEP}} for i, r in enumerate(ds))
    path = write_jsonl(Path(args.out), rows)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
