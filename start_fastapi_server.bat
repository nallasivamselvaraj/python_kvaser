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
echo.
echo 📚 Swagger UI will be available at:
echo    http://localhost:8000/swagger
echo.
echo 📖 ReDoc will be available at:
echo    http://localhost:8000/redoc
echo.
echo 🌐 Home page:
echo    http://localhost:8000/
echo.
echo 🔍 API endpoints:
echo    http://localhost:8000/channels
echo    http://localhost:8000/messages/send
echo    http://localhost:8000/monitoring/
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

echo.
echo Server stopped.
pause
