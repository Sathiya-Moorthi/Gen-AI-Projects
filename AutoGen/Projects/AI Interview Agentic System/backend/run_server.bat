@echo off
REM Batch script to run the FastAPI server
REM Make sure you're in the backend directory

REM Activate virtual environment (adjust path if venv is in parent directory)
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

REM Run uvicorn from the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

