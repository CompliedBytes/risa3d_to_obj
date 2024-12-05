@echo off
:: Check for Python installation
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH. Please install Python 3.7 or higher and ensure it is in PATH.
    pause
    exit /b
)

:: Check for pip installation
echo Checking for pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not installed or not added to PATH. Please install pip and try again.
    pause
    exit /b
)

:: Install required dependencies
echo Installing required dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check the contents of requirements.txt and your internet connection.
    pause
    exit /b
)

:: Run the application
echo Running the application...
python src\convert.py
if %errorlevel% neq 0 (
    echo The application encountered an error. Please check your script and input files.
    pause
    exit /b
)

echo Application completed successfully!
pause
