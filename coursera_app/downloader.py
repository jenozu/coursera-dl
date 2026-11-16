"""Own fetch loop (roadmap 1.1, 4.1, 4.3).

Requirements: (connect, read) timeouts; stream to ``<name>.part`` then ``os.replace``;
skip complete existing files; ``Range`` resume on 206; exponential backoff with jitter;
honour ``Retry-After`` on 429; no retry on 401/403/404; check a cancel Event between chunks.
Every item ends as done, skipped, failed(code) or cancelled.
"""

from __future__ import annotations

import os
import random
import threading
from collections.abc import Callable
from dataclasses import dataclass

import requests

_NO_RETRY = {401, 403, 404}
_CHUNK = 64 * 1024


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
    # ponytail: no Range resume yet (roadmap 4.1); a retry restarts the .part file.
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return ItemResult(path, "skipped")
    part = path + ".part"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    code = "error"
    for attempt in range(max_attempts):
        if cancel.is_set():
            return ItemResult(path, "cancelled")
        delay = min(2**attempt, 30) * (0.5 + random.random() / 2)  # noqa: S311
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                if r.status_code != 200:
                    code = f"http_{r.status_code}"
                    if r.status_code in _NO_RETRY:
                        return ItemResult(path, "failed", code)
                    if r.status_code == 429:
                        try:
                            delay = min(float(r.headers.get("Retry-After", delay)), 60)
                        except ValueError:
                            pass
                else:
                    total = int(r.headers.get("Content-Length") or 0) or None
                    done = 0
                    with open(part, "wb") as f:
                        for chunk in r.iter_content(_CHUNK):
                            if cancel.is_set():
                                return ItemResult(path, "cancelled", bytes_done=done)
                            f.write(chunk)
                            done += len(chunk)
                            if on_progress:
                                on_progress(path, done, total)
                    # Content-Length counts encoded bytes; iter_content yields decoded ones.
                    if r.headers.get("Content-Encoding"):
                        total = None
                    if total is not None and done != total:
                        code = "incomplete"
                    else:
                        os.replace(part, path)
                        return ItemResult(path, "done", bytes_done=done)
        except requests.RequestException:
            code = "network_error"
        if attempt < max_attempts - 1:
            cancel.wait(delay)
    return ItemResult(path, "failed", code)
