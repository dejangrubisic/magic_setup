"""Confusion analysis for a finished baseline run: which misconceptions outrank the true one.

    uv run python -m scripts.eedi_confusion --run runs/eedi_baseline__<id> [--limit 15]
Writes <run>/confusion.md and <run>/map_by_subject.png.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd

from magic import RunDir, bootstrap_ci, to_markdown
from magic.plots import bar_with_ci


def confused_pairs(samples: list[dict]) -> Counter:
    """Count (true_id, distractor_id) for every distractor ranked strictly above the true id."""
    pairs: Counter = Counter()
    for s in samples:
        top = list(s["top25"])
        cut = top.index(s["true_id"]) if s["true_id"] in top else len(top)
        pairs.update((s["true_id"], d) for d in top[:cut])
    return pairs


def distractor_counts(samples: list[dict]) -> Counter:
    """How often each misconception id is ranked above the true id, over all rows."""
    counts: Counter = Counter()
    for (_true, d), n in confused_pairs(samples).items():
        counts[d] += n
    return counts


def subject_ci(samples: pd.DataFrame, n_subjects: int) -> pd.DataFrame:
    """MAP@25 + CI for the n largest subjects."""
    rows = []
    for subj, g in samples.groupby("SubjectName"):
        point, lo, hi = bootstrap_ci(g.ap)
        rows.append({"SubjectName": subj, "n": len(g), "map25": point, "lo": lo, "hi": hi})
    return pd.DataFrame(rows).sort_values("n", ascending=False).head(n_subjects)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True)
    p.add_argument("--limit", type=int, default=15, help="rows per table")
    p.add_argument("--raw", default="data/raw/eedi")
    p.add_argument("--n-subjects", type=int, default=12)
    args = p.parse_args()

    run = RunDir(args.run)
    samples = run.samples()
    names = pd.read_csv(Path(args.raw, "misconception_mapping.csv")).set_index("MisconceptionId")[
        "MisconceptionName"
    ]

    pairs = pd.DataFrame(
        [
            {"true": names[t], "confused_with": names[d], "count": n}
            for (t, d), n in confused_pairs(samples).most_common(args.limit)
        ]
    ).set_index("true")
    distractors = pd.DataFrame(
        [
            {"misconception": names[d], "times_above_true": n}
            for d, n in distractor_counts(samples).most_common(args.limit)
        ]
    ).set_index("misconception")
    text = (
        f"## Top confused pairs (distractor ranked above the true misconception)\n\n{to_markdown(pairs)}\n\n"
        f"## Most frequent distractors\n\n{to_markdown(distractors)}\n"
    )
    print(text)
    Path(args.run, "confusion.md").write_text(text, encoding="utf-8")

    subj = subject_ci(pd.DataFrame(samples), args.n_subjects)
    labels = [s[:28] for s in subj.SubjectName]
    bar_with_ci(
        labels,
        subj.map25,
        subj.lo,
        subj.hi,
        title="TF-IDF MAP@25 by subject (largest subjects, 95% bootstrap CI)",
        path=Path(args.run, "map_by_subject.png"),
    )
    print(f"wrote {Path(args.run, 'map_by_subject.png')}")


if __name__ == "__main__":
    main()
