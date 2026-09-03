"""Train a tabular Q-learner on gridworld levels and log held-out solve rate per checkpoint.

uv run python scripts/gridworld_train.py [--limit N] [--curriculum random|easy2hard|plr] [--steps-per-ckpt 20000] [--seed 0]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks.gridworld import (
    Easy2Hard,
    PLRLite,
    QAgent,
    RandomCurriculum,
    make_heldout,
    make_pool,
    train,
)

from magic import RunDir, to_markdown


def main(argv: list[str] | None = None) -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20, help="number of eval checkpoints")
    ap.add_argument("--steps-per-ckpt", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--curriculum", choices=["random", "easy2hard", "plr"], default="random")
    ap.add_argument("--runs", default="runs")
    args = ap.parse_args(argv)

    t0 = time.time()
    pool, heldout = make_pool(), make_heldout()
    agent = QAgent(seed=args.seed, eps_decay_steps=args.limit * args.steps_per_ckpt // 2)
    budget = args.limit * args.steps_per_ckpt
    curriculum = {
        "random": lambda: RandomCurriculum(pool, seed=args.seed),
        "easy2hard": lambda: Easy2Hard(pool, total_steps=budget, seed=args.seed),
        "plr": lambda: PLRLite(pool, seed=args.seed),
    }[args.curriculum]()
    run = RunDir.new(args.runs, name=f"gridworld_{args.curriculum}")
    run.write_config(
        {
            "curriculum": args.curriculum,
            "seed": args.seed,
            "n_ckpts": args.limit,
            "steps_per_ckpt": args.steps_per_ckpt,
            "pool_size": len(pool),
            "heldout_ids": [lvl.id for lvl in heldout],
            "heldout_path_len": [lvl.path_len for lvl in heldout],
        }
    )
    rows = train(curriculum, heldout, agent, args.steps_per_ckpt, args.limit)
    for row in rows:
        run.append(row)
    df = pd.DataFrame(rows)[["steps", "solve_rate"]].set_index("steps")
    run.write_summary(
        {
            "curriculum": args.curriculum,
            "seed": args.seed,
            "final_solve_rate": rows[-1]["solve_rate"],
            "seconds": round(time.time() - t0, 1),
        }
    )
    print(to_markdown(df))
    print(f"run: {run.path}  ({time.time() - t0:.1f}s)")
    return run.path


if __name__ == "__main__":
    main()
