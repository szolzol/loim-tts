@echo off
REM XTTS v2 Hungarian TTS Setup Script for Windows

echo Setting up XTTS v2 Hungarian TTS environment...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

REM Install other requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check for ffmpeg
echo Checking for ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: ffmpeg not found. MP3 conversion will not work.
    echo Please install ffmpeg manually or use chocolatey: choco install ffmpeg
)

echo Setup complete!
echo.
echo Usage examples:
echo   python xtts_hungarian_tts.py --text "Jó reggelt!" --refs voice1.wav --refs voice2.wav --out output.wav
echo   python xtts_hungarian_tts.py --text "Szép napot!" --refs voice.wav --out greeting.wav --mp3
echo.
echo For help: python xtts_hungarian_tts.py --help
pause