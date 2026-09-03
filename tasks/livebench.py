"""LiveBench reasoning: join raw answers with ground truth and score them with our own extractors.

The public `model_judgment` table has no reasoning rows, so scores are re-derived here from
`model_answer` + `reasoning.ground_truth` following the LiveBench answer formats:
spatial -> **<int>**, web_of_lies_v2 -> **yes, no, yes**, zebra_puzzle -> ***answer*** (the questions
in the public answer table are the single-answer, triple-bold generation of the task).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

TASKS = ("spatial", "web_of_lies_v2", "zebra_puzzle")
MODES = ("strict", "lenient")

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_TRIPLE_BOLD = re.compile(r"\*\*\*(.+?)\*\*\*", re.DOTALL)
_INT = re.compile(r"-?\d+")
_YESNO_LIST = re.compile(r"\b(yes|no)\b(?:\s*,\s*\b(yes|no)\b)+", re.IGNORECASE)  # >= 2 items


def _first_turn(choices) -> str:
    """The answer text of the first turn of the first choice (LiveBench answers are single-turn)."""
    try:
        return str(choices[0]["turns"][0])
    except (IndexError, KeyError, TypeError):
        return ""


def load_reasoning(raw_dir: str | Path, answers: pd.DataFrame | None = None, questions=None):
    """One row per (model, question) for the reasoning category, joined with ground truth.

    `answers`/`questions` override the parquet files (used by tests with jsonl fixtures).
    Questions without ground truth are dropped; duplicate (model, question) rows keep the latest
    `tstamp` (the raw table has 45 such duplicates with identical text).
    """
    raw = Path(raw_dir)
    if answers is None:
        answers = pd.read_parquet(raw / "model_answer.parquet")
    if questions is None:
        questions = pd.read_parquet(raw / "reasoning.parquet")
    ans = answers[answers["category"] == "reasoning"].copy()
    ans["answer"] = ans["choices"].map(_first_turn)
    if "tstamp" in ans.columns:
        ans = ans.sort_values("tstamp", kind="stable")
    ans = ans.rename(columns={"model_id": "model"}).drop_duplicates(
        ["model", "question_id"], keep="last"
    )[["question_id", "task", "model", "answer"]]
    gt = questions[["question_id", "ground_truth"]].dropna(subset=["ground_truth"])
    return ans.merge(gt, on="question_id", how="inner").reset_index(drop=True)


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().replace("*", "").split())


def _norm_list(s: str) -> list[str]:
    return [_norm(x) for x in s.split(",")]


def extract_answer(text: str, task: str, mode: str = "strict") -> str | None:
    """Extract the final answer string from a model response, or None if no answer is found.

    strict: the task's required format, last occurrence. lenient: strict, then fall back to the
    last integer / yes-no list, the last bold span, and (zebra_puzzle only) the last non-empty line.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if task not in TASKS:
        raise ValueError(f"task must be one of {TASKS}, got {task!r}")
    text = text or ""
    bolds = _BOLD.findall(text)
    triples = _TRIPLE_BOLD.findall(text)
    if task == "zebra_puzzle":
        strict = triples[-1].strip() if triples else None
    elif task == "spatial":
        strict = next((b for b in reversed(bolds) if _INT.fullmatch(b.strip())), None)
    else:  # web_of_lies_v2
        strict = next((b for b in reversed(bolds) if _YESNO_LIST.fullmatch(b.strip())), None)
    if strict is not None or mode == "strict":
        return strict
    if task == "spatial":
        ints = _INT.findall(text)
        if ints:
            return ints[-1]
    if task == "web_of_lies_v2":
        hits = [m.group(0) for m in _YESNO_LIST.finditer(text)]
        if hits:
            return hits[-1]
    if bolds:
        return bolds[-1].strip()
    if task != "zebra_puzzle":  # integer / yes-no answers cannot hide in prose
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else None


def score_answer(text: str, ground_truth: str, task: str, mode: str = "strict") -> float:
    """Score in [0, 1]; exact match except zebra_puzzle, which gets the fraction of fields right."""
    pred = extract_answer(text, task, mode)
    if pred is None:
        return 0.0
    if task == "zebra_puzzle":
        p, g = _norm_list(pred), _norm_list(ground_truth)
        if len(p) != len(g):
            return 0.0
        return sum(a == b for a, b in zip(p, g)) / len(g)
    if task == "web_of_lies_v2":
        return float(_norm_list(pred) == _norm_list(ground_truth))
    return float(_norm(pred) == _norm(ground_truth))


def score_rows(df: pd.DataFrame, mode: str = "strict") -> pd.Series:
    """Per-row score for a frame from `load_reasoning`."""
    return pd.Series(
        [
            score_answer(a, g, t, mode)
            for a, g, t in zip(df["answer"], df["ground_truth"], df["task"])
        ],
        index=df.index,
        dtype=float,
    )


def score_matrix(df: pd.DataFrame, mode: str = "strict") -> pd.DataFrame:
    """Models (rows) x question_id (cols) score matrix; NaN where a model has no answer."""
    scored = df.assign(score=score_rows(df, mode))
    return scored.pivot_table(index="model", columns="question_id", values="score", aggfunc="mean")
