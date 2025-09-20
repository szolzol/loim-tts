#!/usr/bin/env python3
"""
Fejlett Audio Preprocessing XTTS v2 Optimalizáláshoz
Több és jobb minőségű referencia klipek készítése
"""

import os
import sys
from pathlib import Path
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
from pydub.effects import normalize, compress_dynamic_range
import librosa
import matplotlib.pyplot as plt

def analyze_audio_segments(audio_file):
    """Részletes audio elemzés a legjobb szegmensek megtalálásához"""
    print(f"🔍 Részletes elemzés: {audio_file}")
    
    # Load audio
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_channels(1)  # Mono
    
    print(f"  📊 Teljes hossz: {len(audio)/1000:.1f} másodperc")
    print(f"  📊 Sample rate: {audio.frame_rate} Hz")
    print(f"  📊 Átlagos hangerő: {audio.dBFS:.1f} dB")
    
    # Convert to numpy for detailed analysis
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    samples = samples / np.max(np.abs(samples))  # Normalize
    
    # Analyze with librosa
    sr = audio.frame_rate
    
    # Energy analysis
    hop_length = 512
    frame_length = 2048
    energy = librosa.feature.rms(y=samples, frame_length=frame_length, hop_length=hop_length)[0]
    
    # Spectral analysis
    spectral_centroids = librosa.feature.spectral_centroid(y=samples, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=samples, sr=sr)[0]
    
    # Find speech segments with good energy and spectral characteristics
    print(f"\n🎯 Hangminőség elemzés:")
    print(f"  📈 Energia tartomány: {np.min(energy):.3f} - {np.max(energy):.3f}")
    print(f"  📈 Spektrális centrum: {np.mean(spectral_centroids):.1f} Hz")
    
    # Find optimal segments
    segment_duration = 8.0  # Target 8 seconds
    overlap = 2.0  # 2 second overlap for better coverage
    
    segments = []
    current_pos = 0
    segment_length_ms = int(segment_duration * 1000)
    overlap_ms = int(overlap * 1000)
    
    while current_pos + segment_length_ms <= len(audio):
        segment = audio[current_pos:current_pos + segment_length_ms]
        
        # Quality metrics for this segment
        seg_samples = np.array(segment.get_array_of_samples(), dtype=np.float32)
        seg_samples = seg_samples / (np.max(np.abs(seg_samples)) + 1e-8)
        
        # Energy consistency
        seg_energy = librosa.feature.rms(y=seg_samples, frame_length=frame_length, hop_length=hop_length)[0]
        energy_variance = np.var(seg_energy)
        energy_mean = np.mean(seg_energy)
        
        # Spectral richness
        seg_spectral = librosa.feature.spectral_centroid(y=seg_samples, sr=sr)[0]
        spectral_variance = np.var(seg_spectral)
        
        # Silence detection
        silence_ranges = detect_silence(segment, min_silence_len=500, silence_thresh=-40)
        silence_ratio = sum([end - start for start, end in silence_ranges]) / len(segment)
        
        # Quality score
        energy_score = min(energy_mean * 10, 1.0)  # Prefer higher energy
        consistency_score = max(0, 1.0 - energy_variance * 5)  # Prefer consistent energy
        spectral_score = min(spectral_variance / 1000, 1.0)  # Prefer spectral variety
        speech_score = max(0, 1.0 - silence_ratio * 2)  # Prefer less silence
        
        quality_score = (energy_score + consistency_score + spectral_score + speech_score) / 4
        
        segments.append({
            'start_ms': current_pos,
            'end_ms': current_pos + segment_length_ms,
            'start_sec': current_pos / 1000,
            'end_sec': (current_pos + segment_length_ms) / 1000,
            'energy_mean': energy_mean,
            'energy_variance': energy_variance,
            'spectral_variance': spectral_variance,
            'silence_ratio': silence_ratio,
            'quality_score': quality_score,
            'segment': segment
        })
        
        current_pos += segment_length_ms - overlap_ms
    
    # Sort by quality score
    segments.sort(key=lambda x: x['quality_score'], reverse=True)
    
    print(f"\n📋 Talált szegmensek: {len(segments)}")
    for i, seg in enumerate(segments[:10]):  # Top 10
        print(f"  {i+1:2d}. {seg['start_sec']:5.1f}-{seg['end_sec']:5.1f}s | "
              f"Minőség: {seg['quality_score']:.3f} | "
              f"Energia: {seg['energy_mean']:.3f} | "
              f"Csend: {seg['silence_ratio']:.1%}")
    
    return segments

def create_optimized_references(audio_file, output_dir, num_clips=8):
    """Optimalizált referencia klipek létrehozása"""
    print(f"\n🎨 Optimalizált referencia klipek készítése...")
    
    # Analyze segments
    segments = analyze_audio_segments(audio_file)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Clear existing optimized clips
    for existing_file in output_path.glob("optimized_clip_*.wav"):
        existing_file.unlink()
    
    # Select best segments with diversity
    selected_segments = []
    
    # Take top quality segments but ensure they don't overlap too much
    for seg in segments:
        overlap_found = False
        for selected in selected_segments:
            # Check for significant overlap
            if (seg['start_sec'] < selected['end_sec'] - 2 and 
                seg['end_sec'] > selected['start_sec'] + 2):
                overlap_found = True
                break
        
        if not overlap_found:
            selected_segments.append(seg)
            if len(selected_segments) >= num_clips:
                break
    
    print(f"\n✂️  Kiválasztott {len(selected_segments)} legjobb szegmens:")
    
    # Process and save segments
    created_files = []
    for i, seg in enumerate(selected_segments):
        # Get the audio segment
        audio_segment = seg['segment']
        
        # Optimize audio quality
        # 1. Normalize
        audio_segment = normalize(audio_segment)
        
        # 2. Light compression for consistency
        audio_segment = compress_dynamic_range(audio_segment, threshold=-20.0, ratio=2.0)
        
        # 3. Convert to 24kHz for XTTS
        audio_segment = audio_segment.set_frame_rate(24000)
        
        # 4. Ensure optimal length (6-12 seconds)
        target_length = 8000  # 8 seconds in ms
        if len(audio_segment) > target_length:
            # Crop from center to preserve quality
            start_crop = (len(audio_segment) - target_length) // 2
            audio_segment = audio_segment[start_crop:start_crop + target_length]
        
        # 5. Fade in/out for smooth edges
        audio_segment = audio_segment.fade_in(100).fade_out(100)
        
        # Save
        output_file = output_path / f"optimized_clip_{i+1:02d}.wav"
        audio_segment.export(output_file, format="wav")
        
        created_files.append(str(output_file))
        
        print(f"  ✅ {output_file.name}: {seg['start_sec']:.1f}-{seg['end_sec']:.1f}s "
              f"(minőség: {seg['quality_score']:.3f})")
    
    return created_files

def main():
    audio_file = "vago_vagott.mp3"
    output_dir = "processed_audio"
    
    if not os.path.exists(audio_file):
        print(f"❌ Nem található: {audio_file}")
        return 1
    
    print("🎚️  XTTS v2 Fejlett Audio Preprocessing")
    print("=" * 50)
    
    # Create optimized references
    optimized_files = create_optimized_references(audio_file, output_dir, num_clips=8)
    
    print(f"\n🎉 Elkészült {len(optimized_files)} optimalizált referencia klip!")
    print("\n📁 Létrehozott fájlok:")
    for f in optimized_files:
        file_path = Path(f)
        audio = AudioSegment.from_wav(f)
        print(f"  📄 {file_path.name}: {len(audio)/1000:.1f}s, {audio.frame_rate}Hz, {audio.dBFS:.1f}dB")
    
    print(f"\n💡 Használat:")
    print(f"   python simple_xtts_hungarian.py --text \"Teszt szöveg\" --refs \"{optimized_files[0]}\" --out test.wav --mp3")
    print(f"   # vagy több referencia:")
    print(f"   python simple_xtts_hungarian.py --text \"Teszt szöveg\" --refs \"{','.join(optimized_files[:4])}\" --out test.wav --mp3")

if __name__ == "__main__":
    sys.exit(main())