"""
Load trained XTTS model and generate quiz show samples
Handles trainer checkpoint format properly
"""

import os
import sys
import torch
import torchaudio
from pathlib import Path

# Add TTS to path
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
except ImportError as e:
    print(f"❌ Error importing TTS: {e}")
    print("Please install: pip install TTS==0.22.0")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_milliomos" / "XTTS_20251002_2323-October-02-2025_11+23PM-06571a9"
OUTPUT_DIR = PROJECT_ROOT / "test_outputs"
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"

# Reference audios for different styles
REFERENCE_AUDIOS = {
    "greeting": str(DATASET_PATH / "greeting" / "greeting_001.wav"),
    "excitement": str(DATASET_PATH / "excitement" / "excitement_001.wav"),
    "question": str(DATASET_PATH / "question" / "question_003.wav"),  # Updated after reclassification
    "tension": str(DATASET_PATH / "tension" / "tension_002.wav"),  # Updated after reclassification
}

# Test phrases from Milliomos show
TEST_PHRASES = [
    ("greeting", "Gratulálok! Helyes válasz!"),
    ("greeting", "Szeretettel köszöntöm nézőinket!"),
    ("greeting", "Nagyszerű teljesítmény!"),
    
    ("excitement", "Ez már másfél millió forint!"),
    ("excitement", "Hihetetlen! Fantasztikus játék!"),
    ("excitement", "Folytatja a győzelmi szériát!"),
    
    ("question", "Jöjjön a következő kérdés!"),
    ("question", "Melyik évben volt a mohácsi csata?"),
    ("question", "Ki festette a Mona Lisát?"),
    
    ("tension", "Ez egy nagyon nehéz kérdés."),
    ("tension", "Gondolkodjon csak nyugodtan!"),
    ("tension", "Biztos benne?"),
]


def load_trained_model():
    """Load the trained model from trainer checkpoint"""
    print("="*60)
    print("LOADING TRAINED MODEL")
    print("="*60)
    
    config_path = MODEL_DIR / "config.json"
    checkpoint_path = MODEL_DIR / "best_model.pth"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return None
    
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return None
    
    print(f"✓ Config: {config_path.name}")
    print(f"✓ Checkpoint: {checkpoint_path.name}")
    print(f"✓ Size: {checkpoint_path.stat().st_size / 1024**3:.2f} GB")
    
    try:
        # Load config
        print("\n📋 Loading configuration...")
        config = XttsConfig()
        config.load_json(str(config_path))
        
        # Initialize model  
        print("🤖 Initializing model...")
        model = Xtts.init_from_config(config)
        
        # Load checkpoint using model's built-in method
        # This properly initializes tokenizer and other components
        print("💾 Loading checkpoint...")
        model.load_checkpoint(
            config,
            checkpoint_dir=str(MODEL_DIR),
            checkpoint_path=str(checkpoint_path),
            eval=True,
            use_deepspeed=False
        )
        print("✓ Checkpoint loaded with tokenizer initialized")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            print("🎮 Moving model to GPU...")
            model.cuda()
            print("✓ Model on GPU")
        else:
            print("💻 Using CPU (will be slower)")
        
        model.eval()
        print("✓ Model loaded successfully!")
        
        return model, config
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_samples(model, config):
    """Generate test samples for all categories"""
    print("\n" + "="*60)
    print("GENERATING TEST SAMPLES")
    print("="*60)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    total_samples = len(TEST_PHRASES)
    success_count = 0
    
    for i, (category, text) in enumerate(TEST_PHRASES, 1):
        output_file = OUTPUT_DIR / f"{i:02d}_{category}.wav"
        ref_audio = REFERENCE_AUDIOS.get(category, REFERENCE_AUDIOS["greeting"])
        
        print(f"\n[{i}/{total_samples}] {category.upper()}")
        print(f"Text: {text}")
        print(f"Ref: {Path(ref_audio).name}")
        
        try:
            # Get conditioning latents from reference audio
            gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
                audio_path=[ref_audio]
            )
            
            # Generate speech using inference method
            out = model.inference(
                text=text,
                language="hu",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=0.75,  # Slightly creative
                top_p=0.85,
                top_k=50,
                repetition_penalty=5.0,
                length_penalty=1.0,
            )
            
            # Save audio
            torchaudio.save(
                str(output_file),
                torch.tensor(out["wav"]).unsqueeze(0),
                24000
            )
            
            print(f"✅ Saved: {output_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"✅ Generated: {success_count}/{total_samples} samples")
    print(f"📁 Output: {OUTPUT_DIR}")
    
    if success_count > 0:
        print("\n🎧 Listen to the samples!")
        print(f"   Generated: {OUTPUT_DIR}")
        print(f"   Originals: {DATASET_PATH}")
        print("\n📊 Compare:")
        print("   - Voice similarity to István Vágó")
        print("   - Quiz show energy and enthusiasm")
        print("   - Natural Hungarian pronunciation")
        print("   - Smoothness (no choppiness)")


def main():
    print("="*60)
    print("XTTS-V2 TRAINED MODEL TESTING")
    print("István Vágó - Milliomos Quiz Show Voice")
    print("="*60)
    
    # Load model
    result = load_trained_model()
    if result is None:
        print("\n❌ Failed to load model")
        sys.exit(1)
    
    model, config = result
    
    # Generate samples
    print("\n⏳ Starting generation (this may take a few minutes)...")
    generate_samples(model, config)
    
    print("\n✅ All done!")


if __name__ == "__main__":
    main()
