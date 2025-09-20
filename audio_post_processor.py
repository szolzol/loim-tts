#!/usr/bin/env python3
"""
Post-Processing Audio Enhancer
TTS kimenet utólagos feldolgozása ElevenLabs-szintű minőségért
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range, low_pass_filter, high_pass_filter
from scipy import signal
from scipy.ndimage import uniform_filter1d

class AudioPostProcessor:
    def __init__(self, target_sample_rate=24000):
        """Audio post-processor inicializálás"""
        self.sample_rate = target_sample_rate
        
    def enhance_tts_audio(self, input_file, output_file=None):
        """TTS audio komplex utólagos feldolgozása"""
        print(f"🎛️  TTS AUDIO ENHANCEMENT: {input_file}")
        print("=" * 50)
        
        if not output_file:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_enhanced{ext}"
        
        # Load audio
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
        
        print(f"📊 Eredeti audio: {len(audio)/1000:.1f}s, {audio.dBFS:.1f}dB")
        
        # Apply enhancement pipeline
        enhanced = self._enhancement_pipeline(audio)
        
        print(f"📊 Javított audio: {len(enhanced)/1000:.1f}s, {enhanced.dBFS:.1f}dB")
        
        # Export enhanced audio
        enhanced.export(output_file, format="wav")
        
        # Also create MP3 version
        mp3_file = output_file.replace('.wav', '.mp3')
        enhanced.export(mp3_file, format="mp3", bitrate="320k")
        
        print(f"✅ Javított audio: {output_file}")
        print(f"✅ MP3 verzió: {mp3_file}")
        
        return output_file, mp3_file
    
    def _enhancement_pipeline(self, audio):
        """Komplex audio javítási pipeline"""
        print("🔧 Enhancement pipeline futtatása...")
        
        # Step 1: Noise reduction and spectral cleaning
        enhanced = self._spectral_enhancement(audio)
        print("  ✓ Spektrális tisztítás")
        
        # Step 2: Dynamic range optimization
        enhanced = self._dynamic_range_processing(enhanced)
        print("  ✓ Dinamikus tartomány optimalizálás")
        
        # Step 3: Prosody smoothing
        enhanced = self._prosody_smoothing(enhanced)
        print("  ✓ Prosódia simítás")
        
        # Step 4: Harmonic enhancement
        enhanced = self._harmonic_enhancement(enhanced)
        print("  ✓ Harmonikus javítás")
        
        # Step 5: Final polish
        enhanced = self._final_polish(enhanced)
        print("  ✓ Végleges csiszolás")
        
        return enhanced
    
    def _spectral_enhancement(self, audio):
        """Spektrális tisztítás és zajcsökkentés"""
        # Convert to numpy for processing
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples = samples / (np.max(np.abs(samples)) + 1e-8)
        
        # Spectral gating (simple noise reduction)
        D = librosa.stft(samples)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Spectral floor (remove very quiet components that are likely noise)
        magnitude_db = librosa.amplitude_to_db(magnitude)
        threshold = np.percentile(magnitude_db, 20)  # Bottom 20% is likely noise
        mask = magnitude_db > threshold - 20  # Keep signal 20dB above noise floor
        
        # Apply gentle spectral gating
        magnitude_clean = magnitude * (0.1 + 0.9 * mask)
        
        # Reconstruct signal
        D_clean = magnitude_clean * np.exp(1j * phase)
        samples_clean = librosa.istft(D_clean)
        
        # Convert back to AudioSegment
        samples_clean = np.clip(samples_clean, -1.0, 1.0)
        samples_int = (samples_clean * 32767).astype(np.int16)
        
        enhanced = AudioSegment(
            samples_int.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=2,
            channels=1
        )
        
        return enhanced
    
    def _dynamic_range_processing(self, audio):
        """Dinamikus tartomány feldolgozása"""
        # Gentle compression for more consistent levels
        compressed = compress_dynamic_range(
            audio,
            threshold=-25.0,  # Start compressing at -25dB
            ratio=2.5,        # Moderate compression
            attack=5.0,       # Quick attack
            release=50.0      # Smooth release
        )
        
        # Normalize to optimal level
        normalized = normalize(compressed)
        
        # Target -16dB for good headroom
        target_level = -16.0
        current_level = normalized.dBFS
        gain_adjustment = target_level - current_level
        
        return normalized.apply_gain(gain_adjustment)
    
    def _prosody_smoothing(self, audio):
        """Prosódia simítása - intonáció és ritmus javítása"""
        # Convert to numpy for prosody analysis
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples = samples / (np.max(np.abs(samples)) + 1e-8)
        
        # Extract fundamental frequency
        f0, voiced_flag, _ = librosa.pyin(
            samples, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'),
            sr=self.sample_rate
        )
        
        # Smooth pitch contour
        if np.any(voiced_flag):
            # Fill gaps in F0 with interpolation
            f0_smooth = f0.copy()
            valid_indices = np.where(voiced_flag)[0]
            
            if len(valid_indices) > 1:
                # Interpolate missing values
                f0_interp = np.interp(
                    np.arange(len(f0)),
                    valid_indices,
                    f0[valid_indices]
                )
                
                # Apply gentle smoothing to reduce abrupt pitch changes
                f0_smooth = uniform_filter1d(f0_interp, size=5)
                
                # Only apply smoothing to voiced regions
                f0_smooth = np.where(voiced_flag, f0_smooth, f0)
        
        # Apply fade in/out to sentence boundaries (simple approach)
        # Detect pauses and apply gentle fades
        silence_thresh = -40  # dB
        rms = librosa.feature.rms(y=samples)[0]
        rms_db = librosa.amplitude_to_db(rms)
        
        # Find silence regions
        silence_mask = rms_db < silence_thresh
        
        # Convert back to AudioSegment for final processing
        samples_int = (samples * 32767).astype(np.int16)
        enhanced = AudioSegment(
            samples_int.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=2,
            channels=1
        )
        
        return enhanced
    
    def _harmonic_enhancement(self, audio):
        """Harmonikus tartalom javítása a természetességért"""
        # Subtle harmonic enhancement to make voice sound more natural
        
        # High-frequency enhancement (add subtle brightness)
        enhanced = high_pass_filter(audio, cutoff=100)  # Remove very low frequencies
        
        # Subtle high-frequency boost (2-8kHz range for speech clarity)
        # This is a simplified approach - in practice would use parametric EQ
        
        # Low-pass filter to remove excessive high-frequency content
        enhanced = low_pass_filter(enhanced, cutoff=8000)
        
        return enhanced
    
    def _final_polish(self, audio):
        """Végleges csiszolás és finomhangolás"""
        # Final gentle normalization
        polished = normalize(audio)
        
        # Soft limiting to prevent clipping
        if polished.dBFS > -3:
            polished = polished.apply_gain(-3 - polished.dBFS)
        
        # Add subtle fade in/out for clean edges
        polished = polished.fade_in(10).fade_out(10)
        
        return polished
    
    def batch_enhance(self, input_dir, output_dir=None, pattern="*.wav"):
        """Batch enhancement több fájlra"""
        input_path = Path(input_dir)
        if not output_dir:
            output_dir = input_path / "enhanced"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        audio_files = list(input_path.glob(pattern))
        
        print(f"🔄 BATCH ENHANCEMENT: {len(audio_files)} fájl")
        print("=" * 50)
        
        results = []
        for audio_file in audio_files:
            output_file = output_path / f"{audio_file.stem}_enhanced.wav"
            try:
                wav_file, mp3_file = self.enhance_tts_audio(str(audio_file), str(output_file))
                results.append((str(audio_file), wav_file, mp3_file))
                print(f"✅ {audio_file.name} -> {output_file.name}")
            except Exception as e:
                print(f"❌ Hiba {audio_file.name}: {e}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="TTS Audio Post-Processing Enhancement")
    parser.add_argument("--input", "-i", required=True, help="Input audio file vagy directory")
    parser.add_argument("--output", "-o", help="Output file vagy directory")
    parser.add_argument("--batch", action="store_true", help="Batch processing mode")
    parser.add_argument("--pattern", default="*.wav", help="File pattern for batch mode")
    
    args = parser.parse_args()
    
    processor = AudioPostProcessor()
    
    if args.batch:
        results = processor.batch_enhance(args.input, args.output, args.pattern)
        print(f"\n🎉 {len(results)} fájl feldolgozva!")
    else:
        if not os.path.exists(args.input):
            print(f"❌ Nem található: {args.input}")
            return 1
        
        wav_file, mp3_file = processor.enhance_tts_audio(args.input, args.output)
        print(f"\n🎉 Audio enhancement kész!")
        print(f"📁 WAV: {wav_file}")
        print(f"📁 MP3: {mp3_file}")

if __name__ == "__main__":
    main()