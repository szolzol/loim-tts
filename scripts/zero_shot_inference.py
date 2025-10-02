"""
István Vágó Voice - Zero-Shot Inference
Generate speech WITHOUT fine-tuning using pre-trained XTTS-v2
Just needs 6-10 seconds of reference audio!
"""

import os
import sys
import torch
import torchaudio
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("  István Vágó Voice - Zero-Shot Inference")
print("  Using Pre-trained XTTS-v2 (No Training Required!)")
print("=" * 70)
print()

# Check TTS installation
try:
    from TTS.api import TTS
except ImportError:
    print("❌ Error: TTS not installed")
    print("Installing TTS...")
    os.system("pip install TTS==0.22.0")
    from TTS.api import TTS

# Configuration
PROJECT_ROOT = Path("f:/CODE/tts-2")
SOURCE_CLIPS_DIR = PROJECT_ROOT / "source_clips"
OUTPUT_DIR = PROJECT_ROOT / "output" / "zero_shot"

# Reference audio files (use 2-3 for best results)
# Using most energetic/expressive clips for better prosody
REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",  # Most energetic
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",  # High expression
    SOURCE_CLIPS_DIR / "vago_vagott_03.wav",  # Dynamic delivery
]

LANGUAGE = "hu"  # Hungarian

# Inference settings - OPTIMIZED FOR SMOOTHER SPEECH
# Reducing temperature and adjusting settings for less choppy output
TEMPERATURE = 0.7  # Lower = more stable/smooth (was 0.95)
LENGTH_PENALTY = 1.0
REPETITION_PENALTY = 5.0  # Lower = smoother flow (was 7.0)
SPEED = 1.0  # Normal speed for natural flow
TOP_K = 50  # Limit vocabulary for more stable output
TOP_P = 0.85  # Nucleus sampling for smoother generation

# Test phrases in Hungarian (quiz show style)
TEST_PHRASES = [
    "Üdvözlöm önöket a mai kvízműsorban! Készen állnak a kérdésekre?",
    "Ez egy rendkívül érdekes kérdés lesz. Figyeljünk együtt!",
    "Gratulálok a helyes válaszhoz! Fantasztikus teljesítmény volt.",
    "Sajnos ez nem a jó válasz. De ne adjanak fel, jön a következő kérdés!",
    "Az idő múlik, dönteniük kell hamarosan. Mit válaszolnak?",
    "Lássuk a helyes választ! Vajon eltalálták?",
    "Köszönöm szépen a mai játékot! Találkozunk a következő adásban!",
    "Most egy nehezebb kérdés következik. Gondolkodjanak csak!",
    "Izgalmas pillanathoz érkeztünk. Ki fog nyerni ma este?",
    "Remek játék volt! Minden játékosnak gratulálok!",
]


def check_reference_audio():
    """Check if reference audio files exist"""
    
    print("🎤 Checking reference audio...")
    
    available_refs = []
    for ref_path in REFERENCE_AUDIO:
        if ref_path.exists():
            print(f"  ✅ Found: {ref_path.name}")
            available_refs.append(str(ref_path))
        else:
            print(f"  ⚠️ Missing: {ref_path.name}")
    
    if not available_refs:
        print("\n❌ No reference audio found!")
        print(f"Expected location: {SOURCE_CLIPS_DIR}")
        
        # Show what's actually there
        if SOURCE_CLIPS_DIR.exists():
            print("\nAvailable files:")
            for f in SOURCE_CLIPS_DIR.glob("*.wav"):
                print(f"  - {f.name}")
        
        return None
    
    print(f"  ✅ Using {len(available_refs)} reference files")
    return available_refs


def load_model():
    """Load pre-trained XTTS-v2 model"""
    
    print("\n🤖 Loading XTTS-v2 model...")
    print("  (This will download ~2GB on first run)")
    
    try:
        # Initialize TTS with XTTS-v2 multilingual model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  ℹ️ Using device: {device}")
        
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("  ✅ Model loaded successfully!")
        
        return tts
        
    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_speech(tts, text, speaker_wav, output_path):
    """
    Generate speech with zero-shot voice cloning
    
    Args:
        tts: TTS model
        text: Hungarian text to synthesize
        speaker_wav: Reference audio file(s)
        output_path: Where to save output
    """
    
    try:
        import time
        start_time = time.time()
        
        # Generate speech with optimized parameters for smooth output
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=LANGUAGE,
            file_path=str(output_path),
            # Optimized settings for smooth, natural flow
            temperature=TEMPERATURE,
            length_penalty=LENGTH_PENALTY,
            repetition_penalty=REPETITION_PENALTY,
            speed=SPEED,
            top_k=TOP_K,
            top_p=TOP_P,
        )
        
        # Calculate generation time
        elapsed = time.time() - start_time
        
        # Get audio duration
        try:
            import torchaudio
            waveform, sample_rate = torchaudio.load(str(output_path))
            duration = waveform.shape[1] / sample_rate
            rtf = elapsed / duration  # Real-time factor
            print(f"  ⏱️ Generated in {elapsed:.2f}s (RTF: {rtf:.2f}x)")
        except:
            print(f"  ⏱️ Generated in {elapsed:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_test_samples(tts, speaker_wav):
    """Generate test quiz show phrases"""
    
    print("\n🎬 Generating quiz show samples...")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    successful = 0
    failed = 0
    
    for i, phrase in enumerate(TEST_PHRASES, 1):
        print(f"\n[{i}/{len(TEST_PHRASES)}] Generating...")
        print(f"  Text: {phrase[:60]}...")
        
        output_filename = f"quiz_{i:02d}_{timestamp}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        success = generate_speech(tts, phrase, speaker_wav, output_path)
        
        if success:
            print(f"  ✅ Saved: {output_filename}")
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Generation complete: {successful} successful, {failed} failed")
    print(f"📁 Saved to: {OUTPUT_DIR}")
    
    return successful > 0


def interactive_mode(tts, speaker_wav):
    """Interactive text-to-speech mode"""
    
    print("\n" + "=" * 70)
    print("🎤 Interactive Mode - Zero-Shot Voice Cloning")
    print("=" * 70)
    print("Enter Hungarian text to synthesize (or 'quit' to exit)")
    print()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        text = input("📝 Hungarian text: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("Exiting...")
            break
        
        if not text:
            print("  ⚠️ Please enter some text")
            continue
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"custom_{timestamp}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        print(f"  🔊 Generating: {text[:60]}...")
        
        success = generate_speech(tts, text, speaker_wav, output_path)
        
        if success:
            print(f"  ✅ Saved: {output_filename}")
        else:
            print(f"  ❌ Failed to generate")


def main():
    """Main zero-shot inference pipeline"""
    
    # Check GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"🖥️ GPU: {gpu_name}")
    else:
        print("⚠️ No GPU detected - running on CPU (slower)")
    
    # Check reference audio
    speaker_wav = check_reference_audio()
    if speaker_wav is None:
        return
    
    # Load model
    tts = load_model()
    if tts is None:
        return
    
    # Menu
    print("\n" + "=" * 70)
    print("What would you like to do?")
    print("  1. Generate quiz show samples (10 phrases)")
    print("  2. Interactive mode (enter custom text)")
    print("  3. Both")
    print("=" * 70)
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "1":
        generate_test_samples(tts, speaker_wav)
    elif choice == "2":
        interactive_mode(tts, speaker_wav)
    elif choice == "3":
        generate_test_samples(tts, speaker_wav)
        interactive_mode(tts, speaker_wav)
    else:
        print("Invalid choice")
        return
    
    print("\n" + "=" * 70)
    print("✅ Zero-shot inference complete!")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\n💡 Tips:")
    print("  - Listen to the generated audio")
    print("  - If quality is good, you can use this without training!")
    print("  - If quality needs improvement, consider fine-tuning")
    print("  - Use 2-3 diverse reference clips for best results")


if __name__ == "__main__":
    main()
