import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 2.4")]


def test_defaults():
    """No file, no env: download_dir == 'downloads'."""


def test_env_overrides_file():
    """COURSERA_DOWNLOAD_DIR beats settings.json."""


def test_rejects_unwritable_download_dir():
    """save_settings raises for a path that cannot be created or written."""
