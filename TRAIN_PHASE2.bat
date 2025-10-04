@echo off
echo ======================================================================
echo COMBINED TRAINING - PHASE 2
echo ======================================================================
echo.
echo Current Status:
echo   - Mel CE: 3.507 (high quality)
echo   - Target: ^< 2.5 (excellent quality)
echo   - Resume from: checkpoint_1500.pth
echo.
echo Phase 2 Strategy:
echo   - Learning Rate: 1e-6 (ultra-low for fine refinement)
echo   - Additional Epochs: 30
echo   - Focus: Ultra-smooth audio quality
echo.
echo ======================================================================
echo.
echo Starting training in 3 seconds...
timeout /t 3 /nobreak >nul
echo.

python scripts\train_combined_phase2.py

echo.
echo ======================================================================
echo Training session ended
echo Check the logs in run/training_combined_phase2/
echo ======================================================================
pause
