@echo off
echo ============================================================
echo XTTS-v2 Training - Istvan Vago Milliomos
echo ============================================================
echo.
echo Setting UTF-8 encoding...
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo Changing to project directory...
cd /d F:\CODE\tts-2

echo.
echo Starting training...
echo Progress will be shown in terminal (no TensorBoard needed)
echo.
python scripts\train_xtts_milliomos.py --auto-start

echo.
echo ============================================================
echo Training finished!
echo ============================================================
pause
