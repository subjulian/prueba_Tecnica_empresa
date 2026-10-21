@echo off
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
echo.
echo Swagger: http://localhost:8000/docs
uvicorn app.main:app --reload
