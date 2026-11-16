import pytest

pytestmark = [pytest.mark.api, pytest.mark.skip(reason="roadmap 5.1 - 5.3")]


def test_wrong_host_header_is_400():
    """DNS-rebinding defence."""


def test_missing_token_is_401():
    """Every /api route needs the launch token."""


def test_cross_origin_post_is_403():
    """No CORS; foreign Origin rejected."""


def test_security_headers_present():
    """CSP default-src 'self' and X-Content-Type-Options: nosniff."""


def test_no_response_contains_cookie_values():
    """CAUTH never returned by any route."""


def test_invalid_slug_returns_invalid_slug_error():
    """POST /api/downloads with '../x' -> 422 invalid_slug."""


def test_sse_snapshot_then_delta():
    """Reconnecting client gets a fresh snapshot."""
