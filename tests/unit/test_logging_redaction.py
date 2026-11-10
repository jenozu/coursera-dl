import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 2.3")]


def test_cauth_and_signed_urls_never_reach_log_file():
    """Log a fake CAUTH and a URL with ?Signature=...; neither appears in the log output."""
