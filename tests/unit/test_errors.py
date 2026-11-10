import pytest

from coursera_app.errors import AuthExpired, InvalidSlug

pytestmark = pytest.mark.unit


def test_error_dict_shape():
    body = AuthExpired("session ended").to_dict()["error"]
    assert body["code"] == "auth_expired"
    assert body["message"] == "session ended"
    assert body["hint"]


def test_status_codes():
    assert AuthExpired().status == 401
    assert InvalidSlug().status == 422
