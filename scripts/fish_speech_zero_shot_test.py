"""
Fish Speech Zero-Shot Test Script
Tests Fish Speech TTS on Vágó question samples without fine-tuning
"""

import sys
from pathlib import Path
import torch

# Add fish-speech to path
sys.path.insert(0, str(Path("I:/CODE/fish-speech")))

print("🐟 Fish Speech Zero-Shot Test - Vágó Voice")
print("=" * 60)

# Check GPU availability
print(f"\n✅ CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA Capability: {torch.cuda.get_device_capability(0)}")

# Test samples - Question samples from vago_samples_selected
PROJECT_ROOT = Path("I:/CODE/tts-2")
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

print(f"\n📂 Reference Audio: {REFERENCE_AUDIO}")
print(f"📂 Output Directory: {OUTPUT_DIR}")
print(f"\n🎯 Test Questions: {len(TEST_TEXTS)}")

try:
    print("\n⏳ Loading Fish Speech model...")
    from fish_speech.models.text2semantic import Text2Semantic
    from fish_speech.models.vqgan import VQGAN
    
    print("✅ Fish Speech modules imported successfully!")
    print("\n🚀 Ready for zero-shot testing")
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Download Fish Speech pretrained models")
    print("2. Run inference with reference audio")
    print("3. Compare output quality with XTTS-v2")
    
except ImportError as e:
    print(f"\n⚠️ Import error: {e}")
    print("Fish Speech installation may still be in progress...")
    print("Run this script again after installation completes.")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
