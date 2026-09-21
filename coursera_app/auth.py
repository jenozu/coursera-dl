"""Coursera authentication/session helpers."""

from dataclasses import dataclass
from typing import Any, List

from coursera.coursera_dl import get_session
from coursera.extractors import CourseraExtractor


class CourseraAuthenticationError(RuntimeError):
    """Raised when Coursera authentication is missing, invalid, or expired."""


@dataclass
class CourseraConnection:
    """Authenticated Coursera session and extractor."""

    session: Any
    extractor: Any


def connect_with_cauth(cauth: str) -> CourseraConnection:
    """Create a Coursera session authenticated with a CAUTH cookie."""

    cauth = (cauth or "").strip()
    if not cauth:
        raise CourseraAuthenticationError("A Coursera CAUTH cookie is required.")

    try:
        session = get_session()
        session.cookies.set("CAUTH", cauth, domain=".coursera.org", path="/")
        extractor = CourseraExtractor(session)
        return CourseraConnection(session=session, extractor=extractor)
    except Exception as exc:
        raise CourseraAuthenticationError(
            "Could not create an authenticated Coursera session."
        ) from exc


def list_courses(connection: CourseraConnection) -> List[str]:
    """Return courses visible to the authenticated Coursera account."""

    try:
        courses = connection.extractor.list_courses()
    except Exception as exc:
        raise CourseraAuthenticationError(
            "Coursera rejected the browser session. "
            "Your login may have expired; sign in to coursera.org again and reconnect."
        ) from exc

    return list(courses or [])
