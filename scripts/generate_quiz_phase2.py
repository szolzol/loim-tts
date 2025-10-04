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

# Paths - PHASE 2 BEST MODEL
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_combined_phase2" / "XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd"
OUTPUT_DIR = PROJECT_ROOT / "quiz_samples_phase2_final"

# Reference audio (use neutral reference from dataset)
REFERENCE_AUDIO = "dataset_combined/neutral/neutral_002.wav"

# Quiz show phrases - 5 complete questions with A/B/C/D options (with longer pauses between answers)
TEST_PHRASES = [
    ("q1_geography", "Melyik ország fővárosa Budapest? Magyarország... Románia... Ausztria... vagy Szlovákia."),
    ("q2_history", "Melyik évben fedezte fel Kolumbusz Amerikát? Ezernégyszázkilencvenkettő... ezernégyszáznyolcvannyolc... ezernégyszázhetvenhat... vagy ezernégyszázkilencvenhat."),
    ("q3_science", "Hány proton van egy hidrogén atom magjában? Egy proton... kettő proton... három proton... vagy négy proton."),
    ("q4_literature", "Ki írta a Rómeó és Júliát? William Shakespeare... Charles Dickens... Victor Hugo... vagy Mark Twain."),
    ("q5_sports", "Hány játékos játszik egy futballcsapatban egyszerre? Kilenc játékos... tíz játékos... tizenegy játékos... vagy tizenkettő játékos."),
]


def load_trained_model():
    """Load the trained model from trainer checkpoint"""
    print("="*60)
    print("LOADING TRAINED MODEL")
    print("="*60)
    
    config_path = MODEL_DIR / "config.json"
    checkpoint_path = MODEL_DIR / "best_model_1901.pth"  # Phase 2 best model (Mel CE: 2.971)
    
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
        vocab_path = MODEL_DIR / "vocab.json"
        if not vocab_path.exists():
            print(f"❌ Vocab file not found: {vocab_path}")
            return None
        
        model.load_checkpoint(
            config,
            checkpoint_dir=str(MODEL_DIR),
            checkpoint_path=str(checkpoint_path),
            vocab_path=str(vocab_path),  # CRITICAL: needed for tokenizer
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
        ref_audio = REFERENCE_AUDIO  # Use single high-quality reference
        
        print(f"\n[{i}/{total_samples}] {category.upper()}")
        print(f"Text: {text}")
        print(f"Ref: {Path(ref_audio).name}")
        
        try:
            # Get conditioning latents from reference audio
            gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
                audio_path=[ref_audio]
            )
            
            # Extremely low temperature for maximum stability
            # 0.40 = ultra stable, perfectly even delivery
            temperature = 0.40
            
            char_count = len(text)
            print(f"Length: {char_count} chars → temp={temperature}")
            
            # Generate speech using inference method
            out = model.inference(
                text=text,
                language="hu",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=temperature,  # Ultra low temp for maximum stability
                top_p=0.80,  # Lower for more predictability
                top_k=40,    # Lower for less variation
                repetition_penalty=6.0,  # Higher to prevent emphasis spikes
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
        print(f"\n🎯 Phase 2 Model: best_model_1901.pth (Mel CE: 2.971, -41.1% improvement)")
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
