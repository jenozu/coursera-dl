$ErrorActionPreference = "Stop"
$python = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }

& $python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python -m pytest -q
exit $LASTEXITCODE
