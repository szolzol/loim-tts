"""
István Vágó Voice - Inference Script
Generate high-quality quiz show audio using fine-tuned XTTS-v2 model
"""

import os
import sys
import torch
import torchaudio
from pathlib import Path
from datetime import datetime

try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
except ImportError as e:
    print(f"❌ Error importing TTS: {e}")
    print("Please ensure TTS is installed: pip install TTS==0.22.0")
    sys.exit(1)

# ========================================
# CONFIGURATION
# ========================================

PROJECT_ROOT = Path("f:/CODE/tts-2")

# Model paths (adjust after training)
CHECKPOINT_DIR = PROJECT_ROOT / "run" / "training" / "best_model"
CONFIG_FILE = CHECKPOINT_DIR / "config.json"

# Reference audio for voice cloning
REFERENCE_AUDIO = [
    str(PROJECT_ROOT / "dataset" / "wavs" / "1_vago_finetune2.wav"),
    str(PROJECT_ROOT / "dataset" / "wavs" / "2_vago_finetune2.wav"),
]

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "output" / "generated"

# Inference settings (for maximum quality)
TEMPERATURE = 0.75  # Lower = more consistent, Higher = more expressive
TOP_P = 0.85  # Nucleus sampling parameter
TOP_K = 50  # Top-k sampling parameter
REPETITION_PENALTY = 5.0  # Prevent repetition
LENGTH_PENALTY = 1.0  # Control output length

LANGUAGE = "hu"  # Hungarian


def check_model_files():
    """Check if model files exist"""
    
    if not CHECKPOINT_DIR.exists():
        print(f"❌ Checkpoint directory not found: {CHECKPOINT_DIR}")
        print("\n📝 Available training runs:")
        
        training_dir = PROJECT_ROOT / "run" / "training"
        if training_dir.exists():
            for run_dir in training_dir.iterdir():
                if run_dir.is_dir() and not run_dir.name.startswith("XTTS_v2"):
                    print(f"  - {run_dir.name}")
        
        return False
    
    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return False
    
    # Check for .pth files
    pth_files = list(CHECKPOINT_DIR.glob("*.pth"))
    if not pth_files:
        print(f"❌ No model checkpoint (.pth) files found in: {CHECKPOINT_DIR}")
        return False
    
    print(f"✅ Found model checkpoint: {pth_files[0].name}")
    return True


def check_reference_audio():
    """Check if reference audio files exist"""
    
    for ref in REFERENCE_AUDIO:
        ref_path = Path(ref)
        if not ref_path.exists():
            print(f"⚠️ Reference audio not found: {ref}")
            return False
    
    print(f"✅ Found {len(REFERENCE_AUDIO)} reference audio files")
    return True


def load_model():
    """Load the fine-tuned XTTS model"""
    
    print("\n🤖 Loading XTTS model...")
    
    try:
        # Load config
        config = XttsConfig()
        config.load_json(str(CONFIG_FILE))
        print("  ✅ Config loaded")
        
        # Initialize model
        model = Xtts.init_from_config(config)
        print("  ✅ Model initialized")
        
        # Load checkpoint
        model.load_checkpoint(
            config, 
            checkpoint_dir=str(CHECKPOINT_DIR),
            use_deepspeed=False  # Not using DeepSpeed for inference
        )
        print("  ✅ Checkpoint loaded")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            model.cuda()
            print(f"  ✅ Model moved to GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("  ⚠️ Running on CPU (will be slower)")
        
        return model
        
    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None


def compute_speaker_latents(model):
    """Compute speaker conditioning latents from reference audio"""
    
    print("\n🎙️ Computing speaker latents...")
    
    try:
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=REFERENCE_AUDIO
        )
        print("  ✅ Speaker latents computed")
        return gpt_cond_latent, speaker_embedding
        
    except Exception as e:
        print(f"  ❌ Error computing latents: {e}")
        return None, None


def synthesize_speech(model, text, gpt_cond_latent, speaker_embedding, output_path):
    """
    Synthesize speech with quality-focused parameters
    
    Args:
        model: Loaded XTTS model
        text: Hungarian text to synthesize
        gpt_cond_latent: Conditioning latent from reference audio
        speaker_embedding: Speaker embedding from reference audio
        output_path: Path to save output WAV file
    """
    
    print(f"\n🔊 Synthesizing: '{text[:50]}...'")
    
    try:
        # Run inference
        out = model.inference(
            text=text,
            language=LANGUAGE,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            repetition_penalty=REPETITION_PENALTY,
            length_penalty=LENGTH_PENALTY,
        )
        
        # Save audio
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        torchaudio.save(
            str(output_path),
            torch.tensor(out["wav"]).unsqueeze(0),
            24000  # Output sample rate
        )
        
        print(f"  ✅ Saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error during synthesis: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_quiz_samples(model, gpt_cond_latent, speaker_embedding):
    """Generate sample quiz show phrases"""
    
    print("\n🎬 Generating quiz show samples...")
    
    # Sample quiz show phrases in Hungarian
    quiz_phrases = [
        "Üdvözlöm önöket a mai kvízműsorban! Készek vagyunk?",
        "Első kérdésünk következik. Figyelem, indul az idő!",
        "Gratulálok! Ez a helyes válasz volt.",
        "Sajnos ez nem volt jó válasz. De ne adjuk fel!",
        "Izgalmas pillanathoz érkeztünk. Ki fogja megnyerni a főnyereményt?",
        "Köszönöm szépen a játékot! Találkozunk a következő adásban!",
        "Ez egy rendkívül nehéz kérdés lesz. Gondolkodjanak csak!",
        "Fantasztikus teljesítmény! Így tovább!",
        "Az idő múlik, dönteniük kell hamarosan.",
        "Lássuk a helyes választ! Mit gondolnak, jó lesz?",
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    successful = 0
    failed = 0
    
    for i, phrase in enumerate(quiz_phrases, 1):
        output_filename = f"quiz_sample_{i:02d}_{timestamp}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        success = synthesize_speech(
            model, phrase, gpt_cond_latent, speaker_embedding, output_path
        )
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Generation complete: {successful} successful, {failed} failed")
    return successful > 0


def interactive_mode(model, gpt_cond_latent, speaker_embedding):
    """Interactive text-to-speech mode"""
    
    print("\n" + "=" * 60)
    print("🎤 Interactive Mode")
    print("=" * 60)
    print("Enter Hungarian text to synthesize (or 'quit' to exit)")
    print()
    
    while True:
        text = input("📝 Text: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("Exiting interactive mode...")
            break
        
        if not text:
            print("  ⚠️ Please enter some text")
            continue
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"custom_{timestamp}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        synthesize_speech(model, text, gpt_cond_latent, speaker_embedding, output_path)


def main():
    """Main inference pipeline"""
    
    print("=" * 60)
    print("  István Vágó Voice - XTTS-v2 Inference")
    print("=" * 60)
    
    # Check files
    if not check_model_files():
        print("\n❌ Model files not found. Please train the model first.")
        return
    
    if not check_reference_audio():
        print("\n⚠️ Reference audio not found. Using default...")
    
    # Load model
    model = load_model()
    if model is None:
        print("\n❌ Failed to load model")
        return
    
    # Compute speaker latents
    gpt_cond_latent, speaker_embedding = compute_speaker_latents(model)
    if gpt_cond_latent is None:
        print("\n❌ Failed to compute speaker latents")
        return
    
    # Menu
    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("  1. Generate quiz show samples")
    print("  2. Interactive mode (enter custom text)")
    print("  3. Both")
    print("=" * 60)
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "1":
        generate_quiz_samples(model, gpt_cond_latent, speaker_embedding)
    elif choice == "2":
        interactive_mode(model, gpt_cond_latent, speaker_embedding)
    elif choice == "3":
        generate_quiz_samples(model, gpt_cond_latent, speaker_embedding)
        interactive_mode(model, gpt_cond_latent, speaker_embedding)
    else:
        print("Invalid choice")
        return
    
    print("\n" + "=" * 60)
    print("✅ Inference complete!")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
