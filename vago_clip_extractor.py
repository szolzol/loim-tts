#!/usr/bin/env python3
"""
Intelligens Vágó István klip kivágó
ElevenLabs minőség elérése érdekében
"""

import os
import sys
import librosa
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import torchaudio
import torch
from scipy import signal
from typing import List, Tuple, Dict
import json

class VagoClipExtractor:
    def __init__(self, source_file: str = "vago_vagott.mp3"):
        """Vágó István klip kivágó inicializálása"""
        self.source_file = source_file
        self.output_dir = Path("processed_audio")
        self.output_dir.mkdir(exist_ok=True)
        
        # Audio analízis paraméterei
        self.min_clip_duration = 3.0  # Minimum klip hossz (másodperc)
        self.max_clip_duration = 15.0  # Maximum klip hossz
        self.target_duration = 8.0     # Ideális klip hossz
        self.min_snr = 15.0           # Minimum jel-zaj arány (dB)
        self.min_rms_energy = 0.02    # Minimum energia szint
        
    def analyze_audio_quality(self, audio: np.ndarray, sr: int) -> Dict:
        """Részletes audio minőség analízis"""
        
        # Alapvető metrikák
        duration = len(audio) / sr
        rms_energy = np.sqrt(np.mean(audio**2))
        peak_amplitude = np.max(np.abs(audio))
        dynamic_range = peak_amplitude - np.min(np.abs(audio[audio != 0]))
        
        # SNR számítás spektrális módszerrel
        snr_db = self._calculate_snr(audio, sr)
        
        # Pitch stabilitás
        pitch_stability = self._calculate_pitch_stability(audio, sr)
        
        # Spektrális tisztaság
        spectral_clarity = self._calculate_spectral_clarity(audio, sr)
        
        # Háttérzaj szint
        noise_level = self._estimate_noise_level(audio, sr)
        
        # Összesített minőségi pontszám (0-100)
        quality_score = self._calculate_quality_score(
            snr_db, rms_energy, pitch_stability, spectral_clarity, noise_level
        )
        
        return {
            'duration': duration,
            'rms_energy': rms_energy,
            'peak_amplitude': peak_amplitude,
            'dynamic_range': dynamic_range,
            'snr_db': snr_db,
            'pitch_stability': pitch_stability,
            'spectral_clarity': spectral_clarity,
            'noise_level': noise_level,
            'quality_score': quality_score
        }
    
    def _calculate_snr(self, audio: np.ndarray, sr: int) -> float:
        """Jel-zaj arány számítása fejlett spektrális módszerrel"""
        
        # Spektrogramm számítás
        f, t, Sxx = signal.spectrogram(audio, sr, nperseg=2048)
        
        # Beszéd frekvencia tartomány: 85Hz - 8000Hz
        speech_mask = (f >= 85) & (f <= 8000)
        noise_mask = f > 8000  # Magasabb frekvenciák zajnak
        
        # Átlagos teljesítmény
        speech_power = np.mean(Sxx[speech_mask, :])
        noise_power = np.mean(Sxx[noise_mask, :]) if np.any(noise_mask) else np.percentile(Sxx[speech_mask, :], 5)
        
        # SNR dB-ben
        snr_ratio = speech_power / (noise_power + 1e-10)
        return 10 * np.log10(snr_ratio)
    
    def _calculate_pitch_stability(self, audio: np.ndarray, sr: int) -> float:
        """Pitch stabilitás számítása"""
        try:
            # F0 extrakció
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
            )
            
            # Csak a hangzó részek
            voiced_f0 = f0[voiced_flag]
            
            if len(voiced_f0) < 10:
                return 0.0
            
            # Stabilitás = 1 - (std / mean)
            f0_mean = np.mean(voiced_f0)
            f0_std = np.std(voiced_f0)
            stability = max(0.0, 1.0 - (f0_std / f0_mean))
            
            return stability
            
        except Exception:
            return 0.5  # Default érték hiba esetén
    
    def _calculate_spectral_clarity(self, audio: np.ndarray, sr: int) -> float:
        """Spektrális tisztaság számítása"""
        
        # Spektrális centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        
        # Spektrális rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, roll_percent=0.85)[0]
        
        # Spektrális kontrast
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        contrast_mean = np.mean(spectral_contrast)
        
        # Harmonicitás (MFCC alapú közelítés)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        harmonic_clarity = 1.0 / (1.0 + np.std(mfccs[1:4]))  # Első néhány MFCC
        
        # Kombinált tisztaság (0-1)
        clarity = (
            0.3 * min(contrast_mean / 10.0, 1.0) +
            0.3 * harmonic_clarity +
            0.4 * min(np.mean(spectral_centroids) / 3000.0, 1.0)
        )
        
        return clarity
    
    def _estimate_noise_level(self, audio: np.ndarray, sr: int) -> float:
        """Háttérzaj szint becslése"""
        
        # Csend részek detektálása (alacsony energia)
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        
        # Frame-enkénti energia
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        frame_energies = np.mean(frames**2, axis=0)
        
        # Legalacsonyabb 10% energia = zaj szint
        noise_level = np.percentile(frame_energies, 10)
        
        return float(np.sqrt(noise_level))
    
    def _calculate_quality_score(self, snr_db: float, rms_energy: float, 
                                pitch_stability: float, spectral_clarity: float, 
                                noise_level: float) -> float:
        """Összesített minőségi pontszám (0-100)"""
        
        # SNR pontszám (0-30)
        snr_score = min(snr_db, 30.0)
        
        # Energia pontszám (0-20)
        energy_score = min(rms_energy * 500, 20.0)  # 0.04 RMS = 20 pont
        
        # Pitch stabilitás pontszám (0-25)
        pitch_score = pitch_stability * 25.0
        
        # Spektrális tisztaság pontszám (0-20)
        clarity_score = spectral_clarity * 20.0
        
        # Zaj büntetés (0-5)
        noise_penalty = min(noise_level * 100, 5.0)
        
        # Összes pontszám
        total_score = snr_score + energy_score + pitch_score + clarity_score - noise_penalty
        
        return max(0.0, min(100.0, total_score))
    
    def find_best_segments(self, target_count: int = 8) -> List[Tuple[float, float, float]]:
        """Legjobb audio szegmensek megkeresése"""
        
        print(f"🔍 Audio analízis: {self.source_file}")
        
        # Audio betöltés
        audio, sr = librosa.load(self.source_file, sr=None)
        total_duration = len(audio) / sr
        
        print(f"📊 Teljes hossz: {total_duration:.1f} másodperc")
        print(f"📡 Sample rate: {sr} Hz")
        
        # Ablak paraméterek
        window_duration = self.target_duration
        step_duration = 2.0  # 2 másodpercenként próbálunk
        
        segments = []
        
        # Végigszkenneljük az egész fájlt
        current_time = 0.0
        while current_time + window_duration <= total_duration:
            
            # Aktuális szegmens kivágása
            start_sample = int(current_time * sr)
            end_sample = int((current_time + window_duration) * sr)
            segment_audio = audio[start_sample:end_sample]
            
            # Minőség analízis
            quality_metrics = self.analyze_audio_quality(segment_audio, sr)
            
            # Szegmens hozzáadása ha megfelel a kritériumoknak
            if (quality_metrics['snr_db'] >= self.min_snr and 
                quality_metrics['rms_energy'] >= self.min_rms_energy):
                
                segments.append((
                    current_time, 
                    current_time + window_duration,
                    quality_metrics['quality_score']
                ))
                
                print(f"   ✅ {current_time:.1f}s-{current_time + window_duration:.1f}s: "
                      f"Q={quality_metrics['quality_score']:.1f}, "
                      f"SNR={quality_metrics['snr_db']:.1f}dB, "
                      f"RMS={quality_metrics['rms_energy']:.3f}")
            else:
                print(f"   ❌ {current_time:.1f}s-{current_time + window_duration:.1f}s: "
                      f"SNR={quality_metrics['snr_db']:.1f}dB, "
                      f"RMS={quality_metrics['rms_energy']:.3f}")
            
            current_time += step_duration
        
        # Legjobb szegmensek kiválasztása
        segments.sort(key=lambda x: x[2], reverse=True)  # Minőség szerint rendezés
        best_segments = segments[:target_count]
        
        print(f"\n🎯 {len(best_segments)} legjobb szegmens kiválasztva!")
        
        return best_segments
    
    def extract_clips(self, target_count: int = 8):
        """Klipek kivágása és mentése"""
        
        # Legjobb szegmensek megkeresése
        segments = self.find_best_segments(target_count)
        
        if not segments:
            print("❌ Nem találhatók megfelelő minőségű szegmensek!")
            return
        
        # Audio betöltés
        audio, sr = librosa.load(self.source_file, sr=None)
        
        print(f"\n🎬 Klipek kivágása...")
        
        extracted_clips = []
        
        for i, (start_time, end_time, quality_score) in enumerate(segments, 1):
            
            # Szegmens kivágása
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            segment_audio = audio[start_sample:end_sample]
            
            # Fájlnév generálás
            output_filename = f"vago_premium_clip_{i:02d}_q{quality_score:.0f}.wav"
            output_path = self.output_dir / output_filename
            
            # Mentés
            segment_tensor = torch.from_numpy(segment_audio).unsqueeze(0)
            torchaudio.save(str(output_path), segment_tensor, sr)
            
            extracted_clips.append(str(output_path))
            
            print(f"   💾 {output_filename}: {start_time:.1f}s-{end_time:.1f}s "
                  f"(Q={quality_score:.1f})")
        
        print(f"\n✅ {len(extracted_clips)} prémium klip elkészült!")
        print(f"📁 Mentési hely: {self.output_dir}")
        
        # Klipek összesítő jelentése
        self._generate_clip_report(extracted_clips)
        
        return extracted_clips
    
    def _generate_clip_report(self, clips: List[str]):
        """Klipek minőségi jelentésének generálása"""
        
        report = {
            'timestamp': str(np.datetime64('now')),
            'source_file': self.source_file,
            'clips': []
        }
        
        print(f"\n📊 MINŐSÉGI JELENTÉS")
        print("=" * 50)
        
        for clip_path in clips:
            # Audio betöltés és analízis
            audio, sr = torchaudio.load(clip_path)
            audio_np = audio.squeeze().numpy()
            
            metrics = self.analyze_audio_quality(audio_np, sr)
            
            clip_info = {
                'filename': Path(clip_path).name,
                'path': clip_path,
                'metrics': metrics
            }
            
            report['clips'].append(clip_info)
            
            print(f"🎵 {Path(clip_path).name}")
            print(f"   ⏱️ Időtartam: {metrics['duration']:.1f}s")
            print(f"   📡 SNR: {metrics['snr_db']:.1f}dB")
            print(f"   ⚡ RMS energia: {metrics['rms_energy']:.3f}")
            print(f"   🎯 Pitch stabilitás: {metrics['pitch_stability']:.2f}")
            print(f"   🌊 Spektrális tisztaság: {metrics['spectral_clarity']:.2f}")
            print(f"   🏆 Minőségi pontszám: {metrics['quality_score']:.1f}/100")
            print()
        
        # Jelentés mentése
        report_path = self.output_dir / "vago_clips_quality_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📋 Részletes jelentés mentve: {report_path}")

def main():
    """Főprogram"""
    
    print("🎙️ Vágó István Prémium Klip Kivágó")
    print("=" * 40)
    
    # Ellenőrzés: létezik-e a forrásfájl
    source_file = "vago_vagott.mp3"
    if not os.path.exists(source_file):
        print(f"❌ Forrásfájl nem található: {source_file}")
        return
    
    # Kivágó példány
    extractor = VagoClipExtractor(source_file)
    
    # Klipek kivágása
    clips = extractor.extract_clips(target_count=8)
    
    if clips:
        print(f"\n🎉 SIKER! {len(clips)} prémium klip elkészült!")
        print("🚀 Ezek használhatók ElevenLabs minőségű TTS-hez!")
    else:
        print("❌ Nem sikerült megfelelő klipeket kivágni.")

if __name__ == "__main__":
    main()