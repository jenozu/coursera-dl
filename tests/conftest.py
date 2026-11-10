from __future__ import annotations

import pytest

from tests.fake_coursera import FakeCoursera


@pytest.fixture
def fake_coursera():
    """Local HTTP server standing in for Coursera. Never touches the real site."""
    server = FakeCoursera()
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def cookies():
    return [
        {
            "domain": ".coursera.org",
            "path": "/",
            "secure": True,
            "expires": 0,
            "name": "CAUTH",
            "value": "fake-token",
        }
    ]
