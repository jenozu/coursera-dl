# Coursera Downloader

A local tool for downloading course material that your own Coursera account is enrolled in.

> Independent personal tool, not affiliated with Coursera. Use it only for content you are authorized to access, in line with Coursera's terms and applicable law.

## Status

**Rebuild in progress on branch `rebuild/fastapi`.** The current app is a Streamlit UI with known issues (see `docs/audit/AUDIT_REPORT.md`). A FastAPI + plain HTML/JS app is being built milestone by milestone; see `CLAUDE.md` for the order and `.taskmaster/docs/prd.md` for the goals. Modules under `coursera_app/` that raise `NotImplementedError` belong to the new app and are not used yet.

## What the current app does

- **Connect from Browser:** reads your Coursera cookies (all `coursera.org` cookies, including `CAUTH`) from Firefox, Edge or Brave and keeps them in memory for the session.
- **Manual CAUTH fallback:** paste a `CAUTH` value if browser reading fails.
- **Disconnect:** clears the in-memory session.
- **Course dropdown:** lists your enrolled courses.
- **Content-type checkboxes:** videos, subtitles, PDFs, assignments/HTML, supplementary files, with Select All.
- **Download:** crawls the course with `dl_coursera` and downloads matching files into the download folder, with a status box showing how many resources were found and processed.

Not yet available: per-file progress, cancel, retry, a log viewer, download history. These come with the new app.

Known issues (fixed in milestone M1): repeat downloads of the same course can ignore a new selection (audit C-1), failed files are not reported (H-1), and Streamlit listens on all network interfaces unless started as shown below (H-2).

## Requirements

- Windows 10/11
- **Python 3.11** (the legacy `coursera-dl` package used for course listing does not import on Python 3.12+; it is removed in milestone M2)
- Git

## Setup

```powershell
git clone https://github.com/jenozu/coursera-dl.git
cd coursera-dl
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\scripts\setup.ps1
```

`setup.ps1` installs `requirements-dev.txt` and then the legacy `coursera-dl==0.11.5` with `--no-deps` (its `attrs` pin conflicts with Streamlit). A plain `pip install -r requirements.txt` is not enough for the current app; if a dependency is missing the app says so on startup.

Optional: `Copy-Item .env.example .env` and set `COURSERA_DOWNLOAD_DIR` (default `downloads`).

## Run

Sign in to `coursera.org` in Firefox, Edge or Brave first, then:

```powershell
streamlit run app.py
```

Run it from the repo root: `.streamlit/config.toml` sets `address = "127.0.0.1"` and turns off usage statistics, so the log shows only `http://127.0.0.1:8501` and no Network URL.

Open the URL Streamlit prints (normally `http://localhost:8501`), choose your browser in the sidebar and click **Connect from Browser**. Edge and Brave may need PowerShell run as Administrator.

## Tests

```powershell
.\scripts\dev.ps1          # ruff + pytest
```

Tests never contact Coursera; they use a local fake server (`tests/fake_coursera.py`) and fixtures in `tests/fixtures/`. Skipped tests are acceptance criteria for the rebuild and are enabled as each milestone lands.

## Project structure

```text
app.py                        Streamlit app (current, removed in M7)
run.py, scripts/run.ps1       launcher for the new app (from M5)
coursera_app/
  auth.py                     session + course listing (legacy coursera-dl)
  browser_auth.py             browser cookie reading (rookiepy)
  config.py                   download-folder setting
  download_engine.py          dl_coursera adapter used by app.py
  errors.py                   typed errors (new app)
  main.py, api/, services/,   new FastAPI app (stubs)
  engine.py, downloader.py,
  jobs.py, db.py, schema.sql,
  settings.py, security.py,
  logging_setup.py, web/
tests/                        unit/, integration/, api/, fake server, fixtures
docs/audit/                   audit, architecture, roadmap
docs/LIVE_CHECKLIST.md        manual Windows checks
```

## Security

- Your Coursera password is never asked for or stored.
- Cookies stay in memory; the download step writes them to a temporary file that is deleted when the download ends.
- Never commit `.env`, cookie or session files, `CAUTH` values or downloaded course content.
