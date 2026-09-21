"""Compatibility authentication wrapper around coursera-dl.

Phase 2 will replace direct password authentication with browser-cookie support.
Keeping the upstream dependency behind this module prevents the Streamlit UI from
depending directly on coursera-dl internals.
"""

from dataclasses import dataclass
from typing import Any, List

from coursera.coursera_dl import get_session, login
from coursera.extractors import CourseraExtractor


class CourseraAuthenticationError(RuntimeError):
    """Raised when the current Coursera authentication method fails."""


@dataclass
class CourseraConnection:
    """Authenticated Coursera session and extractor."""

    session: Any
    extractor: Any


def connect(username: str, password: str) -> CourseraConnection:
    """Authenticate using the legacy coursera-dl username/password flow."""

    if not username or not password:
        raise CourseraAuthenticationError("Coursera username and password are required.")

    try:
        session = get_session()
        login(session, username, password)
        return CourseraConnection(
            session=session,
            extractor=CourseraExtractor(session),
        )
    except Exception as exc:
        raise CourseraAuthenticationError(str(exc)) from exc


def list_courses(connection: CourseraConnection) -> List[str]:
    """Return courses visible to the authenticated Coursera account."""

    courses = connection.extractor.list_courses()
    return list(courses or [])
