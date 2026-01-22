# PowerShell script to run the FastAPI server
# Make sure you're in the backend directory

# Activate virtual environment (adjust path if venv is in parent directory)
if (Test-Path "..\venv\Scripts\Activate.ps1") {
    & "..\venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Run uvicorn from the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

