import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 2.5 / 1.2")]


def test_job_moves_queued_crawling_downloading_done():
    """Status transitions recorded in the database."""


def test_restart_marks_running_jobs_interrupted():
    """A job left in 'downloading' becomes 'interrupted' on startup."""


def test_same_course_never_runs_twice_concurrently():
    """Second job for the same slug waits."""


def test_summary_with_failed_item_is_done_with_errors():
    """Never plain 'done' when any item failed (audit H-1)."""
