# Coursera Downloader

A local Streamlit interface for downloading course content that your Coursera account can access.

> This project is an independent personal tool and is not affiliated with Coursera. Use it only for content you are authorized to access and in accordance with Coursera's terms and applicable law.

## Project Status

The project is currently in **Phase 1 — Foundation**.

See [MASTER_PLAN.md](MASTER_PLAN.md) for the source-of-truth roadmap.

## Current Features

- Local Streamlit UI
- Browser-based Coursera authentication using the existing CAUTH session cookie
- Course dropdown
- Content-type selection
- Video, subtitle, PDF, assignment, and supplementary-file filtering
- Download progress display
- Download log viewer
- Retry/cancel controls
- Local credential update/logout

Phase 2 browser-cookie authentication is now implemented and awaiting live Windows verification.

## Requirements

Recommended:

- Windows 10/11
- Python 3.10 or 3.11
- Git

The upstream `coursera-dl` dependency is old, so newer Python versions may require additional compatibility work.

## Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/jenozu/coursera-dl.git
cd coursera-dl
```

### 2. Create a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can instead run Python directly from `.venv\Scripts\python.exe`.

### 3. Install dependencies

The upstream `coursera-dl 0.11.5` package pins `attrs==18.1.0`, which conflicts with modern Streamlit packages. Install this project’s dependencies first, then install `coursera-dl` without its legacy dependency pins:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install --no-deps coursera-dl==0.11.5
```

Or run the included Windows setup helper:

```powershell
.\scripts\setup.ps1
```

For development/testing:

```powershell
pip install -r requirements-dev.txt
```

### 4. Optional local settings

You do not need to store your Coursera email or password. Log in to `coursera.org` in Firefox, Edge, or Brave.

Optionally copy the settings example:

```powershell
Copy-Item .env.example .env
```

The only current setting is the download directory:

```env
COURSERA_DOWNLOAD_DIR=downloads
```

### 5. Run the app

```powershell
streamlit run app.py
```

Then open the local URL Streamlit prints, normally:

```text
http://localhost:8501
```

## Running Tests

```powershell
pytest
```

## Project Structure

```text
coursera-dl/
├── app.py
├── MASTER_PLAN.md
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── scripts/
│   └── setup.ps1
├── coursera_app/
│   ├── __init__.py
│   ├── auth.py
│   └── config.py
└── tests/
    └── test_config.py
```

## Authentication

1. Sign in to `coursera.org` in Firefox, Edge, or Brave.
2. Start the app.
3. Select that browser in the sidebar.
4. Click **Connect from Browser**.
5. The app reads only the Coursera `CAUTH` cookie and keeps it in memory for the current Streamlit session.

If automatic reading fails, the sidebar provides a manual CAUTH fallback.

## Security

Never commit:

- `.env`
- cookies or session files
- CAUTH values
- downloaded course content
- authentication tokens

The normal app flow does not store your Coursera password.

## Download Location

By default, downloaded content is written under:

```text
downloads/
```

A custom location can be set with:

```env
COURSERA_DOWNLOAD_DIR=D:\Coursera
```

## Architecture Direction

The Streamlit UI should not depend directly on upstream `coursera-dl` internals long-term. The project will progressively move authentication, course retrieval, and downloads behind application service modules so the backend can be replaced or updated without rewriting the UI.
