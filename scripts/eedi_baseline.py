"""TF-IDF baseline for Eedi misconception retrieval: MAP@25 with a bootstrap CI on the test split.

uv run python -m scripts.eedi_baseline [--limit N] [--k 25] [--no-construct] [--test-pct 20]
"""

from __future__ import annotations

import argparse
import time

import pandas as pd
from tasks.eedi import TfidfRanker, add_split, ap_at_k, load_raw, query_text, reshape

from magic import RunDir, bootstrap_ci, to_markdown


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--limit", type=int, default=None, help="max test rows (default: all)")
    p.add_argument("--k", type=int, default=25)
    p.add_argument("--test-pct", type=int, default=20)
    p.add_argument("--no-construct", action="store_true", help="query = question + answer only")
    p.add_argument("--raw", default="data/raw/eedi")
    p.add_argument("--runs", default="runs")
    p.add_argument("--name", default="eedi_baseline")
    args = p.parse_args()
    use_construct = not args.no_construct

    t0 = time.time()
    train, misc = load_raw(args.raw)
    rows = add_split(reshape(train), test_pct=args.test_pct)
    names = misc.set_index("MisconceptionId")["MisconceptionName"]
    tr, te = rows[rows.split == "train"], rows[rows.split == "test"]
    if args.limit is not None:
        te = te.head(args.limit)

    ranker = TfidfRanker().fit(names, extra_texts=list(query_text(tr, use_construct)))
    top = ranker.rank(list(query_text(te, use_construct)), k=args.k)

    run = RunDir.new(args.runs, args.name)
    run.write_config({**vars(args), "n_train": len(tr), "n_test": len(te), "n_misc": len(names)})
    aps = []
    for r, ids in zip(te.itertuples(index=False), top):
        ap = ap_at_k(ids, r.MisconceptionId)
        aps.append(ap)
        run.append(
            {
                "id": f"{r.QuestionId}{r.letter}",
                "QuestionId": r.QuestionId,
                "letter": r.letter,
                "SubjectName": r.SubjectName,
                "ConstructName": r.ConstructName,
                "true_id": r.MisconceptionId,
                "top25": [int(x) for x in ids],
                "ap": ap,
            }
        )
    point, lo, hi = bootstrap_ci(aps)
    summary = {
        f"map{args.k}": point,
        "lo": lo,
        "hi": hi,
        "n": len(aps),
        "seconds": round(time.time() - t0, 1),
    }
    run.write_summary(summary)
    table = pd.DataFrame(
        [{"run": run.path.name, "n": len(aps), f"map{args.k}": point, "lo": lo, "hi": hi}]
    )
    print(to_markdown(table.set_index("run")))


if __name__ == "__main__":
    main()
