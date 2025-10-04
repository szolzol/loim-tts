"""
Generate the entire quiz show audio from a transcript using XTTS-v2
Input: full_milliomos_vago_source_v1_hun.txt
Output: output_quiz_show/quiz_show_001.wav, quiz_show_002.wav, ...
"""

import os
from pathlib import Path
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_milliomos" / "XTTS_20251002_2323-October-02-2025_11+23PM-06571a9"
INPUT_FILE = PROJECT_ROOT / "source_text" / "full_milliomos_vago_source_v1_hun.txt"
OUTPUT_DIR = PROJECT_ROOT / "output_quiz_show"
REFERENCE_AUDIO = PROJECT_ROOT / "dataset_milliomos" / "greeting" / "greeting_001.wav"  # Use greeting style for all

# XTTS segment limit
MAX_CHARS = 224

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Load model
print("Loading XTTS-v2 model...")
config_path = MODEL_DIR / "config.json"
checkpoint_path = MODEL_DIR / "best_model.pth"
config = XttsConfig()
config.load_json(str(config_path))
model = Xtts.init_from_config(config)
model.load_checkpoint(
    config,
    checkpoint_dir=str(MODEL_DIR),
    checkpoint_path=str(checkpoint_path),
    eval=True,
    use_deepspeed=False
)
if torch.cuda.is_available():
    model.cuda()
    print("Model loaded on GPU.")
else:
    print("Model loaded on CPU.")

# Read transcript
with open(INPUT_FILE, encoding="utf-8") as f:
    full_text = f.read()

# Split into segments ≤224 chars
import re
segments = []
for block in re.split(r'\n{2,}', full_text):
    block = block.strip()
    if not block:
        continue
    while len(block) > MAX_CHARS:
        # Split at last sentence end before limit
        split_idx = block.rfind('.', 0, MAX_CHARS)
        if split_idx == -1:
            split_idx = MAX_CHARS
        segments.append(block[:split_idx+1].strip())
        block = block[split_idx+1:].strip()
    if block:
        segments.append(block)

print(f"Total segments: {len(segments)}")

# Synthesize each segment
for i, text in enumerate(segments, 1):
    print(f"[{i}/{len(segments)}] Synthesizing: {text[:60]}...")
    try:
        # Use greeting reference for all (can be customized)
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[str(REFERENCE_AUDIO)]
        )
        
        # Run inference
        outputs = model.inference(
            text,
            language="hu",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=0.65,
            repetition_penalty=3.5,
        )
        
        # Extract waveform - handle both dict and direct tensor
        if isinstance(outputs, dict):
            wav = outputs.get("wav", outputs)
        else:
            wav = outputs
        
        # Skip if still a dict (fallback)
        if isinstance(wav, dict):
            print(f"⚠️ Unexpected dict output: {list(wav.keys())}")
            continue
            
        out_path = OUTPUT_DIR / f"quiz_show_{i:03d}.wav"
        
        # Convert to proper tensor format if needed
        if not torch.is_tensor(wav):
            wav = torch.tensor(wav)
        
        # Ensure wav is 2D [channels, samples] for torchaudio
        wav = wav.squeeze().cpu()
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)  # Add channel dimension
        
        # Save using torchaudio
        torchaudio.save(str(out_path), wav, 24000)
        
        print(f"✅ Saved: {out_path.name}")
    except Exception as e:
        import traceback
        print(f"❌ Error on segment {i}: {e}")
        traceback.print_exc()

print("\n🎬 All segments generated!")
print(f"Output folder: {OUTPUT_DIR}")
