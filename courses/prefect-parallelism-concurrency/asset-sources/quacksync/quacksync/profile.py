"""Tiny per-stage timing helper used in Module 1."""
from __future__ import annotations

import time
from contextlib import contextmanager

_stage_times: dict[str, float] = {}


@contextmanager
def stage(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        _stage_times[name] = _stage_times.get(name, 0.0) + (time.perf_counter() - start)


def report() -> dict[str, float]:
    return dict(_stage_times)


def reset() -> None:
    _stage_times.clear()
