"""
Monitor Combined Training Progress
Tracks Mel CE improvement and displays current status
"""
import os
import time
from pathlib import Path
import re

TRAINING_DIR = Path("run/training_combined")
LOG_FILE_PATTERN = "trainer_0_log.txt"

def find_latest_training():
    """Find the most recent training run"""
    if not TRAINING_DIR.exists():
        return None
    
    runs = list(TRAINING_DIR.glob("XTTS_Combined_*"))
    if not runs:
        return None
    
    return max(runs, key=lambda p: p.stat().st_mtime)

def parse_log_file(log_path):
    """Extract training metrics from log file"""
    if not log_path.exists():
        return None
    
    metrics = {
        "steps": [],
        "loss": [],
        "text_ce": [],
        "mel_ce": [],
        "eval_loss": []
    }
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Parse step information
    step_pattern = r"STEP:\s*(\d+)/\d+"
    loss_pattern = r"LOSS:\s*([\d.]+)"
    text_ce_pattern = r"text_ce:\s*([\d.]+)"
    mel_ce_pattern = r"mel_ce:\s*([\d.]+)"
    
    lines = content.split('\n')
    for line in lines:
        step_match = re.search(step_pattern, line)
        if step_match:
            step = int(step_match.group(1))
            metrics["steps"].append(step)
            
            loss_match = re.search(loss_pattern, line)
            if loss_match:
                metrics["loss"].append(float(loss_match.group(1)))
            
            text_ce_match = re.search(text_ce_pattern, line)
            if text_ce_match:
                metrics["text_ce"].append(float(text_ce_match.group(1)))
            
            mel_ce_match = re.search(mel_ce_pattern, line)
            if mel_ce_match:
                metrics["mel_ce"].append(float(mel_ce_match.group(1)))
    
    return metrics if metrics["steps"] else None

def display_progress():
    """Display current training progress"""
    print("=" * 70)
    print("🔍 COMBINED TRAINING MONITOR - MEL CE FOCUS")
    print("=" * 70)
    print()
    
    latest_run = find_latest_training()
    
    if not latest_run:
        print("❌ No training run found in run/training_combined/")
        print("   Make sure training has started.")
        return
    
    print(f"📁 Training run: {latest_run.name}")
    print()
    
    log_path = latest_run / LOG_FILE_PATTERN
    
    if not log_path.exists():
        print("⏳ Training started but no log file yet...")
        print("   Waiting for training to begin...")
        return
    
    metrics = parse_log_file(log_path)
    
    if not metrics or not metrics["steps"]:
        print("⏳ No training steps recorded yet...")
        return
    
    # Get latest values
    current_step = metrics["steps"][-1]
    current_loss = metrics["loss"][-1] if metrics["loss"] else None
    current_text_ce = metrics["text_ce"][-1] if metrics["text_ce"] else None
    current_mel_ce = metrics["mel_ce"][-1] if metrics["mel_ce"] else None
    
    print(f"📊 CURRENT STATUS:")
    print(f"   Step: {current_step}")
    if current_loss:
        print(f"   Loss: {current_loss:.4f}")
    if current_text_ce:
        print(f"   Text CE: {current_text_ce:.4f}")
    if current_mel_ce:
        print(f"   Mel CE: {current_mel_ce:.4f}")
    print()
    
    # Show Mel CE progress
    if current_mel_ce:
        initial_mel_ce = 5.046  # From Milliomos training
        target_mel_ce = 2.5
        
        improvement = initial_mel_ce - current_mel_ce
        remaining = current_mel_ce - target_mel_ce
        progress_pct = (improvement / (initial_mel_ce - target_mel_ce)) * 100
        
        print("🎯 MEL CE PROGRESS:")
        print(f"   Starting: {initial_mel_ce:.3f}")
        print(f"   Current:  {current_mel_ce:.3f} ({improvement:+.3f})")
        print(f"   Target:   {target_mel_ce:.3f}")
        print(f"   Remaining: {remaining:.3f}")
        print(f"   Progress: {progress_pct:.1f}% toward target")
        
        # Progress bar
        bar_length = 40
        filled = int((progress_pct / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"   [{bar}] {progress_pct:.1f}%")
        print()
        
        if current_mel_ce <= target_mel_ce:
            print("   ✅ TARGET REACHED! Excellent smoothness achieved!")
        elif current_mel_ce <= 3.0:
            print("   🟢 Very good progress! Getting close to target.")
        elif current_mel_ce <= 4.0:
            print("   🟡 Good progress! Keep training...")
        else:
            print("   🔵 Early stages. Improvement expected with more training.")
    
    print()
    
    # Recent history
    if len(metrics["mel_ce"]) > 1:
        print("📈 RECENT MEL CE HISTORY (last 10 steps):")
        recent_steps = metrics["steps"][-10:]
        recent_mel = metrics["mel_ce"][-10:]
        
        for step, mel in zip(recent_steps, recent_mel):
            print(f"   Step {step:4d}: {mel:.4f}")
        print()
    
    # Check for improvements
    if len(metrics["mel_ce"]) >= 2:
        initial = metrics["mel_ce"][0]
        current = metrics["mel_ce"][-1]
        change = current - initial
        
        if change < -0.5:
            print(f"   ✅ Great improvement: {change:.3f} from start!")
        elif change < -0.1:
            print(f"   🟢 Good improvement: {change:.3f} from start")
        elif change < 0:
            print(f"   🟡 Slight improvement: {change:.3f} from start")
        else:
            print(f"   🔵 Still warming up (early training)")
    
    print()
    print("=" * 70)
    print("💡 Tips:")
    print("   • Training takes ~30-40 minutes for 40 epochs")
    print("   • Mel CE should gradually decrease")
    print("   • Target: Mel CE < 2.5 for excellent quality")
    print("   • Run this script again to see updated progress")
    print("=" * 70)

if __name__ == "__main__":
    display_progress()
