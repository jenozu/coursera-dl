"""Roadmap 1.3 (audit H-2): Streamlit listens on localhost only and sends no usage stats."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_streamlit_binds_localhost_and_disables_usage_stats():
    cfg = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert cfg["server"]["address"] == "127.0.0.1"
    assert cfg["browser"]["gatherUsageStats"] is False


def test_streamlit_config_is_not_ignored_by_git():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "!.streamlit/config.toml" in lines
    assert ".streamlit/" not in lines
