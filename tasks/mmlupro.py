"""MMLU-Pro per-question model outputs: loading and the item x model correctness matrix."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pandas as pd

from magic import wilson_interval

LETTERS = "ABCDEFGHIJ"
QUESTION_COLS = ["question_id", "question", "options", "answer", "answer_index", "category"]


def _as_list(x) -> list:
    if isinstance(x, list):
        return x
    if hasattr(x, "tolist"):
        return list(x.tolist())
    return list(ast.literal_eval(x))


def load_questions(path: str | Path) -> pd.DataFrame:
    """HF MMLU-Pro question table from parquet or jsonl; typed ids and options as python lists."""
    p = Path(path)
    df = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_json(p, lines=True)
    df = df[QUESTION_COLS].copy()
    df["question_id"] = df["question_id"].astype(int)
    df["answer_index"] = df["answer_index"].astype(int)
    df["options"] = df["options"].map(_as_list)
    return df.sort_values("question_id").reset_index(drop=True)


def _text_key(question: str, options: list) -> str:
    return f"{question}||{options[0] if options else ''}"


def load_model_outputs(
    root: str | Path, questions: pd.DataFrame | None = None, min_id_agreement: float = 0.9
) -> pd.DataFrame:
    """All <root>/*/*.json rows (one file per model directory) as one tidy frame; CoT text lands in `cot`.

    With `questions`, a model whose `question_id`s agree with the HF ids on fewer than
    `min_id_agreement` of rows (matched on question text + first option) is re-keyed by text and
    rows without a text match are dropped; `rekeyed` marks those rows.
    """
    key_to_id = None
    if questions is not None:
        keys = [_text_key(q, o) for q, o in zip(questions["question"], questions["options"])]
        key_to_id = pd.Series(questions["question_id"].to_numpy(), index=keys)
        key_to_id = key_to_id[~key_to_id.index.duplicated(keep="first")]
    frames = []
    for f in sorted(Path(root).glob("*/*.json")):
        rows = json.loads(f.read_text(encoding="utf-8"))
        df = pd.DataFrame(rows)
        df["model"] = f.parent.name
        cot_key = "model_outputs" if "model_outputs" in df.columns else "generated_text"
        df["cot"] = df[cot_key].fillna("").astype(str)
        df["question_id"] = df["question_id"].astype(int)
        df["answer_index"] = df["answer_index"].astype(int)
        df["options"] = df["options"].map(_as_list)
        df["pred"] = df["pred"].astype(object).where(df["pred"].notna(), None)  # None, not NaN
        df["rekeyed"] = False
        if key_to_id is not None:
            text_ids = pd.Series(
                [_text_key(q, o) for q, o in zip(df["question"], df["options"])], index=df.index
            ).map(key_to_id)
            if (text_ids == df["question_id"]).mean() < min_id_agreement:
                df = df[text_ids.notna()].assign(
                    question_id=text_ids.dropna().astype(int), rekeyed=True
                )
        frames.append(
            df[
                [
                    "model",
                    "question_id",
                    "category",
                    "options",
                    "answer",
                    "answer_index",
                    "pred",
                    "cot",
                    "rekeyed",
                ]
            ]
        )
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(["model", "question_id"], keep="first")
    out["correct"] = out["pred"] == out["answer"]
    return out.sort_values(["model", "question_id"]).reset_index(drop=True)


def correctness_matrix(outputs: pd.DataFrame) -> pd.DataFrame:
    """question_id x model; True/False, NaN where the model has no row."""
    return outputs.pivot(index="question_id", columns="model", values="correct").astype(object)


def model_accuracy(outputs: pd.DataFrame) -> pd.DataFrame:
    """Per-model accuracy with a Wilson 95% interval: columns model, n, acc, lo, hi."""
    rows = []
    for model, g in outputs.groupby("model", sort=True):
        acc, lo, hi = wilson_interval(int(g["correct"].sum()), len(g))
        rows.append({"model": model, "n": len(g), "acc": acc, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)
