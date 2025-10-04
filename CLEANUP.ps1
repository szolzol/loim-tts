# Cleanup Script - Remove Unnecessary Training and Sample Files
# Keep only what's needed for Phase 2 best model sample generation

Write-Host ""
Write-Host "=" * 70
Write-Host "🧹 CLEANUP - Removing Unnecessary Training & Sample Files"
Write-Host "=" * 70
Write-Host ""

# Calculate sizes before cleanup
Write-Host "📊 Calculating current disk usage..."
$beforeSize = (Get-ChildItem "F:\CODE\tts-2" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "Current total: $([math]::Round($beforeSize, 2)) GB"
Write-Host ""

# =============================================================================
# 1. DELETE OLD TRAINING DIRECTORIES (Keep only Phase 2)
# =============================================================================
Write-Host "🗑️  Step 1: Removing old training directories..."
Write-Host ""

$trainingToDelete = @(
    "run\training",  # Original Milliomos training
    "run\training_combined"  # Phase 1 combined training
)

foreach ($dir in $trainingToDelete) {
    if (Test-Path $dir) {
        $size = [math]::Round((Get-ChildItem $dir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
        Write-Host "   Deleting: $dir ($size GB)"
        Remove-Item $dir -Recurse -Force
        Write-Host "   ✅ Deleted"
    }
}

Write-Host ""
Write-Host "✅ Old training directories removed!"
Write-Host ""

# =============================================================================
# 2. DELETE OLD SAMPLE DIRECTORIES (Keep only quiz_samples_phase2_final)
# =============================================================================
Write-Host "🗑️  Step 2: Removing old sample directories..."
Write-Host ""

$samplesToDelete = @(
    "comparison_outputs",
    "generated_samples_phase2",
    "output",
    "output_quiz_show",
    "quiz_show_samples_phase2",
    "test_outputs",
    "test_outputs_combined",
    "test_outputs_combined_extended",
    "test_outputs_combined_more",
    "test_outputs_phase2_best",
    "test_outputs_v2"
)

foreach ($dir in $samplesToDelete) {
    if (Test-Path $dir) {
        $size = [math]::Round((Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
        Write-Host "   Deleting: $dir ($size MB)"
        Remove-Item $dir -Recurse -Force
        Write-Host "   Deleted"
    }
}

Write-Host ""
Write-Host "✅ Old sample directories removed!"
Write-Host "✅ Kept: quiz_samples_phase2_final (Phase 2 best model samples)"
Write-Host ""

# =============================================================================
# 3. DELETE UNNECESSARY TRAINING SCRIPTS
# =============================================================================
Write-Host "🗑️  Step 3: Removing old training scripts..."
Write-Host ""

$scriptsToDelete = @(
    "scripts\train.py",
    "scripts\train_phase2.py",
    "scripts\continue_training.py",
    "scripts\monitor_training.py",
    "scripts\cleanup_checkpoints.py",
    "scripts\analyze_quality.py",
    "scripts\compare_models.py",
    "scripts\evaluate_samples.py",
    "scripts\reclassify_dataset.py",
    "scripts\prepare_blikk_dataset.py",
    "scripts\regenerate_improved.py",
    "scripts\merge_quiz_show.py"
)

foreach ($script in $scriptsToDelete) {
    if (Test-Path $script) {
        Write-Host "   Deleting: $script"
        Remove-Item $script -Force
        Write-Host "   ✅ Deleted"
    }
}

Write-Host ""
Write-Host "✅ Old training scripts removed!"
Write-Host ""

# =============================================================================
# 4. DELETE UNNECESSARY SAMPLE GENERATION SCRIPTS (Keep only working one)
# =============================================================================
Write-Host "🗑️  Step 4: Removing old sample generation scripts..."
Write-Host ""

$sampleScriptsToDelete = @(
    "scripts\generate_samples.py",
    "scripts\generate_best_samples.py",
    "scripts\generate_more_combined_samples.py",
    "scripts\generate_phase2_samples.py",
    "scripts\generate_quizshow_samples.py",
    "scripts\test_combined_model.py",
    "scripts\generate_quiz_question.py",
    "scripts\generate_full_quiz_show.py"
)

foreach ($script in $sampleScriptsToDelete) {
    if (Test-Path $script) {
        Write-Host "   Deleting: $script"
        Remove-Item $script -Force
        Write-Host "   ✅ Deleted"
    }
}

Write-Host ""
Write-Host "✅ Old sample generation scripts removed!"
Write-Host "✅ Kept: scripts\generate_quiz_phase2.py (working script for Phase 2 model)"
Write-Host ""

# =============================================================================
# 5. DELETE OLD TRAINING BATCH FILES
# =============================================================================
Write-Host "🗑️  Step 5: Removing old training batch files..."
Write-Host ""

$batchToDelete = @(
    "TRAIN.bat",
    "TRAIN_COMBINED.bat",
    "TRAIN_COMBINED_MEL_FOCUS.bat"
)

foreach ($batch in $batchToDelete) {
    if (Test-Path $batch) {
        Write-Host "   Deleting: $batch"
        Remove-Item $batch -Force
        Write-Host "   ✅ Deleted"
    }
}

Write-Host ""
Write-Host "✅ Old batch files removed!"
Write-Host "✅ Kept: TRAIN_PHASE2.bat (if needed for reference)"
Write-Host ""

# =============================================================================
# 6. CLEAN UP PHASE 2 DIRECTORY (Keep only best model and essentials)
# =============================================================================
Write-Host "🗑️  Step 6: Cleaning Phase 2 training directory..."
Write-Host ""

$phase2Dir = "run\training_combined_phase2\XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd"

if (Test-Path $phase2Dir) {
    Write-Host "   Removing intermediate checkpoints from Phase 2..."
    
    # Delete all checkpoint files except the latest and best model
    Get-ChildItem "$phase2Dir\checkpoint_*.pth" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "   Deleting checkpoint: $($_.Name)"
        Remove-Item $_.FullName -Force
    }
    
    # Delete best_model.pth (keep only best_model_1901.pth)
    if (Test-Path "$phase2Dir\best_model.pth") {
        Write-Host "   Deleting: best_model.pth (keeping best_model_1901.pth)"
        Remove-Item "$phase2Dir\best_model.pth" -Force
    }
    
    Write-Host "   ✅ Phase 2 directory cleaned!"
    Write-Host "   ✅ Kept: best_model_1901.pth, config.json, vocab.json"
}

Write-Host ""

# =============================================================================
# SUMMARY
# =============================================================================
Write-Host ""
Write-Host "=" * 70
Write-Host "✅ CLEANUP COMPLETE!"
Write-Host "=" * 70
Write-Host ""

# Calculate sizes after cleanup
$afterSize = (Get-ChildItem "F:\CODE\tts-2" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
$saved = $beforeSize - $afterSize

Write-Host "📊 Disk Space Summary:"
Write-Host "   Before: $([math]::Round($beforeSize, 2)) GB"
Write-Host "   After:  $([math]::Round($afterSize, 2)) GB"
Write-Host "   Saved:  $([math]::Round($saved, 2)) GB"
Write-Host ""

Write-Host "Files Kept for Production:"
Write-Host "   - run\training_combined_phase2\...\best_model_1901.pth (Phase 2 best)"
Write-Host "   - run\training_combined_phase2\...\config.json"
Write-Host "   - run\training_combined_phase2\...\vocab.json"
Write-Host "   - scripts\generate_quiz_phase2.py (sample generation)"
Write-Host "   - scripts\inference.py (if exists)"
Write-Host "   - quiz_samples_phase2_final\ (15 generated samples)"
Write-Host "   - processed_clips\ (reference audio)"
Write-Host ""

Write-Host "Your project is now clean and production-ready!"
Write-Host ""
Write-Host ("=" * 70)
Write-Host ""
