# Coursera Downloader

A local Streamlit interface for downloading course content that your Coursera account can access.

> This project is an independent personal tool and is not affiliated with Coursera. Use it only for content you are authorized to access and in accordance with Coursera's terms and applicable law.

## Project Status

The project is currently in **Phase 1 — Foundation**.

See [MASTER_PLAN.md](MASTER_PLAN.md) for the source-of-truth roadmap.

## Current Features

- Local Streamlit UI
- Legacy username/password authentication through `coursera-dl`
- Course dropdown
- Content-type selection
- Video, subtitle, PDF, assignment, and supplementary-file filtering
- Download progress display
- Download log viewer
- Retry/cancel controls
- Local credential update/logout

Phase 2 will replace the legacy password flow with browser-cookie authentication.

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

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For development/testing:

```powershell
pip install -r requirements-dev.txt
```

### 4. Configure credentials

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` locally:

```env
COURSERA_USERNAME=your-email@example.com
COURSERA_PASSWORD=your-password
```

Do **not** commit `.env`.

You can also enter/update these credentials from the app sidebar.

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
├── coursera_app/
│   ├── __init__.py
│   ├── auth.py
│   └── config.py
└── tests/
    └── test_config.py
```

## Security

Never commit:

- Coursera passwords
- `.env`
- cookies or session files
- downloaded course content
- authentication tokens

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
