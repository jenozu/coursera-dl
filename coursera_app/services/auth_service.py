"""In-memory session store and Coursera session checks (roadmap 2.2, 3.1, 3.3).

Replaces the legacy ``coursera-dl`` ``get_session``/``list_courses``. Cookies live only in
memory. ``list_courses`` is one GET to
https://api.coursera.org/api/memberships.v1?includes=courseId,courses.v1&q=me&showHidden=true&filter=current,preEnrolled
and reads ``linked["courses.v1"][*]["slug"]``.
"""

from __future__ import annotations


class SessionStore:
    def connect_from_browser(self, browser: str) -> None:
        raise NotImplementedError("roadmap 3.3")

    def connect_manual(self, cauth: str) -> None:
        raise NotImplementedError("roadmap 3.3")

    def disconnect(self) -> None:
        raise NotImplementedError("roadmap 3.3")

    def status(self) -> dict:
        raise NotImplementedError("roadmap 3.5")


def check_session(store: SessionStore) -> str:
    """Return 'valid', 'expired' or 'network_error'. Network failures are never 'expired'."""
    raise NotImplementedError("roadmap 3.1")


def list_courses(store: SessionStore) -> list[str]:
    raise NotImplementedError("roadmap 2.2")
