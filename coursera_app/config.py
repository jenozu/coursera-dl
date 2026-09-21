"""Configuration helpers for the Coursera Downloader."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from environment variables."""

    coursera_username: str = ""
    coursera_password: str = ""
    download_dir: str = "downloads"


def load_config() -> AppConfig:
    """Load configuration from .env/environment without exposing secrets."""

    load_dotenv()
    return AppConfig(
        coursera_username=os.getenv("COURSERA_USERNAME", "").strip(),
        coursera_password=os.getenv("COURSERA_PASSWORD", ""),
        download_dir=os.getenv("COURSERA_DOWNLOAD_DIR", "downloads").strip() or "downloads",
    )


def write_legacy_credentials(username: str, password: str, env_path: str = ".env") -> None:
    """Persist prototype username/password credentials until Phase 2 auth is implemented."""

    safe_username = username.replace("\n", "").replace("\r", "")
    safe_password = password.replace("\n", "").replace("\r", "")
    with open(env_path, "w", encoding="utf-8") as env_file:
        env_file.write(f"COURSERA_USERNAME={safe_username}\n")
        env_file.write(f"COURSERA_PASSWORD={safe_password}\n")


def clear_legacy_credentials(env_path: str = ".env") -> None:
    """Clear prototype credentials from the local environment file."""

    write_legacy_credentials("", "", env_path=env_path)
