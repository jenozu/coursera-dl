"""Configuration helpers for the Coursera Downloader."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    """Non-secret runtime configuration."""

    download_dir: str = "downloads"


def load_config() -> AppConfig:
    """Load non-secret configuration from .env/environment."""

    load_dotenv()
    return AppConfig(
        download_dir=os.getenv("COURSERA_DOWNLOAD_DIR", "downloads").strip()
        or "downloads",
    )
