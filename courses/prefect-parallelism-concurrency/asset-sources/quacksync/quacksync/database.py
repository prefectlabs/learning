"""A SQLite-backed DatabasePool that mimics a real connection pool.

It enforces a configurable maximum number of concurrent connections and raises
`ConnectionPoolExhausted` when a task tries to open one too many. This makes
the behavior learners see in Module 5 feel like a real PostgreSQL pool without
requiring a Postgres server.
"""
from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path


class ConnectionPoolExhausted(RuntimeError):
    """Raised when the pool is at capacity and a new connection is requested."""


class DatabasePool:
    def __init__(self, path: str | os.PathLike = "quacksync.db", max_connections: int = 5) -> None:
        self.path = str(path)
        self.max_connections = max_connections
        self._active = 0
        self._lock = threading.Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ducks (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    color TEXT,
                    size TEXT,
                    price_cents INTEGER,
                    stock INTEGER,
                    rating REAL,
                    reviews INTEGER,
                    score REAL
                )
                """
            )

    @contextmanager
    def connection(self):
        """Acquire a connection or raise `ConnectionPoolExhausted` immediately.

        This is intentionally non-blocking: we want the pool-exhausted error
        to surface loudly so learners see why concurrency limits matter.
        """
        with self._lock:
            if self._active >= self.max_connections:
                raise ConnectionPoolExhausted(
                    f"Pool exhausted: {self._active}/{self.max_connections} in use"
                )
            self._active += 1
        try:
            conn = sqlite3.connect(self.path, timeout=0.1)
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()
        finally:
            with self._lock:
                self._active -= 1

    def upsert_duck(self, record: dict) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO ducks (id, name, color, size, price_cents, stock, rating, reviews, score)
                VALUES (:id, :name, :color, :size, :price_cents, :stock, :rating, :reviews, :score)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    color=excluded.color,
                    size=excluded.size,
                    price_cents=excluded.price_cents,
                    stock=excluded.stock,
                    rating=excluded.rating,
                    reviews=excluded.reviews,
                    score=excluded.score
                """,
                record,
            )

    def count(self) -> int:
        with self.connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM ducks").fetchone()
            return int(row[0]) if row else 0


pool = DatabasePool()
