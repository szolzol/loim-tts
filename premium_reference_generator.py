#!/usr/bin/env python3
"""
Premium Reference Clip Generator
ElevenLabs-szintű referencia klipek készítése fejlett kritériumokkal
"""

import os
import sys
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
from pydub.effects import normalize, compress_dynamic_range, high_pass_filter, low_pass_filter
import json

class PremiumReferenceGenerator:
    def __init__(self, config_path="premium_tts_config.json"):
        """Premium referencia generátor inicializálás"""
        self.config = self._load_config(config_path)
        self.sample_rate = 24000
        
    def _load_config(self, config_path):
        """Konfiguráció betöltése"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default premium konfiguráció
        return {
            "conditioning_strategy": {
                "min_ref_duration": 10.0,
                "max_ref_duration": 15.0,
                "ref_overlap": 0.3,
                "diversity_threshold": 0.7,
                "quality_threshold": 0.9
            }
        }
    
    def analyze_audio_premium(self, audio_file):
        """Prémium audio elemzés ElevenLabs kritériumokkal"""
        print(f"🔬 PRÉMIUM AUDIO ELEMZÉS: {audio_file}")
        
        # Load audio
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
        
        # Convert to numpy
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples = samples / (np.max(np.abs(samples)) + 1e-8)
        
        # Advanced analysis with librosa
        sr = self.sample_rate
        
        # 1. Signal quality metrics
        snr = self._calculate_snr(samples)
        dynamic_range = self._calculate_dynamic_range(samples)
        spectral_centroid = librosa.feature.spectral_centroid(y=samples, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=samples, sr=sr)[0]
        spectral_flux = librosa.onset.onset_strength(y=samples, sr=sr)
        
        # 2. Prosody analysis
        f0, voiced_flag, _ = librosa.pyin(samples, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        f0_clean = f0[voiced_flag]
        
        pitch_variation = np.std(f0_clean) / np.mean(f0_clean) if len(f0_clean) > 0 else 0
        
        # 3. Energy and rhythm analysis
        rms_energy = librosa.feature.rms(y=samples)[0]
        tempo, _ = librosa.beat.beat_track(y=samples, sr=sr)
        
        # 4. Emotional/tonal features
        mfccs = librosa.feature.mfcc(y=samples, sr=sr, n_mfcc=13)
        
        # 5. Quality scoring
        quality_metrics = {
            "snr_db": float(snr),
            "dynamic_range_db": float(dynamic_range),
            "pitch_variation": float(pitch_variation),
            "spectral_centroid_mean": float(np.mean(spectral_centroid)),
            "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
            "tempo": float(tempo),
            "energy_variance": float(np.var(rms_energy)),
            "duration": len(audio) / 1000.0
        }
        
        # Overall quality score (0-1)
        quality_score = self._calculate_quality_score(quality_metrics)
        quality_metrics["overall_quality"] = quality_score
        
        return quality_metrics, samples
    
    def _calculate_snr(self, samples):
        """Signal-to-noise ratio kiszámítása"""
        # Simple SNR estimation
        signal_power = np.mean(samples ** 2)
        noise_power = np.mean((samples - np.mean(samples)) ** 2) * 0.1  # Approximate
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        return snr
    
    def _calculate_dynamic_range(self, samples):
        """Dinamikus tartomány kiszámítása"""
        rms = np.sqrt(np.mean(samples ** 2))
        peak = np.max(np.abs(samples))
        return 20 * np.log10(peak / (rms + 1e-10))
    
    def _calculate_quality_score(self, metrics):
        """Összesített minőségi pontszám (0-1)"""
        scores = []
        
        # SNR score (25+ dB = perfect)
        snr_score = min(metrics["snr_db"] / 25.0, 1.0)
        scores.append(snr_score)
        
        # Dynamic range score (15+ dB = perfect)
        dr_score = min(metrics["dynamic_range_db"] / 15.0, 1.0)
        scores.append(dr_score)
        
        # Pitch variation score (0.2-0.4 = natural)
        pv = metrics["pitch_variation"]
        pv_score = 1.0 - abs(pv - 0.3) / 0.3 if pv <= 0.6 else 0.5
        scores.append(max(pv_score, 0.0))
        
        # Duration score (10-15s = optimal)
        duration = metrics["duration"]
        if 10 <= duration <= 15:
            dur_score = 1.0
        elif 8 <= duration <= 18:
            dur_score = 0.8
        else:
            dur_score = 0.5
        scores.append(dur_score)
        
        # Energy consistency score
        energy_consistency = 1.0 - min(metrics["energy_variance"] * 10, 1.0)
        scores.append(energy_consistency)
        
        return np.mean(scores)
    
    def find_premium_segments(self, audio_file, output_dir="processed_audio", num_clips=6):
        """Prémium szegmensek keresése fejlett kritériumokkal"""
        print(f"\n🎯 PRÉMIUM SZEGMENSEK KERESÉSE")
        print("=" * 50)
        
        # Analyze full audio
        quality_metrics, samples = self.analyze_audio_premium(audio_file)
        
        print(f"📊 Audio kvalitás metrikák:")
        for key, value in quality_metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
        
        # Load audio for segmentation
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
        
        # Advanced segmentation
        segments = self._advanced_segmentation(audio, samples)
        
        # Filter and rank segments
        premium_segments = self._filter_premium_segments(segments, num_clips)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Clear existing premium clips
        for existing_file in output_path.glob("premium_clip_*.wav"):
            existing_file.unlink()
        
        # Generate premium clips
        created_files = []
        for i, segment in enumerate(premium_segments):
            # Enhanced audio processing
            enhanced_segment = self._enhance_audio_segment(segment['audio'])
            
            # Save premium clip
            output_file = output_path / f"premium_clip_{i+1:02d}.wav"
            enhanced_segment.export(output_file, format="wav")
            
            created_files.append(str(output_file))
            
            print(f"  ✅ {output_file.name}: {segment['start_sec']:.1f}-{segment['end_sec']:.1f}s "
                  f"(Q: {segment['quality_score']:.3f}, SNR: {segment['snr']:.1f}dB)")
        
        return created_files
    
    def _advanced_segmentation(self, audio, samples):
        """Fejlett szegmentálás prémium kritériumokkal"""
        sr = self.sample_rate
        min_duration = self.config["conditioning_strategy"]["min_ref_duration"]
        max_duration = self.config["conditioning_strategy"]["max_ref_duration"]
        
        # Find speech segments with relaxed silence detection for real audio
        speech_segments = split_on_silence(
            audio,
            min_silence_len=500,  # Shorter silence tolerance
            silence_thresh=-30,   # Less sensitive to capture more content
            keep_silence=150      # Natural pauses
        )
        
        segments = []
        current_pos = 0
        
        for speech_segment in speech_segments:
            segment_duration = len(speech_segment) / 1000.0
            
            # Skip too short segments
            if segment_duration < min_duration:
                current_pos += len(speech_segment)
                continue
            
            # Process longer segments by splitting
            if segment_duration > max_duration:
                # Split into overlapping chunks
                chunk_duration_ms = int(max_duration * 1000)
                overlap_ms = int(max_duration * 1000 * 0.2)  # 20% overlap
                
                for start_ms in range(0, len(speech_segment) - chunk_duration_ms, chunk_duration_ms - overlap_ms):
                    chunk = speech_segment[start_ms:start_ms + chunk_duration_ms]
                    
                    segment_info = self._analyze_segment_quality(chunk, current_pos + start_ms, audio)
                    if segment_info:
                        segments.append(segment_info)
            else:
                # Use full segment
                segment_info = self._analyze_segment_quality(speech_segment, current_pos, audio)
                if segment_info:
                    segments.append(segment_info)
            
            current_pos += len(speech_segment)
        
        return segments
    
    def _analyze_segment_quality(self, segment, start_pos_ms, full_audio):
        """Szegmens minőség elemzése"""
        duration = len(segment) / 1000.0
        start_sec = start_pos_ms / 1000.0
        end_sec = start_sec + duration
        
        # Convert to numpy for analysis
        seg_samples = np.array(segment.get_array_of_samples(), dtype=np.float32)
        seg_samples = seg_samples / (np.max(np.abs(seg_samples)) + 1e-8)
        
        # Quality metrics
        snr = self._calculate_snr(seg_samples)
        dynamic_range = self._calculate_dynamic_range(seg_samples)
        
        # Prosody analysis
        try:
            f0, voiced_flag, _ = librosa.pyin(seg_samples, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            f0_clean = f0[voiced_flag]
            pitch_variation = np.std(f0_clean) / np.mean(f0_clean) if len(f0_clean) > 0 else 0
        except:
            pitch_variation = 0
        
        # Energy analysis
        rms_energy = librosa.feature.rms(y=seg_samples)[0]
        energy_variance = np.var(rms_energy)
        
        # Silence ratio
        silence_ranges = detect_silence(segment, min_silence_len=300, silence_thresh=-40)
        silence_ratio = sum([end - start for start, end in silence_ranges]) / len(segment)
        
        # Overall quality score
        metrics = {
            "snr_db": snr,
            "dynamic_range_db": dynamic_range,
            "pitch_variation": pitch_variation,
            "energy_variance": energy_variance,
            "duration": duration
        }
        
        quality_score = self._calculate_quality_score(metrics)
        
        # Relaxed quality criteria for real-world audio
        if quality_score >= 0.5 and snr >= 8 and silence_ratio < 0.6:
            return {
                "audio": segment,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "quality_score": quality_score,
                "snr": snr,
                "dynamic_range": dynamic_range,
                "pitch_variation": pitch_variation,
                "silence_ratio": silence_ratio,
                "duration": duration
            }
        
        return None
    
    def _filter_premium_segments(self, segments, num_clips):
        """Prémium szegmensek szűrése és rangsorolása"""
        if not segments:
            return []
        
        # Sort by quality score
        segments.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Ensure diversity (no overlapping segments)
        selected = []
        for segment in segments:
            overlap_found = False
            for selected_seg in selected:
                # Check for overlap
                if (segment['start_sec'] < selected_seg['end_sec'] - 2 and 
                    segment['end_sec'] > selected_seg['start_sec'] + 2):
                    overlap_found = True
                    break
            
            if not overlap_found:
                selected.append(segment)
                if len(selected) >= num_clips:
                    break
        
        return selected
    
    def _enhance_audio_segment(self, segment):
        """Audio szegmens minőség javítása"""
        # 1. Normalizálás
        enhanced = normalize(segment)
        
        # 2. Dinamikus range optimalizálás
        enhanced = compress_dynamic_range(enhanced, threshold=-20.0, ratio=2.0, attack=10.0, release=100.0)
        
        # 3. Spektrális tisztítás
        # High-pass filter (remove low-frequency noise)
        enhanced = high_pass_filter(enhanced, cutoff=80)
        
        # Low-pass filter (remove high-frequency noise above speech range)
        enhanced = low_pass_filter(enhanced, cutoff=8000)
        
        # 4. Fade in/out for smooth edges
        enhanced = enhanced.fade_in(50).fade_out(50)
        
        # 5. Final normalization to optimal level
        enhanced = enhanced.apply_gain(-20 - enhanced.dBFS)  # Target -20dB
        
        return enhanced

def main():
    """Main premium reference generator"""
    print("🎨 PRÉMIUM REFERENCIA KLIP GENERÁTOR")
    print("=" * 50)
    print("ElevenLabs-szintű referencia klipek készítése")
    
    audio_file = "vago_vagott.mp3"
    output_dir = "processed_audio"
    
    if not os.path.exists(audio_file):
        print(f"❌ Nem található: {audio_file}")
        return 1
    
    # Premium generator inicializálás
    generator = PremiumReferenceGenerator()
    
    # Generate premium clips
    premium_files = generator.find_premium_segments(
        audio_file=audio_file,
        output_dir=output_dir,
        num_clips=6
    )
    
    print(f"\n🎉 {len(premium_files)} prémium referencia klip elkészült!")
    print("\n📁 Létrehozott fájlok:")
    for f in premium_files:
        file_path = Path(f)
        audio = AudioSegment.from_wav(f)
        print(f"  📄 {file_path.name}: {len(audio)/1000:.1f}s, {audio.dBFS:.1f}dB")
    
    if premium_files:
        print(f"\n💡 Prémium szintézis használat:")
        print(f"   python premium_xtts_hungarian.py --text \"Teszt szöveg\" --refs \"{premium_files[0]}\" --out premium_test.wav --mp3")
    else:
        print("\n⚠️  Nem sikerült megfelelő minőségű szegmenseket találni.")
        print("   Próbálja a relaxáltabb kritériumokkal vagy hosszabb audio fájllal.")

if __name__ == "__main__":
    sys.exit(main())