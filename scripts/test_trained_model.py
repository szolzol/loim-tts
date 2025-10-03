"""
Test the trained XTTS model with quiz show phrases
"""

import os
import sys
import torch
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_PATH = PROJECT_ROOT / "run" / "training_milliomos" / "XTTS_20251002_2323-October-02-2025_11+23PM-06571a9"
OUTPUT_DIR = PROJECT_ROOT / "test_outputs"
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"

# Reference audio for voice cloning
REFERENCE_AUDIOS = {
    "greeting": str(DATASET_PATH / "greeting" / "greeting_001.wav"),
    "excitement": str(DATASET_PATH / "excitement" / "excitement_001.wav"),
    "question": str(DATASET_PATH / "question" / "question_001.wav"),
    "tension": str(DATASET_PATH / "tension" / "tension_001.wav"),
}

# Test phrases from Milliomos show
TEST_PHRASES = {
    "greeting": [
        "Gratulálok! Helyes válasz!",
        "Szeretettel köszöntöm nézőinket!",
        "Nagyszerű teljesítmény!",
    ],
    "excitement": [
        "Ez már másfél millió forint!",
        "Hihetetlen! Folytatja a győzelmi szériát!",
        "Fantasztikus játék!",
    ],
    "question": [
        "Jöjjön a következő kérdés ötven ezer forintért!",
        "Melyik évben volt a mohácsi csata?",
        "Ki festette a Mona Lisát?",
    ],
    "tension": [
        "Ez egy nagyon nehéz kérdés.",
        "Gondolkodjon csak nyugodtan!",
        "Biztos benne?",
    ],
}


def load_model():
    """Load the trained XTTS model"""
    print("="*60)
    print("LOADING TRAINED MODEL")
    print("="*60)
    
    config_path = MODEL_PATH / "config.json"
    checkpoint_path = MODEL_PATH / "best_model.pth"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return None
    
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return None
    
    print(f"Config: {config_path}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Size: {checkpoint_path.stat().st_size / 1024**3:.2f} GB")
    
    # Load config
    config = XttsConfig()
    config.load_json(str(config_path))
    
    # Initialize model
    model = Xtts.init_from_config(config)
    
    # Load checkpoint directly
    print("Loading checkpoint...")
    checkpoint = torch.load(str(checkpoint_path), map_location="cpu")
    
    # Load model weights
    if "model" in checkpoint:
        model.load_state_dict(checkpoint["model"])
    else:
        model.load_state_dict(checkpoint)
    
    # Move to GPU if available
    if torch.cuda.is_available():
        model.cuda()
        print(f"✓ Model loaded on GPU")
    else:
        print(f"✓ Model loaded on CPU (will be slower)")
    
    model.eval()  # Set to evaluation mode
    
    return model, config


def generate_samples(model, config):
    """Generate test samples for all categories"""
    print("\n" + "="*60)
    print("GENERATING TEST SAMPLES")
    print("="*60)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    total_samples = 0
    
    for category, phrases in TEST_PHRASES.items():
        print(f"\n📁 Category: {category.upper()}")
        print("-" * 60)
        
        ref_audio = REFERENCE_AUDIOS.get(category, REFERENCE_AUDIOS["greeting"])
        print(f"Reference audio: {Path(ref_audio).name}")
        
        for i, text in enumerate(phrases, 1):
            output_file = OUTPUT_DIR / f"{category}_{i:02d}.wav"
            
            print(f"\n{i}. Generating: {text[:60]}...")
            print(f"   Output: {output_file.name}")
            
            try:
                # Generate speech
                outputs = model.synthesize(
                    text=text,
                    config=config,
                    speaker_wav=ref_audio,
                    language="hu",
                    gpt_cond_len=6,  # 6 seconds of reference
                    temperature=0.7,  # Slightly creative
                )
                
                # Save audio
                import torchaudio
                torchaudio.save(
                    str(output_file),
                    torch.tensor(outputs["wav"]).unsqueeze(0),
                    24000
                )
                
                print(f"   ✓ Saved: {output_file.name}")
                total_samples += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print(f"✓ Generated {total_samples} samples")
    print(f"✓ Saved to: {OUTPUT_DIR}")
    print("="*60)


def compare_with_original():
    """Show comparison instructions"""
    print("\n" + "="*60)
    print("COMPARISON GUIDE")
    print("="*60)
    print("\n📊 To evaluate the fine-tuned model:")
    print("\n1. Listen to generated samples:")
    print(f"   {OUTPUT_DIR}")
    print("\n2. Compare with original dataset:")
    print(f"   {DATASET_PATH}")
    print("\n3. Check for:")
    print("   ✓ Voice similarity (sounds like István Vágó)")
    print("   ✓ Quiz show energy and enthusiasm")
    print("   ✓ Natural intonation (questions rise, excitement peaks)")
    print("   ✓ Smooth audio (no choppiness)")
    print("   ✓ Clear pronunciation of Hungarian")
    print("\n4. Expected improvements over zero-shot:")
    print("   ✓ More consistent voice character")
    print("   ✓ Better quiz show prosody")
    print("   ✓ Smoother, less robotic delivery")
    print("   ✓ More natural Hungarian pronunciation")


def main():
    print("="*60)
    print("XTTS-V2 TRAINED MODEL TESTING")
    print("István Vágó - Milliomos Quiz Show Voice")
    print("="*60)
    
    # Load model
    result = load_model()
    if result is None:
        print("\n❌ Failed to load model")
        sys.exit(1)
    
    model, config = result
    
    # Generate samples
    generate_samples(model, config)
    
    # Show comparison guide
    compare_with_original()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
