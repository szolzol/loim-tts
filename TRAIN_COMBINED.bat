@echo off
echo ============================================================================
echo CONTINUE FINE-TUNING WITH BLIKK INTERVIEW DATA
echo István Vágó Voice Clone - Expanding Training Dataset
echo ============================================================================
echo.

REM Set encoding
set PYTHONIOENCODING=utf-8

echo Step 1/2: Preparing combined dataset...
echo ============================================================================
python scripts\prepare_blikk_dataset.py
if errorlevel 1 (
    echo.
    echo ERROR: Dataset preparation failed!
    pause
    exit /b 1
)

echo.
echo.
echo Step 2/2: Continue fine-tuning...
echo ============================================================================
python scripts\train_combined.py

echo.
echo ============================================================================
echo Training complete! Check the output above for results.
echo ============================================================================
pause
