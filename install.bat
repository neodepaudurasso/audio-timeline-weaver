
@echo off
echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment. Ensure Python is installed and accessible.
    pause
    exit /b %ERRORLEVEL%
)

echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %ERRORLEVEL%
)

echo Upgrading pip...
python.exe -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip.
    pause
    exit /b %ERRORLEVEL%
)

echo Installing required packages (audioop-lts, PyQt5, pydub, matplotlib, numpy)...
pip install audioop-lts PyQt5 pydub matplotlib numpy
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install one or more packages. Check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo Installation completed successfully.
echo You can now run the application using run.bat
pause
