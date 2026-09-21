"""Browser-cookie authentication for Coursera.

The app reads only the Coursera CAUTH cookie from a supported local browser.
The cookie is kept in memory and is not written to disk by this module.
"""

from typing import Iterable

import rookiepy


SUPPORTED_BROWSERS = ("firefox", "edge", "brave")


class BrowserCookieError(RuntimeError):
    """Raised when a Coursera CAUTH cookie cannot be read from a browser."""


def _find_cauth(cookies: Iterable[dict]) -> str:
    for cookie in cookies:
        if cookie.get("name") == "CAUTH" and cookie.get("value"):
            return str(cookie["value"])
    raise BrowserCookieError(
        "No Coursera CAUTH cookie was found. "
        "Make sure you are logged in to coursera.org in the selected browser."
    )


def read_cauth_from_browser(browser: str) -> str:
    """Read the Coursera CAUTH cookie from a supported browser."""

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
        raise BrowserCookieError(
            "Could not read Coursera cookies from the selected browser. "
            "Confirm you are logged in to Coursera and try again."
        ) from exc

    return _find_cauth(cookies)
