"""
Generate test samples from the trained model using TTS CLI
Much simpler than direct model loading - works with trainer checkpoints
"""

import subprocess
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_milliomos" / "XTTS_20251002_2323-October-02-2025_11+23PM-06571a9"
OUTPUT_DIR = PROJECT_ROOT / "test_outputs_cli"
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"

# Reference audio
REF_AUDIO = str(DATASET_PATH / "greeting" / "greeting_001.wav")

# Test phrases from show
TEST_PHRASES = [
    ("greeting_1", "Gratulálok! Helyes válasz!"),
    ("greeting_2", "Szeretettel köszöntöm nézőinket!"),
    ("excitement_1", "Ez már másfél millió forint!"),
    ("excitement_2", "Hihetetlen! Fantasztikus játék!"),
    ("question_1", "Jöjjön a következő kérdés!"),
    ("question_2", "Melyik évben volt a mohácsi csata?"),
    ("tension_1", "Ez egy nagyon nehéz kérdés."),
    ("tension_2", "Biztos benne?"),
]

def main():
    print("="*60)
    print("TESTING TRAINED MODEL WITH TTS CLI")
    print("="*60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print(f"\nModel: {MODEL_DIR.name}")
    print(f"Reference audio: {Path(REF_AUDIO).name}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"\nGenerating {len(TEST_PHRASES)} samples...")
    
    success_count = 0
    
    for filename, text in TEST_PHRASES:
        output_file = OUTPUT_DIR / f"{filename}.wav"
        
        print(f"\n{'='*60}")
        print(f"Generating: {filename}")
        print(f"Text: {text}")
        print(f"{'='*60}")
        
        try:
            # Use tts command with model path
            cmd = [
                "tts",
                "--text", text,
                "--model_path", str(MODEL_DIR),
                "--config_path", str(MODEL_DIR / "config.json"),
                "--speaker_wav", REF_AUDIO,
                "--language_idx", "hu",
                "--out_path", str(output_file)
            ]
            
            print(f"Running: tts --text \"{text[:40]}...\" ...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0 and output_file.exists():
                print(f"✅ Success: {output_file.name}")
                success_count += 1
            else:
                print(f"❌ Failed: {result.stderr[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Generated: {success_count}/{len(TEST_PHRASES)} samples")
    print(f"📁 Output folder: {OUTPUT_DIR}")
    
    if success_count > 0:
        print("\n🎧 Listen to the samples and compare with originals!")
        print(f"   Generated: {OUTPUT_DIR}")
        print(f"   Originals: {DATASET_PATH}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
