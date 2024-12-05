@echo off
:: Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.7 or higher and try again.
    pause
    exit /b
)

:: Install required dependencies
echo Installing required dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check your Python and pip installation.
    pause
    exit /b
)

:: Run the application
echo Running the application...
python convert.py

pause
