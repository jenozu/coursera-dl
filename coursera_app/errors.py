"""Typed application errors with stable codes (roadmap 2.1).

The API returns ``{"error": {"code", "message", "hint"}}`` built from these.
"""

from __future__ import annotations


class AppError(Exception):
    code = "error"
    status = 500
    hint = ""

    def __init__(self, message: str = "", *, hint: str | None = None):
        super().__init__(message or self.code)
        self.message = message or self.code
        if hint is not None:
            self.hint = hint

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "hint": self.hint}}


class AuthExpired(AppError):
    code = "auth_expired"
    status = 401
    hint = "Sign in to coursera.org in your browser, then reconnect."


class CourseNotFound(AppError):
    code = "course_not_found"
    status = 404
    hint = "Check the course slug and that your account is enrolled."


class NetworkError(AppError):
    code = "network"
    status = 502
    hint = "Check your internet connection and try again."


class DiskError(AppError):
    code = "disk_full"
    status = 507
    hint = "Free disk space or choose another download folder."


class RateLimited(AppError):
    code = "rate_limited"
    status = 429
    hint = "Coursera asked us to slow down. The job will retry later."


class InvalidSlug(AppError):
    code = "invalid_slug"
    status = 422
    hint = "Slugs contain only lowercase letters, digits and hyphens."
