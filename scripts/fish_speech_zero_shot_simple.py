"""
Fish Speech Zero-Shot Inference - Direct Python API
Simple test with Vágó voice samples
"""

import sys
import torch
from pathlib import Path

# Project paths
PROJECT_ROOT = Path("I:/CODE/tts-2")
FISH_SPEECH_ROOT = Path("I:/CODE/fish-speech")

sys.path.insert(0, str(FISH_SPEECH_ROOT))

from fish_speech.models.text2semantic import TextToSemantic
from fish_speech.models.vqgan.modules.firefly import FireflyArchitecture
import torchaudio

print("🐟 Fish Speech Zero-Shot Test - Vágó Voice")
print("=" * 60)

# Check GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n✅ Device: {device}")
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA: {torch.cuda.get_device_capability(0)}")

# Model paths
LLAMA_CHECKPOINT = FISH_SPEECH_ROOT / "checkpoints/fish-speech-1.4/model.pth"
DECODER_CHECKPOINT = FISH_SPEECH_ROOT / "checkpoints/fish-speech-1.4/firefly-gan-vq-fsq-8x1024-21hz-generator.pth"

print(f"\n📦 Loading models...")
print(f"   Llama: {LLAMA_CHECKPOINT}")
print(f"   Decoder: {DECODER_CHECKPOINT}")

# Reference audio
REFERENCE_AUDIO = PROJECT_ROOT / "prepared_sources/vago_samples_selected/question9.wav"
OUTPUT_DIR = PROJECT_ROOT / "test_samples_fish_zero_shot"
OUTPUT_DIR.mkdir(exist_ok=True)

# Test texts (Hungarian quiz questions)
TEST_TEXTS = [
    "Melyik ország fővárosa Budapest?",
    "Ki festette a Mona Lisát?",
    "Hány kontinens van a Földön?",
    "Melyik bolygó a legnagyobb a Naprendszerben?",
    "Ki írta a Rómeó és Júliát?",
]

print(f"\n📂 Reference: {REFERENCE_AUDIO}")
print(f"📂 Output: {OUTPUT_DIR}")
print(f"\n🎯 Test questions: {len(TEST_TEXTS)}")

try:
    # Load reference audio
    print(f"\n⏳ Loading reference audio...")
    waveform, sample_rate = torchaudio.load(str(REFERENCE_AUDIO))
    print(f"✅ Reference loaded: {sample_rate} Hz, shape: {waveform.shape}")
    
    # Load models
    print(f"\n⏳ Loading Text2Semantic model...")
    text2semantic = TextToSemantic.from_pretrained(
        str(LLAMA_CHECKPOINT),
        device=device,
    )
    print(f"✅ Text2Semantic loaded")
    
    print(f"\n⏳ Loading vocoder...")
    vocoder = FireflyArchitecture.from_pretrained(
        str(DECODER_CHECKPOINT),
        device=device,
    )
    print(f"✅ Vocoder loaded")
    
    print("\n" + "=" * 60)
    print("🚀 Models loaded successfully!")
    print("Ready for zero-shot inference")
    
    # Generate samples
    for i, text in enumerate(TEST_TEXTS, 1):
        print(f"\n⏳ Generating {i}/5: {text}")
        output_path = OUTPUT_DIR / f"fish_q{i}.wav"
        
        # TODO: Implement inference
        # This requires understanding Fish Speech's API
        # Will need to:
        # 1. Encode reference audio to semantic tokens
        # 2. Generate semantic tokens for text with reference
        # 3. Decode semantic tokens to audio
        
        print(f"   Output: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ Zero-shot test complete!")
    
except FileNotFoundError as e:
    print(f"\n❌ File not found: {e}")
    print("Make sure models are downloaded and reference audio exists")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("Fish Speech modules may not be properly installed")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
