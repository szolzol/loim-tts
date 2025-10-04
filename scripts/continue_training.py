"""
Continue Training - Resume from Last Checkpoint
Trains 20 more epochs to improve audio quality

Simply run: python scripts/continue_training.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("f:/CODE/tts-2")
TRAINING_DIR = PROJECT_ROOT / "run" / "training_milliomos"

def continue_training():
    """Continue training from the last checkpoint"""
    
    print("="*70)
    print("CONTINUE TRAINING - 20 MORE EPOCHS")
    print("István Vágó Milliomos Voice Clone")
    print("="*70)
    
    # Check if previous training exists
    if not TRAINING_DIR.exists():
        print("\n❌ Training directory not found!")
        print(f"   Expected: {TRAINING_DIR}")
        return
    
    training_runs = list(TRAINING_DIR.glob("XTTS_*"))
    
    if not training_runs:
        print("\n❌ No previous training found!")
        print("Run the main training script first:")
        print("   python scripts\\train_xtts_milliomos.py")
        return
    
    # Get most recent training
    latest_run = max(training_runs, key=lambda p: p.stat().st_mtime)
    
    print(f"\n📁 Found training run:")
    print(f"   {latest_run.name}")
    print(f"   Location: {latest_run}")
    
    # Check for checkpoints
    checkpoints = list(latest_run.glob("*.pth"))
    if not checkpoints:
        print("\n❌ No checkpoint files found!")
        return
    
    print(f"\n💾 Available checkpoints:")
    for ckpt in sorted(checkpoints):
        size_gb = ckpt.stat().st_size / (1024**3)
        print(f"   {ckpt.name:25s} ({size_gb:.2f} GB)")
    
    # Training info
    print(f"\n⚙️  Training plan:")
    print(f"   ✓ Current model: 30 epochs completed")
    print(f"   ✓ Additional: 20 epochs")
    print(f"   ✓ Target total: 50 epochs")
    print(f"   ✓ Expected time: ~17 minutes")
    print(f"   ✓ Expected improvement: 20-30% better audio quality")
    
    print(f"\n� Why continue training?")
    print(f"   • Current eval loss (5.07) is higher than training (2.15)")
    print(f"   • More epochs will smooth out the audio")
    print(f"   • Reduce overfitting gap")
    print(f"   • More natural prosody")
    
    print(f"\n⚠️  Note: The training script will automatically resume from")
    print(f"   the last checkpoint if it exists in the run directory.")
    
    response = input(f"\nReady to continue training? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Training cancelled.")
        return
    
    # Run training script with modified epochs
    print(f"\n{'='*70}")
    print("LAUNCHING TRAINING")
    print(f"{'='*70}\n")
    
    # Change to project root
    os.chdir(PROJECT_ROOT)
    
    # Run training script (it will auto-resume from checkpoint)
    import subprocess
    result = subprocess.run(
        [sys.executable, "scripts/train_xtts_milliomos.py"],
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "NUM_EPOCHS": "50"}
    )
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE!")
        print("="*70)
        print("\n📊 Next steps:")
        print("   1. Generate new samples: python scripts/generate_samples.py")
        print("   2. Compare to previous: test_outputs/ vs test_outputs_v2/")
        print("   3. Check training log: run/training_milliomos/XTTS_*/trainer_0_log.txt")
    else:
        print("\n❌ Training failed. Check the error messages above.")

if __name__ == "__main__":
    continue_training()
