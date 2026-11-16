# Starts the legacy Streamlit app from the repo root so .streamlit/config.toml applies
# (127.0.0.1 only, no usage stats). M5 will switch this to the FastAPI app.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$python = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }

Write-Host "Starting Streamlit (app.py) on 127.0.0.1 using .streamlit/config.toml ..."
& $python -m streamlit run app.py @args
