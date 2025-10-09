@echo off
REM Phase 4 Training - Continue from Checkpoint 1901
REM ================================================
REM Uses 40 new selected Vágó samples to improve Mel CE from 2.971 to < 2.5

echo.
echo ========================================================================
echo PHASE 4 TRAINING - CHECKPOINT 1901 CONTINUATION
echo ========================================================================
echo.
echo Target: Mel CE ^< 2.5 (from 2.971)
echo Dataset: 40 new selected samples (excitement, neutral, question)
echo Starting checkpoint: best_model_1901.pth
echo.
echo ========================================================================
echo.

REM Activate conda environment
echo Activating conda environment...
call conda activate I:\CODE\tts-2\.conda
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate conda environment
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 1: PREPARE PHASE 4 DATASET
echo ========================================================================
echo.
echo This will process 40 samples from prepared_sources/vago_samples_selected
echo.
pause

python scripts\prepare_phase4_dataset.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Dataset preparation failed!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 2: START TRAINING
echo ========================================================================
echo.
echo Training will resume from checkpoint 1901 (Mel CE: 2.971)
echo Target: Mel CE ^< 2.5
echo.
echo This will take 2-4 hours depending on GPU speed.
echo.
echo Press Ctrl+C to cancel, or any key to start training...
pause

python scripts\train_phase4_continuation.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Training failed!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo PHASE 4 TRAINING COMPLETE!
echo ========================================================================
echo.
echo Check results in: run/training_phase4_continuation/
echo.
pause
