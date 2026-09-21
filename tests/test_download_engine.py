from coursera_app import download_engine


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

    def fake_download(tasks, slug, outdir):
        seen["download"] = (tasks, slug, outdir)

    monkeypatch.setattr(download_engine, "crawl", fake_crawl)
    monkeypatch.setattr(download_engine, "gather_dl_tasks", fake_gather)
    monkeypatch.setattr(download_engine, "download", fake_download)

    result = download_engine.download_course(
        cookies=_cookies(),
        course_slug="python-crash-course",
        output_dir=str(tmp_path),
        selected_types=["video"],
    )

    assert seen["crawl"][1:] == ("python-crash-course", str(tmp_path))
    assert seen["download"][1:] == ("python-crash-course", str(tmp_path))
    assert result["download_tasks"] == 1


def test_download_course_supports_four_arg_crawl(monkeypatch, tmp_path):
    seen = {}

    def fake_crawl(cookie_file, slug, outdir, is_spec):
        seen["crawl"] = (cookie_file, slug, outdir, is_spec)
        return {"slug": slug, "type": "Course"}

    monkeypatch.setattr(download_engine, "crawl", fake_crawl)
    monkeypatch.setattr(download_engine, "gather_dl_tasks", lambda outdir, course: [])
    monkeypatch.setattr(download_engine, "download", lambda tasks, slug, outdir: None)

    download_engine.download_course(
        cookies=_cookies(),
        course_slug="python-crash-course",
        output_dir=str(tmp_path),
        selected_types=["video"],
    )

    assert seen["crawl"][1:] == ("python-crash-course", str(tmp_path), False)
