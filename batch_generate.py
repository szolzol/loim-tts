"""
Batch TTS Generator from JSON Input
====================================
Generates multiple TTS samples from a JSON configuration file.
Supports both simple text and segmented generation with explicit pauses.

Usage:
  python batch_generate.py                          # Uses input_samples.json
  python batch_generate.py custom_input.json        # Uses custom file
  python batch_generate.py input_samples.json --format wav  # Force WAV output
"""

import torch
import numpy as np
import soundfile as sf
import json
import sys
from pathlib import Path
from datetime import datetime
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import TTS.tts.models.xtts as xtts_module
from pydub import AudioSegment

# Workaround for torchaudio/torchcodec - use soundfile instead
def load_audio_sf(audiopath, sr=None):
    """Load audio using soundfile (bypassing broken torchaudio/torchcodec)"""
    audio_np, lsr = sf.read(audiopath)
    audio = torch.FloatTensor(audio_np)
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)
    else:
        audio = audio.T
    return audio

# Monkey-patch XTTS to use our soundfile loader (no sample rate return)
xtts_module.load_audio = load_audio_sf

# ========================================
# CONFIGURATION
# ========================================

PROJECT_ROOT = Path(__file__).parent.absolute()
MODEL_DIR = PROJECT_ROOT / "run" / "training_combined_phase2" / "XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd"

# ========================================
# HELPER FUNCTIONS
# ========================================

def load_config(config_file):
    """Load JSON configuration file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_output_dir(output_path):
    """Create output directory if it doesn't exist"""
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def generate_silence(duration_sec, sample_rate=24000):
    """Generate silence array"""
    num_samples = int(duration_sec * sample_rate)
    return np.zeros(num_samples, dtype=np.float32)

def to_numpy(audio):
    """Convert audio to numpy array"""
    if isinstance(audio, torch.Tensor):
        return audio.cpu().numpy()
    return audio

def convert_to_mp3(wav_path, mp3_path, bitrate="192k"):
    """Convert WAV to MP3 using pydub"""
    audio = AudioSegment.from_wav(str(wav_path))
    audio.export(str(mp3_path), format="mp3", bitrate=bitrate)
    
def generate_simple_sample(model, text, gpt_cond_latent, speaker_embedding, params, language="hu"):
    """Generate a simple non-segmented audio sample"""
    out = model.inference(
        text=text,
        language=language,
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=params["temperature"],
        top_p=params["top_p"],
        top_k=params["top_k"],
        repetition_penalty=params["repetition_penalty"],
        length_penalty=params["length_penalty"],
        enable_text_splitting=True
    )
    return to_numpy(out["wav"])

def generate_segmented_sample(model, segments, gpt_cond_latent, speaker_embedding, params, language="hu", sample_rate=24000):
    """Generate a segmented audio sample with explicit pauses"""
    audio_segments = []
    
    for segment in segments:
        # Generate segment
        out = model.inference(
            text=segment["text"],
            language=language,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=params["temperature"],
            top_p=params["top_p"],
            top_k=params["top_k"],
            repetition_penalty=params["repetition_penalty"],
            length_penalty=params["length_penalty"],
            enable_text_splitting=False
        )
        audio_segments.append(to_numpy(out["wav"]))
        
        # Add pause if specified
        pause_duration = segment.get("pause_after", 0.0)
        if pause_duration > 0:
            audio_segments.append(generate_silence(pause_duration, sample_rate))
    
    # Concatenate all segments
    return np.concatenate(audio_segments)

# ========================================
# MAIN GENERATION
# ========================================

def main():
    # Parse arguments
    config_file = "input_samples.json"
    output_format_override = None
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] in ["--format", "-f"]:
        if len(sys.argv) > 3:
            output_format_override = sys.argv[3]
    
    print("=" * 80)
    print("🎙️  BATCH TTS GENERATOR")
    print("=" * 80)
    print()
    print(f"📄 Config file: {config_file}")
    print()
    
    # Load configuration
    try:
        config = load_config(config_file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return
    
    gen_config = config["generation_config"]
    samples = config["samples"]
    
    # Output format
    output_format = output_format_override or gen_config.get("output_format", "mp3")
    output_dir = create_output_dir(gen_config["output_directory"])
    
    print(f"📁 Output directory: {output_dir}")
    print(f"🎵 Output format: {output_format.upper()}")
    print(f"🗣️  Language: {gen_config['language']}")
    print(f"🎛️  Multi-reference: {gen_config['multi_reference']}")
    print()
    
    # Model paths
    model_path = MODEL_DIR / gen_config["model_checkpoint"]
    config_path = MODEL_DIR / "config.json"
    vocab_path = MODEL_DIR / "vocab.json"
    
    # Check files
    print("📁 Checking files...")
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return
    
    if gen_config["multi_reference"]:
        references = [PROJECT_ROOT / ref for ref in gen_config["references"]]
        for ref in references:
            if not ref.exists():
                print(f"❌ Reference not found: {ref}")
                return
        print(f"✅ Model and {len(references)} references found")
    else:
        print("✅ Model found")
    print()
    
    # Load model
    print("⏳ Loading XTTS model...")
    xtts_config = XttsConfig()
    xtts_config.load_json(str(config_path))
    
    model = Xtts.init_from_config(xtts_config)
    model.load_checkpoint(
        xtts_config,
        checkpoint_dir=str(MODEL_DIR),
        checkpoint_path=str(model_path),
        vocab_path=str(vocab_path),
        eval=True,
        use_deepspeed=False
    )
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"✅ Model loaded on {device.upper()}")
    print()
    
    # Compute speaker latents
    if gen_config["multi_reference"]:
        print("🎙️ Computing speaker latents from references...")
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[str(ref) for ref in references],
            gpt_cond_len=30,
            gpt_cond_chunk_len=4,
            max_ref_length=60
        )
        print(f"✅ Speaker latents computed from {len(references)} references")
    else:
        print("⚠️  Single reference mode not implemented yet")
        return
    print()
    
    # Generate samples
    print("=" * 80)
    print(f"GENERATING {len(samples)} SAMPLES")
    print("=" * 80)
    print()
    
    params = gen_config["parameters"]
    sample_rate = gen_config["sample_rate"]
    language = gen_config["language"]
    
    for i, sample in enumerate(samples, 1):
        sample_id = sample["id"]
        description = sample.get("description", "")
        is_segmented = sample.get("segmented", False)
        
        print(f"[{i}/{len(samples)}] {sample_id}")
        if description:
            print(f"  📝 {description}")
        
        try:
            if is_segmented:
                print(f"  🔧 Mode: Segmented ({len(sample['segments'])} parts)")
                audio_numpy = generate_segmented_sample(
                    model, sample["segments"], 
                    gpt_cond_latent, speaker_embedding, 
                    params, language, sample_rate
                )
            else:
                text = sample["text"]
                print(f"  📄 Text: {text[:60]}{'...' if len(text) > 60 else ''}")
                print(f"  🔧 Mode: Simple")
                audio_numpy = generate_simple_sample(
                    model, text,
                    gpt_cond_latent, speaker_embedding,
                    params, language
                )
            
            # Save as WAV first
            wav_path = output_dir / f"{sample_id}.wav"
            sf.write(str(wav_path), audio_numpy, sample_rate)
            
            # Convert to MP3 if needed
            if output_format.lower() == "mp3":
                mp3_path = output_dir / f"{sample_id}.mp3"
                convert_to_mp3(wav_path, mp3_path)
                wav_path.unlink()  # Remove WAV file
                output_path = mp3_path
            else:
                output_path = wav_path
            
            file_size = output_path.stat().st_size / 1024  # KB
            duration = len(audio_numpy) / sample_rate
            
            print(f"  ✅ Saved: {output_path.name} ({file_size:.1f} KB, {duration:.1f}s)")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("=" * 80)
    print(f"✅ BATCH GENERATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"📁 Output directory: {output_dir}")
    print(f"🎵 Format: {output_format.upper()}")
    print()

if __name__ == "__main__":
    main()
