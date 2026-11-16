import threading

import pytest

from coursera_app.downloader import download_one
from tests.fake_coursera import FakeCoursera

pytestmark = pytest.mark.integration


def _get(tmp_path, route, **kw):
    srv = FakeCoursera()
    srv.start()
    try:
        return download_one(
            f"{srv.base_url}{route}", str(tmp_path / "out.bin"), cancel=threading.Event(), **kw
        )
    finally:
        srv.stop()


def test_success_writes_final_file_and_no_part_file(tmp_path):
    r = _get(tmp_path, "/files/slides.pdf")
    assert r.status == "done"
    assert (tmp_path / "out.bin").exists() and not (tmp_path / "out.bin.part").exists()


def test_http_500_three_times_is_reported_failed(tmp_path):
    r = _get(tmp_path, "/status/500", max_attempts=3)
    assert (r.status, r.error_code) == ("failed", "http_500")


def test_existing_complete_file_is_skipped(tmp_path):
    (tmp_path / "out.bin").write_bytes(b"x")
    assert _get(tmp_path, "/files/slides.pdf").status == "skipped"


def test_404_is_not_retried(tmp_path):
    r = _get(tmp_path, "/files/nope.pdf", max_attempts=5)
    assert (r.status, r.error_code) == ("failed", "http_404")


@pytest.mark.skip(reason="roadmap 4.1 / 4.3")
def test_429_retry_after_waits_then_succeeds():
    """Honours Retry-After."""


@pytest.mark.skip(reason="roadmap 4.1 / 4.3")
def test_mid_body_disconnect_then_resume_completes():
    """Range/206 resume produces byte-identical file."""


@pytest.mark.skip(reason="roadmap 4.1 / 4.3")
def test_slow_server_triggers_timeout_and_retry():
    """Read timeout is enforced."""


@pytest.mark.skip(reason="roadmap 4.1 / 4.3")
def test_cancel_returns_within_one_chunk_and_keeps_part_file():
    """Status 'cancelled'."""
