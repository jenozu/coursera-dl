"""In-process job manager (roadmap 2.5).

One worker thread, one job at a time, a ``threading.Event`` per job for cancel.
Status: queued, crawling, downloading, done, done_with_errors, failed, cancelled, interrupted.
On startup, jobs left in ``crawling``/``downloading`` become ``interrupted``.
"""

from __future__ import annotations


class JobManager:
    def __init__(self, db_path: str = "data/app.db") -> None:
        raise NotImplementedError("roadmap 2.5")

    def submit(self, slug: str, types: list[str]) -> int:
        raise NotImplementedError("roadmap 2.5")

    def cancel(self, job_id: int) -> None:
        raise NotImplementedError("roadmap 4.3")

    def retry_failed(self, job_id: int) -> int:
        raise NotImplementedError("roadmap 2.5")

    def shutdown(self) -> None:
        raise NotImplementedError("roadmap 2.5")
