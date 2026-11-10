"""sqlite3 access (roadmap 2.5). Standard library only; WAL mode; schema in schema.sql."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(path: str = "data/app.db") -> sqlite3.Connection:
    """Open the database, enable WAL and foreign keys, apply schema.sql if needed."""
    raise NotImplementedError("roadmap 2.5")
