@echo off
REM Continue Training - Focus on Mel CE Improvement
REM Combined Dataset: Milliomos (80) + Blikk (231) = 311 samples, 39.7 minutes

echo ===============================================================
echo CONTINUE TRAINING - FOCUS ON MEL CE (SMOOTHNESS) IMPROVEMENT
echo ===============================================================
echo.
echo Dataset: Combined (311 samples, 39.7 minutes)
echo Starting from: Best Milliomos model (Text CE: 0.0234, Mel CE: 5.046)
echo Target: Mel CE ^< 2.5 for excellent smoothness
echo.
echo Configuration:
echo   - Epochs: 40 (more training for better smoothness)
echo   - Learning Rate: 1.5e-6 (lower for fine-tuning)
echo   - Batch Size: 3
echo   - Auto cleanup: Enabled (saves disk space)
echo.
echo Press Ctrl+C to stop training at any time
echo ===============================================================
echo.

python scripts\train_combined.py

echo.
echo ===============================================================
echo Training completed or stopped
echo Check results in: run\training_combined\
echo ===============================================================
pause
