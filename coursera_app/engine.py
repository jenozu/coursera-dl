"""dl_coursera adapter: crawl + gather + classify (roadmap 2.1, 4.4, 4.5).

Only this module may import ``dl_coursera_run``. Replaces ``download_engine.py``
(kept until M7). Do NOT call the engine's ``download()``: it reads a hidden
failed-list file that overrides the selection (audit C-1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    url: str
    path: str  # absolute, already sanitized, inside the course directory
    kind: str  # video | subtitle | pdf | reading | notebook | other


def crawl_and_gather(
    *, cookies: Sequence[dict], slug: str, output_dir: str, refresh: bool = False
) -> list[Task]:
    """Validate slug, write 0600 cookie file, crawl, gather, delete cookie file in finally."""
    raise NotImplementedError("roadmap 2.1 / 4.4")


def classify(filename: str) -> str:
    """Map a filename to a content kind using an explicit, documented extension table."""
    raise NotImplementedError("roadmap 4.5")


def select(tasks: Sequence[Task], types: Sequence[str]) -> list[Task]:
    raise NotImplementedError("roadmap 4.5")
