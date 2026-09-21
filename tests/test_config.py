from coursera_app.config import AppConfig, load_config


def test_app_config_defaults():
    config = AppConfig()
    assert config.download_dir == "downloads"


def test_load_config_reads_download_dir(monkeypatch):
    monkeypatch.setenv("COURSERA_DOWNLOAD_DIR", "course-files")

    config = load_config()

    assert config.download_dir == "course-files"
