"""Rotating file log with secret redaction (roadmap 2.3)."""

from __future__ import annotations

import logging


class RedactingFilter(logging.Filter):
    """Mask CAUTH/cookie values and signed-URL query strings in every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError("roadmap 2.3")


def setup_logging(log_dir: str = "data/logs") -> None:
    raise NotImplementedError("roadmap 2.3")
