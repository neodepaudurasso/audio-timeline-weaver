
@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing required packages...
pip install PyQt5 pydub matplotlib numpy

echo Installation completed successfully.
echo You can now run the application using run.bat
pause
