"""
István Vágó Voice Cloning - Dataset Preparation
Prepares audio samples and creates metadata for XTTS-v2 training
Ensures maximum quality for ElevenLabs/Fish Audio level output
"""

import os
import json
import csv
import wave
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configuration
SOURCE_CLIPS_DIR = Path("f:/CODE/tts-2/source_clips")
OUTPUT_DIR = Path("f:/CODE/tts-2/dataset")
SAMPLE_RATE = 22050  # XTTS-v2 training requirement
MIN_DURATION = 2.0  # seconds
MAX_DURATION = 15.0  # seconds
SILENCE_THRESHOLD = 0.01  # RMS threshold for silence detection
TARGET_RMS = 0.1  # Target RMS for normalization
SNR_THRESHOLD = 15.0  # Minimum SNR in dB

# Hungarian transcriptions for István Vágó clips
# TODO: Replace with actual accurate transcriptions
TRANSCRIPTIONS = {
    "1_vago_finetune2.wav": "Üdvözlöm önöket a kvízműsorban! Készüljünk fel a következő kérdésre.",
    "2_vago_finetune2.wav": "Ez egy rendkívül érdekes kérdés lesz. Figyeljünk együtt!",
    "3_vago_finetune2.wav": "Gratulálok a helyes válaszhoz! Fantasztikus teljesítmény.",
    "4_vago_finetune2.wav": "Most egy nehezebb kérdés következik. Gondolkozzanak csak!",
    "5_vago_finetune2.wav": "Az idő múlik, dönteniük kell hamarosan.",
    "6_vago_finetune2.wav": "Lássuk a helyes választ! Mit gondolnak, jó lesz?",
    "7_vago_finetune2.wav": "Köszönöm szépen, remek játék volt. Gratulálok mindenkinek!",
    "vago_vagott_01.wav": "Jó estét kívánok mindenkinek! Kezdjük is a mai műsort.",
    "vago_vagott_02.wav": "A következő kérdés már nehezebb lesz, koncentráljanak!",
    "vago_vagott_03.wav": "Helyes válasz! Látom, hogy jól felkészültek.",
    "vago_vagott_04.wav": "Sajnos ez nem volt a jó válasz. De ne csüggedjenek!",
    "vago_vagott_05.wav": "Izgalmas pillanatokhoz érkeztünk. Ki fog nyerni?",
    "vago_vagott_06.wav": "Köszönjük a játékot! Viszlát a következő adásban!",
}


def analyze_audio(audio_path: Path) -> Dict:
    """Comprehensive audio analysis for quality assessment"""
    
    # Load audio
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Basic stats
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # Zero crossing rate (voice activity)
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    
    # Estimate SNR
    # Simple method: use quietest 10% as noise floor
    sorted_rms = np.sort(rms)
    noise_floor = np.mean(sorted_rms[:len(sorted_rms)//10])
    signal_power = rms_mean ** 2
    noise_power = noise_floor ** 2
    snr_db = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
    
    return {
        "duration": duration,
        "sample_rate": sr,
        "rms_mean": rms_mean,
        "rms_std": rms_std,
        "spectral_centroid_mean": float(np.mean(spectral_centroids)),
        "zcr_mean": float(np.mean(zcr)),
        "snr_db": snr_db,
        "max_amplitude": float(np.max(np.abs(y))),
        "min_amplitude": float(np.min(np.abs(y))),
    }


def reduce_noise(audio: np.ndarray, sr: int) -> np.ndarray:
    """Apply noise reduction"""
    try:
        # Use the first 0.5 seconds as noise sample if available
        noise_sample = audio[:int(0.5 * sr)]
        reduced = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample, prop_decrease=0.8)
        return reduced
    except Exception as e:
        print(f"  Warning: Noise reduction failed: {e}")
        return audio


def normalize_audio(audio: np.ndarray, target_rms: float = TARGET_RMS) -> np.ndarray:
    """Normalize audio to target RMS level"""
    current_rms = np.sqrt(np.mean(audio ** 2))
    if current_rms > 0:
        audio = audio * (target_rms / current_rms)
    
    # Peak normalize to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 0.95:
        audio = audio * (0.95 / max_val)
    
    return audio


def trim_silence(audio: np.ndarray, sr: int, threshold: float = SILENCE_THRESHOLD) -> np.ndarray:
    """Aggressively trim silence from beginning and end"""
    # Use librosa's built-in function
    trimmed, _ = librosa.effects.trim(audio, top_db=30, frame_length=2048, hop_length=512)
    return trimmed


def process_audio_file(input_path: Path, output_path: Path) -> Tuple[bool, Dict]:
    """
    Process a single audio file:
    1. Load and convert to mono
    2. Resample to target SR
    3. Reduce noise
    4. Trim silence
    5. Normalize
    6. Save
    
    Returns: (success, analysis_dict)
    """
    try:
        # Load audio
        y, sr = librosa.load(input_path, sr=None, mono=True)
        
        # Resample if needed
        if sr != SAMPLE_RATE:
            y = librosa.resample(y, orig_sr=sr, target_sr=SAMPLE_RATE)
            sr = SAMPLE_RATE
        
        # Apply noise reduction
        y = reduce_noise(y, sr)
        
        # Trim silence
        y = trim_silence(y, sr)
        
        # Check duration
        duration = len(y) / sr
        if duration < MIN_DURATION:
            print(f"  ⚠️ Too short: {duration:.2f}s < {MIN_DURATION}s")
            return False, {}
        
        if duration > MAX_DURATION:
            print(f"  ⚠️ Too long: {duration:.2f}s > {MAX_DURATION}s - trimming")
            y = y[:int(MAX_DURATION * sr)]
        
        # Normalize
        y = normalize_audio(y, TARGET_RMS)
        
        # Analyze
        analysis = {
            "duration": len(y) / sr,
            "sample_rate": sr,
            "rms": float(np.sqrt(np.mean(y ** 2))),
            "max_amplitude": float(np.max(np.abs(y))),
        }
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, y, sr, subtype='PCM_16')
        
        return True, analysis
        
    except Exception as e:
        print(f"  ❌ Error processing: {e}")
        return False, {}


def create_metadata_csv(dataset_dir: Path, transcriptions: Dict) -> Path:
    """Create metadata.csv in LJSpeech format: filename|text|speaker"""
    
    metadata_path = dataset_dir / "metadata.csv"
    wavs_dir = dataset_dir / "wavs"
    
    with open(metadata_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        
        for wav_file in sorted(wavs_dir.glob("*.wav")):
            filename = wav_file.stem  # filename without extension
            text = transcriptions.get(wav_file.name, "")
            
            if not text:
                print(f"⚠️ Warning: No transcription for {wav_file.name}")
                continue
            
            # Format: filename|text|speaker_name
            writer.writerow([filename, text, "istvan_vago"])
    
    print(f"\n✅ Created metadata.csv with {len(list(wavs_dir.glob('*.wav')))} entries")
    return metadata_path


def create_dataset_statistics(wavs_dir: Path, output_file: Path):
    """Generate comprehensive dataset statistics"""
    
    stats = {
        "total_files": 0,
        "total_duration": 0.0,
        "durations": [],
        "rms_values": [],
        "snr_values": [],
    }
    
    print("\n📊 Analyzing dataset quality...")
    
    for wav_file in tqdm(list(wavs_dir.glob("*.wav"))):
        analysis = analyze_audio(wav_file)
        
        stats["total_files"] += 1
        stats["total_duration"] += analysis["duration"]
        stats["durations"].append(analysis["duration"])
        stats["rms_values"].append(analysis["rms_mean"])
        stats["snr_values"].append(analysis["snr_db"])
    
    # Calculate statistics
    summary = {
        "total_files": stats["total_files"],
        "total_duration_minutes": stats["total_duration"] / 60,
        "avg_duration": np.mean(stats["durations"]),
        "min_duration": np.min(stats["durations"]),
        "max_duration": np.max(stats["durations"]),
        "avg_rms": np.mean(stats["rms_values"]),
        "avg_snr_db": np.mean([s for s in stats["snr_values"] if s != float('inf')]),
    }
    
    # Save statistics
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n📈 Dataset Statistics:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Total duration: {summary['total_duration_minutes']:.2f} minutes")
    print(f"  Average duration: {summary['avg_duration']:.2f} seconds")
    print(f"  Duration range: {summary['min_duration']:.2f}s - {summary['max_duration']:.2f}s")
    print(f"  Average RMS: {summary['avg_rms']:.4f}")
    print(f"  Average SNR: {summary['avg_snr_db']:.2f} dB")
    
    # Quality assessment
    print("\n✅ Quality Assessment:")
    if summary['total_duration_minutes'] >= 10:
        print(f"  ✅ Duration: Sufficient ({summary['total_duration_minutes']:.1f} min)")
    else:
        print(f"  ⚠️ Duration: Low ({summary['total_duration_minutes']:.1f} min, recommend 15+ min)")
    
    if summary['avg_snr_db'] >= SNR_THRESHOLD:
        print(f"  ✅ SNR: Good ({summary['avg_snr_db']:.1f} dB)")
    else:
        print(f"  ⚠️ SNR: Could be better ({summary['avg_snr_db']:.1f} dB)")
    
    return summary


def main():
    """Main dataset preparation pipeline"""
    
    print("=" * 60)
    print("István Vágó Voice Dataset Preparation")
    print("=" * 60)
    
    # Create output directories
    wavs_dir = OUTPUT_DIR / "wavs"
    wavs_dir.mkdir(parents=True, exist_ok=True)
    
    # Check source directory
    if not SOURCE_CLIPS_DIR.exists():
        print(f"❌ Error: Source directory not found: {SOURCE_CLIPS_DIR}")
        return
    
    source_files = list(SOURCE_CLIPS_DIR.glob("*.wav"))
    if not source_files:
        print(f"❌ Error: No WAV files found in {SOURCE_CLIPS_DIR}")
        return
    
    print(f"\n📁 Found {len(source_files)} audio files in source directory")
    
    # Process each audio file
    print("\n🔧 Processing audio files...")
    successful = 0
    failed = 0
    
    for source_file in tqdm(source_files):
        output_file = wavs_dir / source_file.name
        
        print(f"\n  Processing: {source_file.name}")
        success, analysis = process_audio_file(source_file, output_file)
        
        if success:
            successful += 1
            print(f"    ✅ Processed: {analysis['duration']:.2f}s, RMS: {analysis['rms']:.4f}")
        else:
            failed += 1
    
    print(f"\n📊 Processing Summary:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    
    # Create metadata CSV
    print("\n📝 Creating metadata...")
    metadata_path = create_metadata_csv(OUTPUT_DIR, TRANSCRIPTIONS)
    
    # Generate statistics
    stats_file = OUTPUT_DIR / "dataset_statistics.json"
    create_dataset_statistics(wavs_dir, stats_file)
    
    print("\n" + "=" * 60)
    print("✅ Dataset preparation complete!")
    print("=" * 60)
    print(f"\n📂 Dataset location: {OUTPUT_DIR}")
    print(f"📄 Metadata: {metadata_path}")
    print(f"📊 Statistics: {stats_file}")
    print("\n⚠️ IMPORTANT: Verify transcriptions in metadata.csv before training!")
    print("   Current transcriptions are PLACEHOLDERS and must be replaced with accurate Hungarian text.")
    print("\n🚀 Next step: Run training with scripts/train_xtts.py")


if __name__ == "__main__":
    main()
