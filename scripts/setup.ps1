$ErrorActionPreference = "Stop"

$python = if (Test-Path ".\.venv\Scripts\python.exe") {
    ".\.venv\Scripts\python.exe"
} else {
    "python"
}

& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

# coursera-dl 0.11.5 pins attrs==18.1.0. Installing it without dependencies
# lets this project use compatible modern dependency versions instead.
& $python -m pip install --no-deps coursera-dl==0.11.5

Write-Host ""
Write-Host "Setup complete."
Write-Host "Run: $python -m streamlit run app.py"
