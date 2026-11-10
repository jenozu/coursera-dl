"""JSON settings with environment override (roadmap 2.4).

File: ``data/settings.json``. ``COURSERA_DOWNLOAD_DIR`` overrides ``download_dir``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    download_dir: str = "downloads"
    default_types: list[str] = field(default_factory=lambda: ["video", "subtitle", "pdf"])
    concurrency: int = 1


def load_settings(path: Path | None = None) -> Settings:
    raise NotImplementedError("roadmap 2.4")


def save_settings(settings: Settings, path: Path | None = None) -> None:
    """Check download_dir exists or can be created and is writable, then write atomically."""
    raise NotImplementedError("roadmap 2.4")
