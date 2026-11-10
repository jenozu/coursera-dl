import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 1.6 / 4.2 / 5.1")]


def test_rejects_traversal_slug():
    """'../x', 'a/b', absolute paths, empty and over-long slugs raise InvalidSlug (audit M-6)."""


def test_accepts_normal_slug():
    """'machine-learning', 'python-3' pass unchanged."""


def test_course_dir_is_inside_download_root():
    """safe_course_dir never resolves outside the download root."""


def test_sanitize_segment_windows_rules():
    """CON, trailing dots/spaces, 300-char titles, unicode, '..', separators."""


def test_host_header_allowlist():
    """Only 127.0.0.1:<port> and localhost:<port> are accepted."""
