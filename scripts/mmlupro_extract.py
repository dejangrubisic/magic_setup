"""Stage 2: re-score CoT text with strict/lenient extractors; per-model and per-category tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tasks.mmlupro import load_model_outputs, load_questions  # noqa: E402
from tasks.mmlupro_extract import (  # noqa: E402
    category_accuracy,
    extract_lenient,
    extract_strict,
    score_extractors,
)

from magic import RunDir, to_markdown  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data/raw/mmlupro"))
    ap.add_argument("--limit", type=int, default=None, help="keep the first N question ids")
    ap.add_argument("--runs", default=str(ROOT / "runs"))
    args = ap.parse_args()

    questions = load_questions(Path(args.data) / "questions.parquet")
    keep = questions["question_id"].head(args.limit) if args.limit else questions["question_id"]
    outputs = load_model_outputs(args.data, questions)
    outputs = outputs[outputs["question_id"].isin(set(keep))]

    run = RunDir.new(args.runs, "mmlupro_extract")
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
                "answer": r.answer,
                "pred": r.pred,
                "strict": extract_strict(r.cot),
                "lenient": extract_lenient(r.cot),
                "score": float(r.correct),
            }
        )
    ext = score_extractors(outputs)
    cat = category_accuracy(outputs)
    run.write_summary(
        {"extractors": ext.to_dict("records"), "category_accuracy": cat.to_dict("records")}
    )
    print(f"run: {run.path}")
    print("\n## Extractor agreement per model\n")
    print(to_markdown(ext.set_index("model")))
    print("\n## Accuracy (pred) per category x model, with Wilson 95% CI\n")
    wide = cat.assign(
        cell=lambda d: d.apply(lambda r: f"{r.acc:.3f} [{r.lo:.3f}, {r.hi:.3f}]", axis=1)
    )
    wide = wide.pivot(index="category", columns="model", values="cell")
    wide.insert(0, "n", cat.groupby("category")["n"].max())
    print(wide.to_markdown())


if __name__ == "__main__":
    main()
