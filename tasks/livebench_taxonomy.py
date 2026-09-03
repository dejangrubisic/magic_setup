"""Strict vs lenient parser agreement and a failure taxonomy for LiveBench reasoning answers."""

from __future__ import annotations

import pandas as pd

from tasks.livebench import extract_answer, score_answer

CLASSES = ("correct", "wrong_answer", "format_failure", "truncation", "no_answer")
_TERMINATORS = (".", "!", "?", "*", ">", "`")


def classify(text: str, ground_truth: str, task: str) -> str:
    """One of CLASSES for a single answer (see issue 03 for the rules)."""
    text = text or ""
    if score_answer(text, ground_truth, task, "strict") == 1.0:
        return "correct"
    strict = extract_answer(text, task, "strict")
    if strict is not None:
        return "wrong_answer"
    stripped = text.strip()
    if not stripped or not stripped.endswith(_TERMINATORS):
        return "truncation"
    if extract_answer(text, task, "lenient") is not None:
        return "format_failure"
    return "no_answer"


def agreement(df: pd.DataFrame) -> dict:
    """Strict/lenient agreement stats for a frame with `strict` and `lenient` score columns."""
    strict, lenient = df["strict"], df["lenient"]
    return {
        "n": len(df),
        "exact_agree": float((strict == lenient).mean()) if len(df) else float("nan"),
        "strict_mean": float(strict.mean()) if len(df) else float("nan"),
        "lenient_mean": float(lenient.mean()) if len(df) else float("nan"),
        "lenient_rescues": int(((strict == 0) & (lenient > 0)).sum()),
    }


def bottom_quartile_items(df: pd.DataFrame) -> list[str]:
    """question_ids whose strict mean score is at or below the 25th percentile of item means."""
    means = df.groupby("question_id")["strict"].mean()
    return sorted(means[means <= means.quantile(0.25)].index)
