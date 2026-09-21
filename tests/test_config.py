from coursera_app.config import AppConfig, load_config


def test_app_config_defaults():
    config = AppConfig()

    assert config.coursera_username == ""
    assert config.coursera_password == ""
    assert config.download_dir == "downloads"


def test_load_config_reads_environment(monkeypatch):
    monkeypatch.setenv("COURSERA_USERNAME", "student@example.com")
    monkeypatch.setenv("COURSERA_PASSWORD", "secret")
    monkeypatch.setenv("COURSERA_DOWNLOAD_DIR", "course-files")

    config = load_config()

    assert config.coursera_username == "student@example.com"
    assert config.coursera_password == "secret"
    assert config.download_dir == "course-files"
