import pytest

pytestmark = [pytest.mark.integration, pytest.mark.skip(reason="roadmap 4.1 / 4.3")]


def test_success_writes_final_file_and_no_part_file():
    """Download from the fake server; final file correct, .part removed."""


def test_http_500_three_times_is_reported_failed():
    """Result status 'failed' with an error code (audit H-1)."""


def test_429_retry_after_waits_then_succeeds():
    """Honours Retry-After."""


def test_mid_body_disconnect_then_resume_completes():
    """Range/206 resume produces byte-identical file."""


def test_slow_server_triggers_timeout_and_retry():
    """Read timeout is enforced."""


def test_existing_complete_file_is_skipped():
    """Status 'skipped'; no request body fetched."""


def test_cancel_returns_within_one_chunk_and_keeps_part_file():
    """Status 'cancelled'."""


def test_404_is_not_retried():
    """401/403/404 fail fast."""
