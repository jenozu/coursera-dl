import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 2.1 / 4.4 / 4.5")]


@pytest.mark.parametrize("name", ["a.mp4", "a.srt", "a.pdf", "a.html", "a.ipynb", "noext"])
def test_classify_table(name):
    """Each extension maps to the documented kind; extensionless is 'other'."""


def test_second_run_downloads_new_selection():
    """Run 1 videos, run 2 PDFs on the same course: both sets exist (audit C-1)."""


def test_stale_failed_list_file_is_ignored():
    """A leftover download.dl_tasks_failed.json has no effect on selection."""


def test_selecting_only_video_writes_no_reading_html():
    """Or the behavior is explicitly documented and surfaced in the UI (audit M-7)."""


def test_cookie_file_removed_on_success_error_and_cancel():
    """The temp cookie file never survives a job."""


def test_engine_exceptions_map_to_typed_errors():
    """CookiesExpiredException -> AuthExpired, NotFoundExcepton -> CourseNotFound,
    requests errors -> NetworkError."""
