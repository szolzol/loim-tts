# Phase 4 Training - Continue from Checkpoint 1901
# ================================================
# Uses 40 new selected Vágó samples to improve Mel CE from 2.971 to < 2.5

Write-Host ""
Write-Host "========================================================================"
Write-Host "PHASE 4 TRAINING - CHECKPOINT 1901 CONTINUATION"
Write-Host "========================================================================"
Write-Host ""
Write-Host "Target: Mel CE < 2.5 (from 2.971)"
Write-Host "Dataset: 40 new selected samples (excitement, neutral, question)"
Write-Host "Starting checkpoint: best_model_1901.pth"
Write-Host ""
Write-Host "========================================================================"
Write-Host ""

# Python executable from conda environment
$python = "I:/CODE/tts-2/.conda/python.exe"

# Check if python exists
if (-not (Test-Path $python)) {
    Write-Host "ERROR: Python not found at $python" -ForegroundColor Red
    Write-Host "Please run setup_environment.ps1 first" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "STEP 1: PREPARE PHASE 4 DATASET"
Write-Host "========================================================================"
Write-Host ""
Write-Host "This will process 40 samples from prepared_sources/vago_samples_selected"
Write-Host ""
Write-Host "IMPORTANT: You need to update transcriptions in prepare_phase4_dataset.py" -ForegroundColor Yellow
Write-Host "           Listen to each audio file and update the TRANSCRIPTIONS dict" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue if transcriptions are ready, or Ctrl+C to cancel"

& $python scripts/prepare_phase4_dataset.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Dataset preparation failed!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "STEP 2: START TRAINING"
Write-Host "========================================================================"
Write-Host ""
Write-Host "Training will resume from checkpoint 1901 (Mel CE: 2.971)"
Write-Host "Target: Mel CE < 2.5"
Write-Host ""
Write-Host "This will take 2-4 hours depending on GPU speed (RTX 5070 Ti)."
Write-Host ""
Write-Host "Training Parameters:" -ForegroundColor Cyan
Write-Host "  - Learning Rate: 5e-7 (ultra-low for refinement)"
Write-Host "  - Batch Size: 2 (focused learning)"
Write-Host "  - Epochs: 50"
Write-Host "  - Dataset: 40 samples (32 train, 8 eval)"
Write-Host ""
Write-Host "Monitoring:" -ForegroundColor Cyan
Write-Host "  - Watch for Mel CE decreasing below 2.5"
Write-Host "  - Text CE should stay < 0.03"
Write-Host "  - Training loss should decrease steadily"
Write-Host ""
Read-Host "Press Enter to start training, or Ctrl+C to cancel"

& $python scripts/train_phase4_continuation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Training failed!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "PHASE 4 TRAINING COMPLETE!"
Write-Host "========================================================================"
Write-Host ""
Write-Host "Check results in: run/training_phase4_continuation/" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Check final Mel CE score"
Write-Host "  2. Update generate_questions_and_answers.py with new model"
Write-Host "  3. Generate test samples to verify quality"
Write-Host ""
pause
