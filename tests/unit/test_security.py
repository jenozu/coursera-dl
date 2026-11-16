import os

import pytest

from coursera_app.errors import InvalidSlug
from coursera_app.security import safe_course_dir, validate_slug


@pytest.mark.unit
@pytest.mark.parametrize(
    "slug",
    ["../x", "a/b", "a\\b", "/abs", "C:evil", "", "-leading", "A-upper", "x" * 129, "a\n"],
)
def test_rejects_traversal_slug(slug):
    """'../x', 'a/b', absolute paths, empty and over-long slugs raise InvalidSlug (audit M-6)."""
    with pytest.raises(InvalidSlug):
        validate_slug(slug)


@pytest.mark.unit
@pytest.mark.parametrize("slug", ["machine-learning", "python-3", "a", "x" * 128])
def test_accepts_normal_slug(slug):
    """'machine-learning', 'python-3' pass unchanged."""
    assert validate_slug(slug) == slug


@pytest.mark.unit
def test_course_dir_is_inside_download_root(tmp_path):
    """safe_course_dir never resolves outside the download root."""
    root = tmp_path / "downloads"
    root.mkdir()
    course = safe_course_dir(str(root), "python-3")
    assert os.path.commonpath([os.path.realpath(root), str(course)]) == os.path.realpath(root)
    assert course.name == "python-3"
    with pytest.raises(InvalidSlug):
        safe_course_dir(str(root), "../escaped")


@pytest.mark.unit
@pytest.mark.skip(reason="roadmap 4.2")
def test_sanitize_segment_windows_rules():
    """CON, trailing dots/spaces, 300-char titles, unicode, '..', separators."""


@pytest.mark.unit
@pytest.mark.skip(reason="roadmap 5.1")
def test_host_header_allowlist():
    """Only 127.0.0.1:<port> and localhost:<port> are accepted."""
