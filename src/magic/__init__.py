"""Public API; magic.plots is not re-exported so importing magic stays free of matplotlib."""

from magic.io import ensure_dir, iter_jsonl, read_jsonl, write_jsonl
from magic.llm import complete, complete_many
from magic.results import by_slice, ci_by_group, load_runs, to_markdown
from magic.runs import RunDir
from magic.splits import seed_everything, stable_split
from magic.stats import bootstrap_ci, paired_bootstrap_diff, wilson_interval

__all__ = [
    "RunDir",
    "bootstrap_ci",
    "by_slice",
    "ci_by_group",
    "complete",
    "complete_many",
    "ensure_dir",
    "iter_jsonl",
    "load_runs",
    "paired_bootstrap_diff",
    "read_jsonl",
    "seed_everything",
    "stable_split",
    "to_markdown",
    "wilson_interval",
    "write_jsonl",
]
