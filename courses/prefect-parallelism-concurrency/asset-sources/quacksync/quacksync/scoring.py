"""CPU-bound duck scoring.

This module intentionally does *real* numerical work so that the difference
between `ThreadPoolTaskRunner` and `ProcessPoolTaskRunner` is observable.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

REFERENCE_VECTORS = np.random.RandomState(42).rand(256, 64).astype(np.float64)


def _duck_vector(duck: dict) -> np.ndarray:
    """Turn a duck record into a 64-dimensional feature vector."""
    rng = np.random.RandomState(int(duck["id"]))
    base = rng.rand(64)
    base[0] = (duck.get("price_cents", 0) or 0) / 5000.0
    base[1] = (duck.get("stock", 0) or 0) / 200.0
    base[2] = (duck.get("rating", 0) or 0) / 5.0
    return base


@dataclass
class ScorerConfig:
    """Scoring configuration. Kept simple and picklable."""

    iterations: int = 200
    ref_count: int = 256


def score_record(duck: dict, config: ScorerConfig | None = None) -> float:
    """Compute a cosine-similarity-based score against the reference set."""
    config = config or ScorerConfig()
    vec = _duck_vector(duck)
    refs = REFERENCE_VECTORS[: config.ref_count]

    best = 0.0
    for _ in range(config.iterations):
        sims = refs @ vec / (np.linalg.norm(refs, axis=1) * np.linalg.norm(vec) + 1e-9)
        best = float(np.max(sims))
    return best
