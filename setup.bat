@echo off
REM Setup script for Policy Gap Analysis Tool
REM HACK IITK 2026 - PS1

echo ============================================
echo   Policy Gap Analysis Tool - Setup
echo   HACK IITK 2026 - Cybersecurity Hackathon
echo ============================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)
python --version
echo [OK] Python is installed
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [4/5] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check Ollama
echo [5/5] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not installed or not in PATH
    echo.
    echo Please install Ollama:
    echo   1. Download from: https://ollama.ai
    echo   2. Or run: winget install Ollama.Ollama
    echo.
    echo After installing Ollama, run:
    echo   ollama pull llama3
    echo   ollama serve
    echo.
) else (
    ollama --version
    echo [OK] Ollama is installed
    echo.
    echo To complete setup, run:
    echo   ollama pull llama3
    echo   ollama serve
)
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Ensure Ollama is running: ollama serve
echo   2. Pull a model: ollama pull llama3
echo   3. Run the tool: python main.py
echo.
echo For detailed instructions, see QUICKSTART.md
echo.
pause
