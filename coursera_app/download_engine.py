"""Adapter around the maintained dl_coursera download engine."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

from dl_coursera_run import crawl, download, gather_dl_tasks


class DownloadEngineError(RuntimeError):
    """Raised when crawling or downloading a course fails."""


def _netscape_line(cookie: dict) -> str | None:
    name = str(cookie.get("name") or "")
    value = str(cookie.get("value") or "")
    domain = str(cookie.get("domain") or ".coursera.org")
    path = str(cookie.get("path") or "/")

    if not name:
        return None

    if "coursera.org" not in domain:
        return None

    include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
    secure = "TRUE" if bool(cookie.get("secure")) else "FALSE"

    expires = cookie.get("expires")
    try:
        expires = int(float(expires)) if expires not in (None, "") else 0
    except (TypeError, ValueError):
        expires = 0

    return "\t".join(
        [
            domain,
            include_subdomains,
            path,
            secure,
            str(expires),
            name,
            value,
        ]
    )


def _write_cookie_file(cookies: Iterable[dict]) -> str:
    lines = ["# Netscape HTTP Cookie File"]

    for cookie in cookies:
        line = _netscape_line(cookie)
        if line:
            lines.append(line)

    if len(lines) == 1:
        raise DownloadEngineError("No Coursera cookies were available for the download engine.")

    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".cookies.txt",
        prefix="coursera_",
        delete=False,
        newline="\n",
    )
    try:
        handle.write("\n".join(lines) + "\n")
        return handle.name
    finally:
        handle.close()


def cookies_from_cauth(cauth: str) -> list[dict]:
    """Create the minimal cookie set used for manual CAUTH fallback."""

    cauth = (cauth or "").strip()
    if not cauth:
        raise DownloadEngineError("A CAUTH value is required.")

    return [
        {
            "domain": ".coursera.org",
            "path": "/",
            "secure": True,
            "expires": 0,
            "name": "CAUTH",
            "value": cauth,
        }
    ]


def _filter_download_tasks(tasks: Sequence[dict], selected_types: Sequence[str]) -> list[dict]:
    """Filter downloadable resources using filename extensions.

    HTML reading material is generated locally during the gather stage and is
    therefore not part of this URL-download task list.
    """

    selected = set(selected_types or [])
    if not selected or "all" in selected:
        return list(tasks)

    video_exts = {".mp4"}
    subtitle_exts = {".srt", ".vtt"}
    pdf_exts = {".pdf"}
    assignment_exts = {".html", ".htm"}

    filtered = []
    for task in tasks:
        ext = Path(task.get("filename", "")).suffix.lower()

        keep = (
            ("video" in selected and ext in video_exts)
            or ("subtitle" in selected and ext in subtitle_exts)
            or ("pdf" in selected and ext in pdf_exts)
            or ("assignment" in selected and ext in assignment_exts)
            or (
                "supplement" in selected
                and ext not in video_exts | subtitle_exts | pdf_exts | assignment_exts
            )
        )
        if keep:
            filtered.append(task)

    return filtered


def download_course(
    *,
    cookies: Sequence[dict],
    course_slug: str,
    output_dir: str,
    selected_types: Sequence[str],
) -> dict:
    """Crawl and download one enrolled Coursera course."""

    cookie_file = _write_cookie_file(cookies)

    try:
        os.makedirs(output_dir, exist_ok=True)

        course = crawl(
            cookies_file=cookie_file,
            slug=course_slug,
            outdir=output_dir,
            is_spec=False,
        )
        tasks = gather_dl_tasks(output_dir, course)
        filtered_tasks = _filter_download_tasks(tasks, selected_types)

        if filtered_tasks:
            download(
                dl_tasks=filtered_tasks,
                slug=course_slug,
                outdir=output_dir,
            )

        return {
            "course_slug": course_slug,
            "total_tasks": len(tasks),
            "download_tasks": len(filtered_tasks),
            "output_dir": os.path.abspath(output_dir),
        }
    except Exception as exc:
        raise DownloadEngineError(str(exc)) from exc
    finally:
        try:
            os.remove(cookie_file)
        except OSError:
            pass
