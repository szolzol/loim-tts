"""
Speech-to-Text Transcription for István Vágó Audio Files
Uses OpenAI Whisper for accurate Hungarian transcription
"""

import os
import sys
import csv
from pathlib import Path

try:
    import whisper
    import torch
except ImportError:
    print("❌ Error: whisper or torch not installed")
    print("Run: pip install openai-whisper")
    sys.exit(1)

# Paths
SOURCE_CLIPS_DIR = Path("f:/CODE/tts-2/source_clips")
OUTPUT_CSV = Path("f:/CODE/tts-2/processed_clips/metadata_transcribed.csv")

def transcribe_audio_files():
    """Transcribe all audio files using Whisper"""
    
    print("=" * 70)
    print("István Vágó Audio Transcription")
    print("=" * 70)
    
    # Check for audio files
    if not SOURCE_CLIPS_DIR.exists():
        print(f"❌ Error: Directory not found: {SOURCE_CLIPS_DIR}")
        return
    
    audio_files = sorted(list(SOURCE_CLIPS_DIR.glob("*.wav")))
    if not audio_files:
        print(f"❌ Error: No WAV files found in {SOURCE_CLIPS_DIR}")
        return
    
    print(f"\n📁 Found {len(audio_files)} audio files")
    
    # Load Whisper model
    print("\n🤖 Loading Whisper model (medium - best for Hungarian)...")
    try:
        # Use medium model for better Hungarian accuracy
        # Can use 'large' for even better accuracy but slower
        model = whisper.load_model("medium")
        print("  ✅ Model loaded")
    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        return
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  ℹ️ Using device: {device}")
    
    # Transcribe each file
    results = []
    print("\n🎤 Transcribing audio files...")
    print("-" * 70)
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
        
        try:
            # Transcribe with language hint
            result = model.transcribe(
                str(audio_file),
                language="hu",  # Hungarian
                task="transcribe",
                verbose=False,
            )
            
            transcription = result["text"].strip()
            
            # Show result
            print(f"  ✅ Transcribed: {transcription[:80]}...")
            
            # Store result
            results.append({
                "filename": audio_file.stem,  # without extension
                "text": transcription,
                "speaker_name": "istvan_vago"
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            # Add placeholder if transcription fails
            results.append({
                "filename": audio_file.stem,
                "text": "[TRANSCRIPTION FAILED]",
                "speaker_name": "istvan_vago"
            })
    
    # Save to CSV
    print("\n" + "=" * 70)
    print("💾 Saving transcriptions...")
    
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'text', 'speaker_name'], delimiter='|')
        
        # Write header
        f.write("audio_file|text|speaker_name\n")
        
        # Write data
        for row in results:
            f.write(f"{row['filename']}.wav|{row['text']}|{row['speaker_name']}\n")
    
    print(f"  ✅ Saved to: {OUTPUT_CSV}")
    
    # Display summary
    print("\n" + "=" * 70)
    print("📊 Transcription Summary")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['filename']}.wav")
        print(f"   {result['text']}")
    
    print("\n" + "=" * 70)
    print("✅ Transcription complete!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print(f"1. Review transcriptions in: {OUTPUT_CSV}")
    print("2. Correct any errors or mishearings")
    print("3. Copy corrected version to: dataset/metadata.csv")
    print("4. Then proceed with training")
    
    return results


if __name__ == "__main__":
    transcribe_audio_files()
