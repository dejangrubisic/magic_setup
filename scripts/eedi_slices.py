"""MAP@25 by SubjectName and ConstructName (with bootstrap CIs) from a finished baseline run.

uv run python -m scripts.eedi_slices --run runs/eedi_baseline__<id> [--limit N]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from magic import RunDir, bootstrap_ci, to_markdown


def slice_table(samples: pd.DataFrame, col: str, n_boot: int = 2000) -> pd.DataFrame:
    """Rows: each value of `col` plus ALL; columns: n, map25, lo, hi (percentile bootstrap)."""
    groups = [(k, g.ap) for k, g in samples.groupby(col, sort=True)] + [("ALL", samples.ap)]
    rows = []
    for key, aps in groups:
        point, lo, hi = bootstrap_ci(aps, n_boot=n_boot)
        rows.append({col: key, "n": len(aps), "map25": point, "lo": lo, "hi": hi})
    return pd.DataFrame(rows).set_index(col)


def hardest(
    samples: pd.DataFrame, col: str, min_n: int = 3, top: int = 10, n_boot: int = 2000
) -> pd.DataFrame:
    """Lowest-MAP slices with at least min_n rows, ascending, at most `top` rows."""
    t = slice_table(samples, col, n_boot=n_boot).drop(index="ALL")
    return t[t.n >= min_n].sort_values(["map25", "n"], ascending=[True, False]).head(top)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, help="finished runs/eedi_baseline__* directory")
    p.add_argument("--limit", type=int, default=None, help="max rows per printed table")
    p.add_argument("--min-n", type=int, default=3)
    args = p.parse_args()

    samples = pd.DataFrame(RunDir(args.run).samples())
    sections = [
        (
            "MAP@25 by SubjectName",
            slice_table(samples, "SubjectName").sort_values("n", ascending=False),
        ),
        (
            "MAP@25 by ConstructName",
            slice_table(samples, "ConstructName").sort_values("n", ascending=False),
        ),
        (f"Hardest constructs (n >= {args.min_n})", hardest(samples, "ConstructName", args.min_n)),
    ]
    out = []
    for title, table in sections:
        shown = table.head(args.limit) if args.limit else table
        out.append(f"## {title}\n\n{to_markdown(shown)}\n")
    text = "\n".join(out)
    print(text)
    Path(args.run, "slices.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
