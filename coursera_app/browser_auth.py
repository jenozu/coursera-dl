"""Browser-cookie authentication for Coursera."""

from typing import Iterable, List

import rookiepy


SUPPORTED_BROWSERS = ("firefox", "edge", "brave")


class BrowserCookieError(RuntimeError):
    """Raised when Coursera cookies cannot be read from a browser."""


def _find_cauth(cookies: Iterable[dict]) -> str:
    for cookie in cookies:
        if cookie.get("name") == "CAUTH" and cookie.get("value"):
            return str(cookie["value"])
    raise BrowserCookieError(
        "No Coursera CAUTH cookie was found. "
        "Make sure you are logged in to coursera.org in the selected browser."
    )


def read_coursera_cookies_from_browser(browser: str) -> List[dict]:
    """Read Coursera cookies from a supported local browser."""

    browser = browser.strip().lower()
    if browser not in SUPPORTED_BROWSERS:
        raise BrowserCookieError(
            f"Unsupported browser: {browser}. "
            f"Choose one of: {', '.join(SUPPORTED_BROWSERS)}."
        )

    try:
        if browser == "firefox":
            cookies = rookiepy.firefox(["coursera.org"])
        elif browser == "edge":
            cookies = rookiepy.edge(["coursera.org"])
        else:
            cookies = rookiepy.brave(["coursera.org"])
    except Exception as exc:
        admin_hint = (
            " Edge and Brave may require running PowerShell as Administrator."
            if browser in {"edge", "brave"}
            else ""
        )
        raise BrowserCookieError(
            "Could not read Coursera cookies from the selected browser. "
            "Confirm you are logged in to Coursera and try again."
            + admin_hint
        ) from exc

    cookies = list(cookies or [])
    _find_cauth(cookies)
    return cookies


def read_cauth_from_browser(browser: str) -> str:
    """Read only the Coursera CAUTH cookie from a supported browser."""

    return _find_cauth(read_coursera_cookies_from_browser(browser))
