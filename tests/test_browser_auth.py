import pytest

from coursera_app.browser_auth import (
    BrowserCookieError,
    SUPPORTED_BROWSERS,
    read_cauth_from_browser,
)


@pytest.mark.parametrize("browser", SUPPORTED_BROWSERS)
def test_reads_cauth_from_supported_browser(monkeypatch, browser):
    def fake_reader(domains):
        assert domains == ["coursera.org"]
        return [
            {"name": "OTHER", "value": "x"},
            {"name": "CAUTH", "value": "test-token"},
        ]

    monkeypatch.setattr(
        f"coursera_app.browser_auth.rookiepy.{browser}",
        fake_reader,
    )

    assert read_cauth_from_browser(browser) == "test-token"


def test_rejects_unsupported_browser():
    with pytest.raises(BrowserCookieError):
        read_cauth_from_browser("chrome")


def test_reports_missing_cauth(monkeypatch):
    monkeypatch.setattr(
        "coursera_app.browser_auth.rookiepy.firefox",
        lambda domains: [{"name": "OTHER", "value": "x"}],
    )

    with pytest.raises(BrowserCookieError, match="No Coursera CAUTH"):
        read_cauth_from_browser("firefox")
