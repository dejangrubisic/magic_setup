"""Stage 1: load MMLU-Pro outputs, write per-item correctness samples, print per-model accuracy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tasks.mmlupro import load_model_outputs, load_questions, model_accuracy  # noqa: E402

from magic import RunDir, to_markdown  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data/raw/mmlupro"))
    ap.add_argument("--limit", type=int, default=None, help="keep the first N question ids")
    ap.add_argument("--runs", default=str(ROOT / "runs"))
    args = ap.parse_args()

    questions = load_questions(Path(args.data) / "questions.parquet")
    outputs = load_model_outputs(args.data, questions)
    rekeyed = outputs.groupby("model")["rekeyed"].mean()
    for model, share in rekeyed[rekeyed > 0].items():
        print(
            f"note: {model}: ids did not match HF; re-keyed by question text ({share:.0%} of rows)"
        )
    if args.limit:
        keep = set(questions["question_id"].head(args.limit))
        outputs = outputs[outputs["question_id"].isin(keep)]
    outputs = outputs[outputs["question_id"].isin(set(questions["question_id"]))]

    run = RunDir.new(args.runs, "mmlupro_baseline")
    run.write_config(
        {"data": args.data, "limit": args.limit, "models": sorted(outputs["model"].unique())}
    )
    for r in outputs.itertuples(index=False):
        run.append(
            {
                "id": f"{r.model}:{r.question_id}",
                "model": r.model,
                "question_id": int(r.question_id),
                "category": r.category,
                "pred": r.pred,
                "answer": r.answer,
                "score": float(r.correct),
            }
        )
    acc = model_accuracy(outputs)
    run.write_summary(
        {"n_questions": int(outputs["question_id"].nunique()), "accuracy": acc.to_dict("records")}
    )
    print(f"run: {run.path}")
    print(to_markdown(acc.set_index("model")))


if __name__ == "__main__":
    main()
