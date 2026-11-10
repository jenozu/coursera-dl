"""Slug validation, safe paths, host and token checks (roadmap 1.6, 4.2, 5.1)."""

from __future__ import annotations

from pathlib import Path


def validate_slug(slug: str) -> str:
    """Return the slug if it matches ``^[a-z0-9][a-z0-9-]{0,127}$``, else raise InvalidSlug."""
    raise NotImplementedError("roadmap 1.6")


def safe_course_dir(download_root: str | Path, slug: str) -> Path:
    """Return the resolved course directory, guaranteed to be inside ``download_root``."""
    raise NotImplementedError("roadmap 1.6")


def sanitize_segment(name: str, max_len: int = 80) -> str:
    """Make one path segment safe on Windows: separators, control chars, reserved names, length."""
    raise NotImplementedError("roadmap 4.2")


def is_allowed_host(host_header: str, port: int) -> bool:
    """True only for 127.0.0.1:<port> or localhost:<port> (DNS-rebinding defence)."""
    raise NotImplementedError("roadmap 5.1")


def new_launch_token() -> str:
    """Random per-launch token the page must send on every API call."""
    raise NotImplementedError("roadmap 5.1")
