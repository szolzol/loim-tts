"""
Cleanup Old Checkpoint Files
Removes all checkpoint files except the best model to save disk space
"""

import os
import shutil
from pathlib import Path

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
TRAINING_DIR = PROJECT_ROOT / "run" / "training_combined"

def cleanup_checkpoints():
    """Remove all checkpoints except best_model.pth"""
    
    if not TRAINING_DIR.exists():
        print("❌ Training directory not found")
        return
    
    # Find the latest training run
    runs = sorted(TRAINING_DIR.glob("XTTS_Combined_*"))
    if not runs:
        print("❌ No training runs found")
        return
    
    latest_run = runs[-1]
    print(f"📁 Checking: {latest_run.name}")
    
    # Find all checkpoint files
    checkpoints = list(latest_run.glob("checkpoint_*.pth"))
    best_models = list(latest_run.glob("best_model*.pth"))
    
    total_size_before = 0
    total_size_after = 0
    deleted_count = 0
    
    # Calculate current size
    for f in checkpoints + best_models:
        total_size_before += f.stat().st_size
    
    # Keep only the best model
    for checkpoint in checkpoints:
        size = checkpoint.stat().st_size
        print(f"  🗑️  Deleting: {checkpoint.name} ({size / (1024**3):.2f} GB)")
        checkpoint.unlink()
        deleted_count += 1
    
    # Keep only the latest best model if there are multiple
    if len(best_models) > 1:
        best_models_sorted = sorted(best_models, key=lambda x: x.stat().st_mtime)
        for old_best in best_models_sorted[:-1]:
            size = old_best.stat().st_size
            print(f"  🗑️  Deleting old best: {old_best.name} ({size / (1024**3):.2f} GB)")
            old_best.unlink()
            deleted_count += 1
    
    # Calculate remaining size
    for f in latest_run.glob("*.pth"):
        total_size_after += f.stat().st_size
    
    freed = total_size_before - total_size_after
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted: {deleted_count} files")
    print(f"   Freed: {freed / (1024**3):.2f} GB")
    print(f"   Before: {total_size_before / (1024**3):.2f} GB")
    print(f"   After: {total_size_after / (1024**3):.2f} GB")

if __name__ == "__main__":
    cleanup_checkpoints()
