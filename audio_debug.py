#!/usr/bin/env python3
"""
Audio Debug Tool - Audio fájl részletes elemzése
"""

import os
import numpy as np
import librosa
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def debug_audio_analysis(audio_file):
    """Audio fájl részletes debug elemzése"""
    print(f"🔍 AUDIO DEBUG ELEMZÉS: {audio_file}")
    print("=" * 50)
    
    # Load with pydub
    audio = AudioSegment.from_file(audio_file)
    audio_mono = audio.set_channels(1).set_frame_rate(24000)
    
    print(f"📊 Alapvető audio info:")
    print(f"   Hossz: {len(audio)/1000:.1f} másodperc")
    print(f"   Csatornák: {audio.channels}")
    print(f"   Sample rate: {audio.frame_rate} Hz")
    print(f"   dBFS: {audio.dBFS:.1f} dB")
    print(f"   Max dBFS: {audio.max_dBFS:.1f} dB")
    
    # Silence analysis with different thresholds
    print(f"\n🔇 Csend elemzés különböző küszöbökkel:")
    
    for thresh in [-40, -35, -30, -25, -20]:
        silence_ranges = detect_silence(audio_mono, min_silence_len=300, silence_thresh=thresh)
        total_silence = sum([end - start for start, end in silence_ranges])
        silence_ratio = total_silence / len(audio_mono)
        print(f"   {thresh}dB küszöb: {len(silence_ranges)} csend szakasz, {silence_ratio:.1%} csend arány")
    
    # Segmentation test
    print(f"\n✂️  Szegmentálás teszt különböző paraméterekkel:")
    
    for min_sil_len, sil_thresh in [(300, -30), (500, -25), (800, -30), (1000, -25)]:
        segments = split_on_silence(
            audio_mono,
            min_silence_len=min_sil_len,
            silence_thresh=sil_thresh,
            keep_silence=100
        )
        
        segment_durations = [len(seg)/1000 for seg in segments]
        valid_segments = [d for d in segment_durations if 8 <= d <= 18]
        
        print(f"   min_silence={min_sil_len}ms, thresh={sil_thresh}dB:")
        print(f"     Összes szegmens: {len(segments)}")
        print(f"     8-18s közötti: {len(valid_segments)}")
        if segment_durations:
            print(f"     Időtartamok: {min(segment_durations):.1f}-{max(segment_durations):.1f}s")
    
    # Manual chunking test
    print(f"\n📏 Manuális chunking teszt:")
    chunk_duration = 12  # seconds
    chunk_ms = chunk_duration * 1000
    overlap_ms = 2000  # 2 second overlap
    
    manual_chunks = []
    for start_ms in range(0, len(audio_mono) - chunk_ms, chunk_ms - overlap_ms):
        chunk = audio_mono[start_ms:start_ms + chunk_ms]
        manual_chunks.append({
            'start': start_ms / 1000,
            'end': (start_ms + chunk_ms) / 1000,
            'duration': len(chunk) / 1000,
            'dbfs': chunk.dBFS
        })
    
    print(f"   {chunk_duration}s chunkokkal: {len(manual_chunks)} darab")
    for i, chunk in enumerate(manual_chunks[:5]):  # Show first 5
        print(f"     Chunk {i+1}: {chunk['start']:.1f}-{chunk['end']:.1f}s, {chunk['dbfs']:.1f}dB")
    
    return manual_chunks

def create_simple_reference_clips(audio_file, output_dir="processed_audio", num_clips=6):
    """Egyszerű referencia klipek készítése manuális chunking-gel"""
    print(f"\n🎯 EGYSZERŰ REFERENCIA KLIPEK KÉSZÍTÉSE")
    print("=" * 50)
    
    # Load audio
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_channels(1).set_frame_rate(24000)
    
    # Simple chunking strategy
    chunk_duration = 12  # seconds
    chunk_ms = chunk_duration * 1000
    overlap_ms = 3000  # 3 second overlap for variety
    
    # Skip first 10 seconds (often has startup noise)
    start_offset = 10000  # 10 seconds
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Clear existing clips
    for f in os.listdir(output_dir):
        if f.startswith("premium_clip_") and f.endswith(".wav"):
            os.remove(os.path.join(output_dir, f))
    
    created_files = []
    chunk_count = 0
    
    for start_ms in range(start_offset, len(audio) - chunk_ms, chunk_ms - overlap_ms):
        if chunk_count >= num_clips:
            break
            
        chunk = audio[start_ms:start_ms + chunk_ms]
        
        # Basic quality filter
        if chunk.dBFS > -30:  # Not too quiet
            # Simple enhancement
            enhanced_chunk = chunk.normalize()
            enhanced_chunk = enhanced_chunk.fade_in(100).fade_out(100)
            
            # Save
            output_file = os.path.join(output_dir, f"premium_clip_{chunk_count+1:02d}.wav")
            enhanced_chunk.export(output_file, format="wav")
            
            created_files.append(output_file)
            chunk_count += 1
            
            start_sec = start_ms / 1000
            end_sec = (start_ms + chunk_ms) / 1000
            print(f"  ✅ premium_clip_{chunk_count:02d}.wav: {start_sec:.1f}-{end_sec:.1f}s, {chunk.dBFS:.1f}dB")
    
    return created_files

def main():
    audio_file = "vago_vagott.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ Nem található: {audio_file}")
        return 1
    
    # Debug analysis
    manual_chunks = debug_audio_analysis(audio_file)
    
    # Create simple reference clips
    ref_files = create_simple_reference_clips(audio_file)
    
    print(f"\n🎉 {len(ref_files)} referencia klip elkészült!")
    
    if ref_files:
        print(f"\n💡 Tesztelés:")
        print(f"   python premium_xtts_hungarian.py --text \"Ez egy teszt szöveg Vágó István hangjával.\" --refs \"{ref_files[0]}\" --out test_premium.wav --mp3")

if __name__ == "__main__":
    main()