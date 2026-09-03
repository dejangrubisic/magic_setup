"""One directory per run: append-only samples plus config/summary sidecars."""

from __future__ import annotations

import json
import platform
import secrets
import subprocess
from datetime import datetime
from pathlib import Path

from magic.io import ensure_dir, iter_jsonl, read_jsonl, write_jsonl


def _git_sha() -> str | None:
    """Short HEAD sha, or None outside a git checkout / without git."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except Exception:
        return None
    return out.stdout.strip() or None


class RunDir:
    """A run directory; summary.json is written last and marks the run complete."""

    def __init__(self, path: str | Path) -> None:
        self._path = ensure_dir(path)

    @classmethod
    def new(cls, root: str | Path = "runs", name: str = "run") -> RunDir:
        """Create runs/<name>__<YYYYMMDD-HHMMSS>__<6 hex>; the suffix keeps parallel runs apart."""
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return cls(Path(root) / f"{name}__{stamp}__{secrets.token_hex(3)}")

    @property
    def path(self) -> Path:
        """The run directory."""
        return self._path

    @property
    def samples_path(self) -> Path:
        """The append-only samples.jsonl path."""
        return self._path / "samples.jsonl"

    def write_config(self, config: dict) -> Path:
        """Write config.json, stamped with the git sha (if any) and the python version."""
        payload = {**config, "git_sha": _git_sha(), "python": platform.python_version()}
        p = self._path / "config.json"
        p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return p

    def config(self) -> dict | None:
        """Read config.json, or None if the run was never configured."""
        p = self._path / "config.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def append(self, sample: dict) -> None:
        """Append one sample line; requires an 'id' so resume can skip it."""
        if "id" not in sample:
            raise ValueError("sample must include an 'id' key")
        write_jsonl(self.samples_path, [sample], append=True)

    def done_ids(self) -> set:
        """Ids already written; skip these to resume after a kill."""
        p = self.samples_path
        return {row["id"] for row in iter_jsonl(p)} if p.exists() else set()

    def samples(self) -> list[dict]:
        """All sample rows written so far."""
        p = self.samples_path
        return read_jsonl(p) if p.exists() else []

    def write_summary(self, summary: dict) -> Path:
        """Write summary.json last: its presence means the run finished."""
        p = self._path / "summary.json"
        p.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        return p

    def summary(self) -> dict | None:
        """Read summary.json, or None if the run is unfinished."""
        p = self._path / "summary.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def __repr__(self) -> str:
        return f"RunDir({str(self._path)!r})"
