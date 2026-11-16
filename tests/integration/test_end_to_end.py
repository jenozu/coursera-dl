import pytest

pytestmark = [pytest.mark.integration, pytest.mark.skip(reason="roadmap 7.1")]


def test_crawl_gather_download_against_fake_server():
    """One end-to-end run under 30 seconds; files verified byte-for-byte. No live Coursera."""
