"""Own fetch loop (roadmap 1.1, 4.1, 4.3).

Requirements: (connect, read) timeouts; stream to ``<name>.part`` then ``os.replace``;
skip complete existing files; ``Range`` resume on 206; exponential backoff with jitter;
honour ``Retry-After`` on 429; no retry on 401/403/404; check a cancel Event between chunks.
Every item ends as done, skipped, failed(code) or cancelled.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ItemResult:
    path: str
    status: str  # done | skipped | failed | cancelled
    error_code: str | None = None
    bytes_done: int = 0


ProgressCb = Callable[[str, int, int | None], None]  # path, bytes_done, bytes_total


def download_one(
    url: str,
    path: str,
    *,
    cancel: threading.Event,
    on_progress: ProgressCb | None = None,
    timeout: tuple[float, float] = (10, 30),
    max_attempts: int = 4,
) -> ItemResult:
    raise NotImplementedError("roadmap 4.1")
