import json

from coursera_app import download_engine
from coursera_app.downloader import ItemResult, download_one
from tests.fake_coursera import FakeCoursera


def _cookies():
    return [
        {
            "domain": ".coursera.org",
            "path": "/",
            "secure": True,
            "expires": 0,
            "name": "CAUTH",
            "value": "token",
        }
    ]


def test_download_course_supports_three_arg_crawl(monkeypatch, tmp_path):
    seen = {}

    def fake_crawl(cookie_file, slug, outdir):
        seen["crawl"] = (cookie_file, slug, outdir)
        return {"slug": slug, "type": "Course"}

    def fake_gather(outdir, course):
        return [
            {
                "url": "https://example.com/video",
                "filename": str(tmp_path / "x.mp4"),
            }
        ]

    def fake_download(url, path, **kw):
        seen["download"] = (url, path)
        return ItemResult(path, "done")

    monkeypatch.setattr(download_engine, "crawl", fake_crawl)
    monkeypatch.setattr(download_engine, "gather_dl_tasks", fake_gather)
    monkeypatch.setattr(download_engine, "download_one", fake_download)

    result = download_engine.download_course(
        cookies=_cookies(),
        course_slug="python-crash-course",
        output_dir=str(tmp_path),
        selected_types=["video"],
    )

    assert seen["crawl"][1:] == ("python-crash-course", str(tmp_path))
    assert seen["download"][0] == "https://example.com/video"
    assert result["selected_tasks"] == 1
    assert result["succeeded"] == 1


def test_download_course_supports_four_arg_crawl(monkeypatch, tmp_path):
    seen = {}

    def fake_crawl(cookie_file, slug, outdir, is_spec):
        seen["crawl"] = (cookie_file, slug, outdir, is_spec)
        return {"slug": slug, "type": "Course"}

    monkeypatch.setattr(download_engine, "crawl", fake_crawl)
    monkeypatch.setattr(download_engine, "gather_dl_tasks", lambda outdir, course: [])

    download_engine.download_course(
        cookies=_cookies(),
        course_slug="python-crash-course",
        output_dir=str(tmp_path),
        selected_types=["video"],
    )

    assert seen["crawl"][1:] == ("python-crash-course", str(tmp_path), False)


def test_download_course_creates_cache_directory(monkeypatch, tmp_path):
    seen = {}

    def fake_crawl(cookie_file, slug, outdir):
        cache_dir = tmp_path / slug / ".cache"
        seen["cache_exists"] = cache_dir.is_dir()
        return {"slug": slug, "type": "Course"}

    monkeypatch.setattr(download_engine, "crawl", fake_crawl)
    monkeypatch.setattr(download_engine, "gather_dl_tasks", lambda outdir, course: [])

    download_engine.download_course(
        cookies=_cookies(),
        course_slug="python-crash-course",
        output_dir=str(tmp_path),
        selected_types=["video"],
    )

    assert seen["cache_exists"] is True


def _run(monkeypatch, tmp_path, tasks, types):
    monkeypatch.setattr(download_engine, "crawl", lambda c, s, o: {})
    monkeypatch.setattr(download_engine, "gather_dl_tasks", lambda o, c: tasks)
    return download_engine.download_course(
        cookies=_cookies(), course_slug="c", output_dir=str(tmp_path), selected_types=types
    )


def test_second_run_with_other_selection_and_stale_failed_json(monkeypatch, tmp_path):
    srv = FakeCoursera()
    srv.start()
    try:
        tasks = [
            {"url": f"{srv.base_url}/files/lecture1.mp4", "filename": str(tmp_path / "c/a.mp4")},
            {"url": f"{srv.base_url}/files/slides.pdf", "filename": str(tmp_path / "c/b.pdf")},
        ]
        cache = tmp_path / "c" / ".cache"
        cache.mkdir(parents=True)
        (cache / "download.dl_tasks_failed.json").write_text(json.dumps([]))
        r1 = _run(monkeypatch, tmp_path, tasks, ["video"])
        r2 = _run(monkeypatch, tmp_path, tasks, ["pdf"])
    finally:
        srv.stop()
    assert r1["succeeded"] == 1 and r2["succeeded"] == 1
    assert (tmp_path / "c/a.mp4").exists() and (tmp_path / "c/b.pdf").exists()


def test_http_500_reported_failed_in_summary(monkeypatch, tmp_path):
    srv = FakeCoursera()
    srv.start()
    try:
        tasks = [{"url": f"{srv.base_url}/status/500", "filename": str(tmp_path / "c/x.mp4")}]
        monkeypatch.setattr(
            download_engine,
            "download_one",
            lambda url, path, **kw: download_one(url, path, max_attempts=2, **kw),
        )
        r = _run(monkeypatch, tmp_path, tasks, ["video"])
    finally:
        srv.stop()
    assert r["failed"] == 1 and r["succeeded"] == 0
    assert r["failures"][0]["reason"] == "http_500"
    assert r["failures"][0]["file"] == "x.mp4"
    assert r["selected_tasks"] == 1
    assert "download_tasks" not in r
