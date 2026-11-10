"""Create jobs, summarize outcomes (roadmap 1.2, 2.5).

Summary is derived from item rows: downloaded, skipped, failed counts. A job with any failed
item is ``done_with_errors``, never plain ``done`` (audit H-1).
"""

from __future__ import annotations


def summarize(items: list[dict]) -> dict:
    raise NotImplementedError("roadmap 1.2")
