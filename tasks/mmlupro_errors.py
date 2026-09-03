"""Error clustering for MMLU-Pro: distractor distribution, all-fail items, label-error heuristics."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from tasks.mmlupro import LETTERS

ALL_FAIL_COLS = [
    "question_id",
    "category",
    "answer",
    "answer_index",
    "options",
    "n_models",
    "consensus_pred",
    "consensus_share",
]


def distractor_distribution(outputs: pd.DataFrame) -> pd.DataFrame:
    """Per category over wrong rows: n_wrong, share with no pred, share adjacent to the answer, share per letter."""
    wrong = outputs[~outputs["correct"]]
    rows = []
    for cat, g in wrong.groupby("category", sort=True):
        pred_idx = g["pred"].map(
            lambda p: LETTERS.index(p) if isinstance(p, str) and p in LETTERS else None
        )
        adjacent = (pred_idx - g["answer_index"]).abs() == 1
        counts = g["pred"].value_counts()
        row = {
            "category": cat,
            "n_wrong": len(g),
            "share_pred_none": float(g["pred"].isna().mean()),
            "share_adjacent": float(adjacent.fillna(False).mean()),
        }
        row.update({letter: float(counts.get(letter, 0) / len(g)) for letter in LETTERS})
        rows.append(row)
    cols = ["category", "n_wrong", "share_pred_none", "share_adjacent", *LETTERS]
    return pd.DataFrame(rows, columns=cols).set_index("category")


def all_fail_items(outputs: pd.DataFrame, questions: pd.DataFrame) -> pd.DataFrame:
    """Questions where every model that answered is wrong, with the most common wrong pred and its share."""
    per_q = outputs.groupby("question_id")
    fail_ids = per_q["correct"].sum()[lambda s: s == 0].index
    rows = []
    for qid in fail_ids:
        g = outputs[outputs["question_id"] == qid]
        preds = Counter(p for p in g["pred"] if isinstance(p, str))
        top, n_top = preds.most_common(1)[0] if preds else (None, 0)
        rows.append(
            {
                "question_id": qid,
                "n_models": len(g),
                "consensus_pred": top,
                "consensus_share": n_top / len(g),
            }
        )
    fails = pd.DataFrame(
        rows, columns=["question_id", "n_models", "consensus_pred", "consensus_share"]
    )
    q = questions[["question_id", "category", "answer", "answer_index", "options"]]
    return (
        q.merge(fails, on="question_id")
        .sort_values("question_id")
        .reset_index(drop=True)[ALL_FAIL_COLS]
    )


def label_error_flags(row: pd.Series) -> dict[str, bool]:
    """Heuristic label-error signals for one all-fail row; `suspect` is any flag."""
    opts = [str(o).strip().lower() for o in row["options"]]
    answer_idx = int(row["answer_index"])
    answer_text = opts[answer_idx] if 0 <= answer_idx < len(opts) else None
    flags = {
        "dup_option": answer_text is not None and opts.count(answer_text) > 1,
        "consensus": bool(row["n_models"] >= 3 and row["consensus_share"] >= 0.8),
        "answer_index_mismatch": LETTERS[answer_idx] != row["answer"]
        if answer_idx < len(LETTERS)
        else True,
    }
    flags["suspect"] = any(flags.values())
    return flags
