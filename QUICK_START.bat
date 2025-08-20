@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 🎯 Adobe Finale - Quick Start Script for Windows Judges
REM This script automatically sets up and starts your Adobe Finale application

echo 🚀 Adobe Finale - Quick Start for Judges
echo ==========================================

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: Please run this script from the Adobe_Round3 directory
    echo    Current directory: %CD%
    pause
    exit /b 1
)
if not exist "frontend" (
    echo ❌ Error: Please run this script from the Adobe_Round3 directory
    echo    Current directory: %CD%
    pause
    exit /b 1
)

REM Check prerequisites
echo 🔍 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do set PYTHON_MAJOR=%%a& set PYTHON_MINOR=%%b
if %PYTHON_MAJOR% LSS 3 (
    echo ❌ Python version %PYTHON_VERSION% is too old. Please install Python 3.10+
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 10 (
    echo ❌ Python version %PYTHON_VERSION% is too old. Please install Python 3.10+
    pause
    exit /b 1
)

echo ✅ Python %PYTHON_VERSION% found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

for /f "tokens=1 delims=." %%i in ('node --version') do set NODE_VERSION=%%i
set NODE_VERSION=%NODE_VERSION:~1%
if %NODE_VERSION% LSS 16 (
    echo ❌ Node.js version !NODE_VERSION! is too old. Please install Node.js 16+
    pause
    exit /b 1
)

echo ✅ Node.js !NODE_VERSION! found

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm
    pause
    exit /b 1
)

echo ✅ npm found

echo.
echo 🚀 Starting Adobe Finale...

REM Start Backend
echo 🔧 Starting Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies if requirements.txt is newer than .venv
if requirements.txt -nt .venv (
    echo 📥 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Start backend in background
echo 🚀 Starting backend server on port 8080...
start /B uvicorn app.main:app --host 0.0.0.0 --port 8080 > backend.log 2>&1

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8080/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend failed to start. Check backend.log for details
    pause
    exit /b 1
) else (
    echo ✅ Backend is running on http://localhost:8080
)

REM Start Frontend
echo 🎨 Starting Frontend...
cd ..\frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📥 Installing Node.js dependencies...
    npm install
)

REM Start frontend in background
echo 🚀 Starting frontend on port 3000...
start /B npm start > frontend.log 2>&1

REM Wait for frontend to start
echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

REM Check if frontend is running
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend failed to start. Check frontend.log for details
    pause
    exit /b 1
) else (
    echo ✅ Frontend is running on http://localhost:3000
)

echo.
echo 🎉 Adobe Finale is now running!
echo =================================
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8080
echo 📚 API Docs: http://localhost:8080/docs
echo.
echo 📖 Demo Instructions:
echo 1. Open http://localhost:3000 in your browser
echo 2. Upload 2-3 PDF research papers
echo 3. Select text and generate insights
echo 4. Create and play podcasts
echo.
echo 🛑 To stop the application:
echo    Close the terminal windows or use Task Manager
echo.
echo 📝 Logs:
echo    Backend:  type backend\backend.log
echo    Frontend: type frontend\frontend.log
echo.
echo 🎯 Happy judging! 🚀
pause
