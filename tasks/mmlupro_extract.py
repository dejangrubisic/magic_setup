"""Own answer extraction over MMLU-Pro CoT text: strict vs lenient, and per-category accuracy."""

from __future__ import annotations

import re

import pandas as pd

from magic import wilson_interval

STRICT_RE = re.compile(r"answer(?:\s+is|:)\s*\(?([A-Ja-j])\)?(?![A-Za-z])", re.IGNORECASE)
LENIENT_RE = re.compile(r"(?<![A-Za-z])\(?([A-J])\)?(?![A-Za-z])")


def extract_strict(text: str, last: bool = False) -> str | None:
    """First `answer is (X)` / `answer is X` / `Answer: (X)` in the text, X in A-J; None if absent.

    First match mirrors the official MMLU-Pro scorer; `last=True` takes the last match instead,
    which exposes models that keep generating new questions after answering.
    """
    hits = STRICT_RE.findall(text or "")
    if not hits:
        return None
    return (hits[-1] if last else hits[0]).upper()


def extract_lenient(text: str) -> str | None:
    """Last standalone capital letter A-J (optionally parenthesised); None if there is none."""
    hits = LENIENT_RE.findall(text or "")
    return hits[-1] if hits else None


def score_extractors(outputs: pd.DataFrame) -> pd.DataFrame:
    """Per-model accuracy under pred / strict / lenient, agreement with pred, format-failure and runaway rates."""
    df = outputs[["model", "answer", "pred", "cot"]].copy()
    df["strict"] = df["cot"].map(extract_strict)
    df["strict_last"] = df["cot"].map(lambda t: extract_strict(t, last=True))
    df["lenient"] = df["cot"].map(extract_lenient)
    rows = []
    for model, g in df.groupby("model", sort=True):
        rows.append(
            {
                "model": model,
                "n": len(g),
                "acc_pred": float((g["pred"] == g["answer"]).mean()),
                "acc_strict": float((g["strict"] == g["answer"]).mean()),
                "acc_lenient": float((g["lenient"] == g["answer"]).mean()),
                "agree_strict_pred": float((g["strict"] == g["pred"]).mean()),
                "agree_lenient_pred": float((g["lenient"] == g["pred"]).mean()),
                "format_fail": float(g["strict"].isna().mean()),
                "runaway": float((g["strict"].notna() & (g["strict"] != g["strict_last"])).mean()),
            }
        )
    return pd.DataFrame(rows)


def category_accuracy(outputs: pd.DataFrame) -> pd.DataFrame:
    """Accuracy of `pred` per (category, model) with a Wilson 95% interval."""
    rows = []
    for (cat, model), g in outputs.groupby(["category", "model"], sort=True):
        acc, lo, hi = wilson_interval(int(g["correct"].sum()), len(g))
        rows.append({"category": cat, "model": model, "n": len(g), "acc": acc, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)
