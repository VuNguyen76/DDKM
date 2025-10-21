@echo off
echo ========================================
echo Starting Face Recognition Backend API
echo ========================================
echo.

cd api
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo Starting Uvicorn server on port 8000...
uvicorn main:app --reload --port 8000

