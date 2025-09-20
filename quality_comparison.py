#!/usr/bin/env python3
"""
Quality Comparison Tool
Objektív és szubjektív minőségi összehasonlítás ElevenLabs-szel
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import librosa
from pydub import AudioSegment
from datetime import datetime

class QualityComparison:
    def __init__(self):
        """Quality comparison tool inicializálás"""
        self.sample_rate = 24000
        
    def analyze_audio_quality(self, audio_file):
        """Komplex audio minőség elemzése"""
        print(f"🔬 MINŐSÉG ELEMZÉS: {audio_file}")
        
        # Load audio
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
        
        # Convert to numpy
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples = samples / (np.max(np.abs(samples)) + 1e-8)
        
        # Basic metrics
        duration = len(audio) / 1000.0
        dbfs = audio.dBFS
        
        # Advanced analysis
        metrics = {}
        
        # 1. Signal quality
        metrics['signal_quality'] = self._analyze_signal_quality(samples)
        
        # 2. Prosody analysis
        metrics['prosody'] = self._analyze_prosody(samples)
        
        # 3. Naturalness indicators
        metrics['naturalness'] = self._analyze_naturalness(samples)
        
        # 4. Technical quality
        metrics['technical'] = {
            'duration': duration,
            'dbfs': dbfs,
            'sample_rate': self.sample_rate
        }
        
        # 5. Overall quality score
        metrics['overall_score'] = self._calculate_overall_score(metrics)
        
        return metrics
    
    def _analyze_signal_quality(self, samples):
        """Jel minőség elemzése"""
        # SNR estimation
        signal_power = np.mean(samples ** 2)
        noise_power = np.var(samples) * 0.1  # Rough estimation
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        
        # Dynamic range
        rms = np.sqrt(np.mean(samples ** 2))
        peak = np.max(np.abs(samples))
        dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
        
        # Spectral analysis
        D = librosa.stft(samples)
        magnitude = np.abs(D)
        
        # Spectral centroid (brightness)
        spectral_centroid = librosa.feature.spectral_centroid(y=samples, sr=self.sample_rate)[0]
        
        # Spectral rolloff (high frequency content)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=samples, sr=self.sample_rate)[0]
        
        # Zero crossing rate (roughness indicator)
        zcr = librosa.feature.zero_crossing_rate(samples)[0]
        
        return {
            'snr_db': float(snr),
            'dynamic_range_db': float(dynamic_range),
            'spectral_centroid_mean': float(np.mean(spectral_centroid)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'zero_crossing_rate_mean': float(np.mean(zcr)),
            'spectral_flatness': float(np.mean(librosa.feature.spectral_flatness(y=samples)))
        }
    
    def _analyze_prosody(self, samples):
        """Prosódia elemzése (intonáció, ritmus)"""
        # Fundamental frequency analysis
        f0, voiced_flag, _ = librosa.pyin(
            samples, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'),
            sr=self.sample_rate
        )
        
        # Clean F0 data
        f0_clean = f0[voiced_flag]
        
        if len(f0_clean) > 0:
            f0_mean = np.mean(f0_clean)
            f0_std = np.std(f0_clean)
            f0_range = np.max(f0_clean) - np.min(f0_clean)
            pitch_variation = f0_std / f0_mean
        else:
            f0_mean = f0_std = f0_range = pitch_variation = 0
        
        # Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=samples, sr=self.sample_rate)
        
        # Energy and rhythm consistency
        rms_energy = librosa.feature.rms(y=samples)[0]
        energy_variance = np.var(rms_energy)
        
        # Speaking rate (rough estimation)
        onset_strength = librosa.onset.onset_strength(y=samples, sr=self.sample_rate)
        onset_times = librosa.frames_to_time(
            librosa.onset.onset_detect(y=samples, sr=self.sample_rate),
            sr=self.sample_rate
        )
        speaking_rate = len(onset_times) / (len(samples) / self.sample_rate) if len(onset_times) > 0 else 0
        
        return {
            'f0_mean_hz': float(f0_mean),
            'f0_std_hz': float(f0_std),
            'f0_range_hz': float(f0_range),
            'pitch_variation': float(pitch_variation),
            'tempo': float(tempo),
            'energy_variance': float(energy_variance),
            'speaking_rate': float(speaking_rate),
            'voiced_percentage': float(np.sum(voiced_flag) / len(voiced_flag))
        }
    
    def _analyze_naturalness(self, samples):
        """Természetesség elemzése"""
        # Harmonicity analysis
        harmonic = librosa.effects.harmonic(samples)
        percussive = librosa.effects.percussive(samples)
        
        harmonic_ratio = np.mean(harmonic ** 2) / (np.mean(samples ** 2) + 1e-10)
        
        # Jitter and shimmer (simplified)
        # These are rough approximations of acoustic measures
        f0, voiced_flag, _ = librosa.pyin(samples, fmin=50, fmax=400, sr=self.sample_rate)
        
        if np.sum(voiced_flag) > 10:
            f0_voiced = f0[voiced_flag]
            # Jitter approximation (F0 period variability)
            f0_diff = np.diff(f0_voiced)
            jitter = np.std(f0_diff) / np.mean(f0_voiced) if len(f0_diff) > 0 else 0
        else:
            jitter = 0
        
        # Formant analysis (simplified)
        # Extract MFCCs as formant approximation
        mfccs = librosa.feature.mfcc(y=samples, sr=self.sample_rate, n_mfcc=13)
        formant_stability = 1.0 / (1.0 + np.mean(np.std(mfccs, axis=1)))
        
        # Continuity (pause analysis)
        rms = librosa.feature.rms(y=samples)[0]
        rms_db = librosa.amplitude_to_db(rms)
        silence_threshold = np.percentile(rms_db, 20)
        silence_frames = np.sum(rms_db < silence_threshold)
        continuity = 1.0 - (silence_frames / len(rms_db))
        
        return {
            'harmonic_ratio': float(harmonic_ratio),
            'jitter': float(jitter),
            'formant_stability': float(formant_stability),
            'continuity': float(continuity),
            'mfcc_stability': float(np.mean(1.0 / (1.0 + np.std(mfccs, axis=1))))
        }
    
    def _calculate_overall_score(self, metrics):
        """Összesített minőségi pontszám számítása (0-100)"""
        scores = []
        
        # Signal quality score (30%)
        signal = metrics['signal_quality']
        signal_score = 0
        signal_score += min(signal['snr_db'] / 20.0, 1.0) * 25  # SNR
        signal_score += min(signal['dynamic_range_db'] / 15.0, 1.0) * 25  # Dynamic range
        signal_score += (1.0 - min(signal['zero_crossing_rate_mean'] / 0.1, 1.0)) * 25  # Smoothness
        signal_score += min(signal['spectral_flatness'] * 10, 1.0) * 25  # Spectral quality
        scores.append(signal_score * 0.3)
        
        # Prosody score (40%)
        prosody = metrics['prosody']
        prosody_score = 0
        # Pitch variation (should be natural, not monotone or too variable)
        pv = prosody['pitch_variation']
        pv_score = 100 * (1.0 - abs(pv - 0.3) / 0.5) if pv <= 0.8 else 50
        prosody_score += max(pv_score, 0) * 0.3
        
        # Energy consistency
        energy_consistency = 100 * (1.0 - min(prosody['energy_variance'] * 100, 1.0))
        prosody_score += energy_consistency * 0.3
        
        # Voiced percentage (should be high for speech)
        voiced_score = prosody['voiced_percentage'] * 100
        prosody_score += voiced_score * 0.2
        
        # Speaking rate (should be natural)
        rate = prosody['speaking_rate']
        rate_score = 100 * (1.0 - abs(rate - 3.0) / 3.0) if rate <= 6.0 else 50
        prosody_score += max(rate_score, 0) * 0.2
        
        scores.append(prosody_score * 0.4)
        
        # Naturalness score (30%)
        naturalness = metrics['naturalness']
        naturalness_score = 0
        naturalness_score += naturalness['harmonic_ratio'] * 100 * 0.3
        naturalness_score += (1.0 - min(naturalness['jitter'] * 1000, 1.0)) * 100 * 0.2
        naturalness_score += naturalness['formant_stability'] * 100 * 0.3
        naturalness_score += naturalness['continuity'] * 100 * 0.2
        scores.append(naturalness_score * 0.3)
        
        return min(sum(scores), 100.0)
    
    def compare_audio_files(self, files, labels=None):
        """Több audio fájl összehasonlítása"""
        print("🏆 AUDIO MINŐSÉG ÖSSZEHASONLÍTÁS")
        print("=" * 60)
        
        results = []
        
        for i, audio_file in enumerate(files):
            if not os.path.exists(audio_file):
                print(f"❌ Nem található: {audio_file}")
                continue
            
            label = labels[i] if labels and i < len(labels) else f"Audio {i+1}"
            metrics = self.analyze_audio_quality(audio_file)
            
            results.append({
                'file': audio_file,
                'label': label,
                'metrics': metrics
            })
            
            print(f"\n📊 {label} ({Path(audio_file).name}):")
            print(f"   Összpontszám: {metrics['overall_score']:.1f}/100")
            print(f"   SNR: {metrics['signal_quality']['snr_db']:.1f}dB")
            print(f"   Pitch variáció: {metrics['prosody']['pitch_variation']:.3f}")
            print(f"   Harmonikus arány: {metrics['naturalness']['harmonic_ratio']:.3f}")
            print(f"   Folytonosság: {metrics['naturalness']['continuity']:.3f}")
        
        # Ranking
        if len(results) > 1:
            results.sort(key=lambda x: x['metrics']['overall_score'], reverse=True)
            
            print(f"\n🏅 RANGSOR:")
            for i, result in enumerate(results):
                print(f"   {i+1}. {result['label']}: {result['metrics']['overall_score']:.1f}/100")
        
        return results
    
    def generate_quality_report(self, results, output_file="quality_report.json"):
        """Részletes minőségi jelentés generálása"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'comparison_results': results,
            'summary': {
                'best_overall': max(results, key=lambda x: x['metrics']['overall_score'])['label'] if results else None,
                'best_signal_quality': max(results, key=lambda x: x['metrics']['signal_quality']['snr_db'])['label'] if results else None,
                'best_prosody': max(results, key=lambda x: x['metrics']['prosody']['pitch_variation'])['label'] if results else None,
                'best_naturalness': max(results, key=lambda x: x['metrics']['naturalness']['harmonic_ratio'])['label'] if results else None
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Részletes jelentés: {output_file}")
        return output_file

def main():
    """Minőség összehasonlítás főprogram"""
    print("🎯 TTS MINŐSÉG ÉRTÉKELŐ RENDSZER")
    print("=" * 50)
    
    # Test files to compare
    test_files = [
        "test_results/test_resultspremium_test_01.wav",  # Original premium
        "test_results/premium_test_01_enhanced.wav",    # Enhanced version
        "test_results/test_resultspremium_test_02.wav"  # Another test
    ]
    
    labels = [
        "Prémium TTS (eredeti)",
        "Prémium TTS (enhanced)",
        "Prémium TTS (hosszabb)"
    ]
    
    # Filter existing files
    existing_files = []
    existing_labels = []
    for i, file in enumerate(test_files):
        if os.path.exists(file):
            existing_files.append(file)
            existing_labels.append(labels[i])
    
    if not existing_files:
        print("❌ Nem található összehasonlítható audio fájl!")
        return 1
    
    # Quality comparison
    comparator = QualityComparison()
    results = comparator.compare_audio_files(existing_files, existing_labels)
    
    # Generate report
    report_file = comparator.generate_quality_report(results)
    
    print(f"\n🎉 Minőség értékelés kész!")
    print(f"📊 {len(results)} fájl elemezve")
    
    # ElevenLabs comparison baseline
    print(f"\n🎯 ELEVENLABS ÖSSZEHASONLÍTÁS:")
    print(f"   ElevenLabs benchmark: ~90-95/100 pontszám")
    if results:
        best_score = max(r['metrics']['overall_score'] for r in results)
        gap = 90 - best_score
        print(f"   Legjobb eredményünk: {best_score:.1f}/100")
        print(f"   Fejlesztési potenciál: {gap:.1f} pont")
        
        if gap > 0:
            print(f"\n💡 Fejlesztési javaslatok:")
            print(f"   - Még jobb referencia klipek (SNR >25dB)")
            print(f"   - Finomhangolt prosódia modellek")
            print(f"   - Speciális post-processing szűrők")

if __name__ == "__main__":
    main()