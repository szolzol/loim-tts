#!/usr/bin/env python3
"""
Audio preprocessing script for XTTS v2 Hungarian TTS
Converts and splits audio for optimal voice cloning
"""

import os
import sys
from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence
import argparse

def convert_to_wav_24k_mono(input_file, output_dir):
    """
    Convert audio file to WAV, 24kHz, mono format
    """
    print(f"Converting {input_file} to WAV 24kHz mono...")
    
    # Load audio file
    audio = AudioSegment.from_file(input_file)
    
    # Convert to mono
    if audio.channels > 1:
        audio = audio.set_channels(1)
        print("  ✓ Converted to mono")
    
    # Convert to 24kHz
    if audio.frame_rate != 24000:
        audio = audio.set_frame_rate(24000)
        print("  ✓ Resampled to 24kHz")
    
    # Normalize audio to -23 LUFS approximation
    audio = normalize(audio)
    print("  ✓ Normalized audio")
    
    # Export as WAV
    output_file = os.path.join(output_dir, "converted_audio.wav")
    audio.export(output_file, format="wav")
    print(f"  ✓ Saved to {output_file}")
    
    return output_file, audio

def split_audio_intelligent(audio, output_dir, min_length=6, max_length=12, target_clips=4):
    """
    Split audio into optimal clips for XTTS conditioning
    """
    print(f"\nSplitting audio into {target_clips} clips ({min_length}-{max_length} seconds each)...")
    
    # First try splitting on silence
    chunks = split_on_silence(
        audio,
        min_silence_len=500,  # 500ms of silence
        silence_thresh=-40,   # dB threshold
        keep_silence=200      # Keep 200ms of silence
    )
    
    print(f"  Found {len(chunks)} speech segments")
    
    # Filter chunks by length
    good_chunks = []
    for i, chunk in enumerate(chunks):
        duration = len(chunk) / 1000.0  # Convert to seconds
        if min_length <= duration <= max_length:
            good_chunks.append(chunk)
            print(f"    Chunk {i+1}: {duration:.1f}s - ✓ Good")
        elif duration < min_length:
            print(f"    Chunk {i+1}: {duration:.1f}s - Too short")
        else:
            print(f"    Chunk {i+1}: {duration:.1f}s - Too long")
    
    # If we don't have enough good chunks, create them by time splitting
    if len(good_chunks) < target_clips:
        print(f"\n  Only {len(good_chunks)} good chunks found, creating time-based splits...")
        
        total_duration = len(audio) / 1000.0
        chunk_duration = min(max_length, total_duration / target_clips)
        
        chunks = []
        start = 0
        while start < len(audio) and len(chunks) < target_clips:
            end = min(start + chunk_duration * 1000, len(audio))
            chunk = audio[start:end]
            
            # Only add if it's long enough
            if len(chunk) / 1000.0 >= min_length:
                chunks.append(chunk)
                print(f"    Time chunk {len(chunks)}: {len(chunk)/1000.0:.1f}s")
            
            start = end
        
        good_chunks = chunks
    
    # Take the best chunks (up to target_clips)
    good_chunks = good_chunks[:target_clips]
    
    # Save chunks
    output_files = []
    for i, chunk in enumerate(good_chunks):
        filename = f"reference_clip_{i+1:02d}.wav"
        output_path = os.path.join(output_dir, filename)
        chunk.export(output_path, format="wav")
        duration = len(chunk) / 1000.0
        print(f"  ✓ Saved {filename} ({duration:.1f}s)")
        output_files.append(output_path)
    
    return output_files

def main():
    parser = argparse.ArgumentParser(description="Preprocess audio for XTTS v2")
    parser.add_argument("--input", "-i", required=True, help="Input audio file")
    parser.add_argument("--output", "-o", default="./processed", help="Output directory")
    parser.add_argument("--clips", "-c", type=int, default=4, help="Number of clips to create")
    parser.add_argument("--min-length", type=float, default=6.0, help="Minimum clip length in seconds")
    parser.add_argument("--max-length", type=float, default=12.0, help="Maximum clip length in seconds")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    print("XTTS v2 Audio Preprocessing")
    print("=" * 40)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Target clips: {args.clips}")
    print(f"Clip length: {args.min_length}-{args.max_length} seconds")
    
    try:
        # Convert to proper format
        wav_file, audio = convert_to_wav_24k_mono(args.input, args.output)
        
        # Split into clips
        clip_files = split_audio_intelligent(
            audio, args.output, 
            args.min_length, args.max_length, args.clips
        )
        
        print(f"\n🎉 Success! Created {len(clip_files)} reference clips:")
        for clip_file in clip_files:
            print(f"   - {os.path.basename(clip_file)}")
        
        print(f"\nNext steps:")
        print(f"1. Listen to the clips and ensure they sound good")
        print(f"2. Remove any clips with background noise or poor quality")
        print(f"3. Use the clips with the TTS script:")
        print(f"   python xtts_hungarian_tts.py \\")
        print(f"     --text \"Your Hungarian text\" \\")
        for clip_file in clip_files:
            print(f"     --refs \"{clip_file}\" \\")
        print(f"     --out output.wav --mp3")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())