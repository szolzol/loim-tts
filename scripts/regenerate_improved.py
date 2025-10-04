"""
Regenerate samples with improved parameters for natural Hungarian speech
Focus on fixing odd emphasis and punctuation issues
"""

import os
import sys
import torch
import torchaudio
from pathlib import Path

try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
except ImportError as e:
    print(f"❌ Error importing TTS: {e}")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_milliomos" / "XTTS_20251002_2323-October-02-2025_11+23PM-06571a9"
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"
OUTPUT_DIR = PROJECT_ROOT / "test_outputs_v2"

# Test phrases - focusing on problematic ones (2, 3, 5, 6, 7, 8, 9, 11, 12)
# Using multiple reference audios per category for variety
TEST_PHRASES = [
    # Samples that need improvement
    ("greeting", "Szeretettel köszöntöm nézőinket!", "greeting_002.wav"),  # #2 - Use different ref
    ("greeting", "Nagyszerű teljesítmény!", "greeting_003.wav"),  # #3 - Use different ref
    
    ("excitement", "Hihetetlen! Fantasztikus játék!", "excitement_002.wav"),  # #5 - Use different ref
    ("excitement", "Folytatja a győzelmi szériát!", "excitement_003.wav"),  # #6 - Use different ref
    
    ("question", "Jöjjön a következő kérdés!", "question_002.wav"),  # #7 - Use different ref
    ("question", "Melyik évben volt a mohácsi csata?", "question_003.wav"),  # #8 - Use different ref
    ("question", "Ki festette a Mona Lisát?", "question_004.wav"),  # #9 - Use different ref
    
    ("tension", "Gondolkodjon csak nyugodtan!", "tension_002.wav"),  # #11 - Use different ref
    ("tension", "Biztos benne?", "tension_003.wav"),  # #12 - Use different ref
    
    # Good samples for comparison (regenerate with same refs)
    ("greeting", "Gratulálok! Helyes válasz!", "greeting_001.wav"),  # #1 - Keep same
    ("excitement", "Ez már másfél millió forint!", "excitement_001.wav"),  # #4 - Keep same
    ("tension", "Ez egy nagyon nehéz kérdés.", "tension_001.wav"),  # #10 - Keep same
]

# Improved generation parameters for natural Hungarian
GENERATION_PARAMS = {
    # Lower temperature for more consistent/natural delivery
    "temperature": 0.65,  # Was 0.75, now more conservative
    
    # Adjust sampling for better quality
    "top_p": 0.90,  # Was 0.85, slightly higher for smoother flow
    "top_k": 40,    # Was 50, more focused
    
    # Penalties to avoid odd emphasis
    "repetition_penalty": 3.5,  # Was 5.0, less aggressive
    "length_penalty": 1.2,      # Slight preference for natural length
    
    # Speed/pacing
    "speed": 1.0,  # Normal speed
}


def load_model():
    """Load the trained model"""
    print("="*60)
    print("LOADING TRAINED MODEL")
    print("="*60)
    
    try:
        config = XttsConfig()
        config.load_json(str(MODEL_DIR / "config.json"))
        print("✓ Config loaded")
        
        model = Xtts.init_from_config(config)
        print("✓ Model initialized")
        
        model.load_checkpoint(
            config,
            checkpoint_dir=str(MODEL_DIR),
            checkpoint_path=str(MODEL_DIR / "best_model.pth"),
            eval=True,
            use_deepspeed=False
        )
        print("✓ Checkpoint loaded")
        
        if torch.cuda.is_available():
            model.cuda()
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
        
        model.eval()
        return model, config
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def generate_samples(model, config):
    """Generate improved samples"""
    print("\n" + "="*60)
    print("GENERATING IMPROVED SAMPLES")
    print("="*60)
    print(f"\n📝 Parameters:")
    print(f"   Temperature: {GENERATION_PARAMS['temperature']}")
    print(f"   Top-P: {GENERATION_PARAMS['top_p']}")
    print(f"   Top-K: {GENERATION_PARAMS['top_k']}")
    print(f"   Repetition Penalty: {GENERATION_PARAMS['repetition_penalty']}")
    print(f"   Length Penalty: {GENERATION_PARAMS['length_penalty']}")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    success = 0
    total = len(TEST_PHRASES)
    
    for i, (category, text, ref_audio_name) in enumerate(TEST_PHRASES, 1):
        ref_audio = str(DATASET_PATH / category / ref_audio_name)
        output_file = OUTPUT_DIR / f"{i:02d}_{category}_v2.wav"
        
        print(f"\n[{i}/{total}] {category.upper()}")
        print(f"Text: {text}")
        print(f"Ref: {ref_audio_name}")
        
        if not Path(ref_audio).exists():
            print(f"⚠️  Reference audio not found: {ref_audio}")
            continue
        
        try:
            # Get conditioning from reference
            gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
                audio_path=[ref_audio]
            )
            
            # Generate with improved parameters
            out = model.inference(
                text=text,
                language="hu",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                **GENERATION_PARAMS
            )
            
            # Save
            torchaudio.save(
                str(output_file),
                torch.tensor(out["wav"]).unsqueeze(0),
                24000
            )
            
            print(f"✅ Saved: {output_file.name}")
            success += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"✅ Generated: {success}/{total} samples")
    print(f"📁 Output: {OUTPUT_DIR}")
    
    if success > 0:
        print("\n🎧 Compare:")
        print(f"   v1 (original): {PROJECT_ROOT / 'test_outputs'}")
        print(f"   v2 (improved): {OUTPUT_DIR}")
        print("\n📊 Check for:")
        print("   - More natural emphasis")
        print("   - Better punctuation handling")
        print("   - Smoother flow")
        print("   - Consistent quiz show energy")


if __name__ == "__main__":
    print("="*60)
    print("IMPROVED SAMPLE GENERATION")
    print("István Vágó - Milliomos Quiz Show Voice")
    print("="*60)
    
    model, config = load_model()
    
    if model and config:
        generate_samples(model, config)
        print("\n✅ Done!")
    else:
        print("\n❌ Failed to load model")
        sys.exit(1)
