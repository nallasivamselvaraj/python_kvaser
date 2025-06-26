@echo off
echo.
echo =============================================
echo  CAN Channel Backend Server with FastAPI
echo =============================================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking dependencies...
python -c "import fastapi, uvicorn, canlib; print('✓ All dependencies available')" 2>nul
if errorlevel 1 (
    echo ✗ Missing dependencies. Installing...
    pip install -r requirements.txt
)

echo.
echo Starting CAN Channel Backend Server with FastAPI...
echo ✓ Server will start on: http://localhost:8000
echo ✓ Swagger UI:           http://localhost:8000/swagger
echo ✓ ReDoc:                http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.
python server.py

echo.
echo Server stopped.
pause
