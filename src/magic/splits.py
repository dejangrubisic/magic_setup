"""Content-hash splits and seeding."""

from __future__ import annotations

import random
import zlib

import numpy as np


def stable_split(uid: str, test_pct: int = 20, salt: str = "v1") -> str:
    """Assign a uid to "train"/"test" by hash, so other rows appearing never move it."""
    bucket = zlib.crc32(f"{salt}:{uid}".encode()) % 100
    return "test" if bucket < test_pct else "train"


def seed_everything(seed: int) -> None:
    """Seed random and numpy (and torch if installed); does not touch cuDNN determinism."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
