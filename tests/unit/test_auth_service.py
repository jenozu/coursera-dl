import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skip(reason="roadmap 2.2 / 3.1 / 3.3")]


def test_401_or_403_is_expired():
    """check_session returns 'expired'."""


def test_connection_error_is_network_error_not_expired():
    """Audit M-2."""


def test_200_is_valid():
    """check_session returns 'valid'."""


@pytest.mark.parametrize("case", ["empty", "malformed_json", "missing_linked_key"])
def test_list_courses_bad_replies_raise_typed_error(case):
    """No raw KeyError reaches callers."""


def test_cached_course_still_triggers_session_check():
    """Audit M-2: the engine's cache must not hide an expired session."""
