#!/usr/bin/env python3
"""
Példa script XTTS v2 Magyar TTS használatához
Example script for XTTS v2 Hungarian TTS usage
"""

import os
import sys
from pathlib import Path

# Import our TTS class
from xtts_hungarian_tts import XTTSHungarianTTS

def main():
    print("XTTS v2 Magyar TTS Példa / Hungarian TTS Example")
    print("=" * 50)
    
    # Check if we have example reference files
    current_dir = Path(__file__).parent
    example_refs = list(current_dir.glob("example_voice_*.wav"))
    
    if not example_refs:
        print("⚠️  Nincs példa hangfájl. Kérem, készítsen referencia fájlokat:")
        print("   - example_voice_1.wav (6-12 mp, 24kHz, mono)")
        print("   - example_voice_2.wav (6-12 mp, 24kHz, mono)")
        print("   - example_voice_3.wav (6-12 mp, 24kHz, mono)")
        print()
        print("⚠️  No example voice files. Please create reference files:")
        print("   - example_voice_1.wav (6-12 sec, 24kHz, mono)")
        print("   - example_voice_2.wav (6-12 sec, 24kHz, mono)")
        print("   - example_voice_3.wav (6-12 sec, 24kHz, mono)")
        return 1
    
    print(f"✅ Talált referencia fájlok / Found reference files: {len(example_refs)}")
    for ref in example_refs:
        print(f"   - {ref.name}")
    
    # Example texts
    example_texts = [
        "Jó reggelt! Üdvözlöm a magyar hangszintézis bemutatóján.",
        "A mesterséges intelligencia forradalmasítja a beszédtechnológiát.",
        "Köszönöm a figyelmet, és szép napot kívánok mindenkinek!"
    ]
    
    try:
        # Initialize TTS
        print("\n🚀 XTTS modell betöltése / Loading XTTS model...")
        tts = XTTSHungarianTTS()
        
        # Process each example text
        for i, text in enumerate(example_texts, 1):
            print(f"\n📝 Példa {i} / Example {i}:")
            print(f"   Szöveg / Text: {text}")
            
            output_path = f"example_output_{i}.wav"
            
            print("   🎤 Szintézis / Synthesizing...")
            wav_file = tts.synthesize(
                text=text,
                reference_files=[str(ref) for ref in example_refs],
                output_path=output_path,
                temperature=0.7,
                gpt_cond_len=8
            )
            
            print(f"   ✅ WAV elkészült / WAV created: {wav_file}")
            
            # Convert to MP3
            mp3_file = tts.convert_to_mp3(wav_file)
            if mp3_file:
                print(f"   ✅ MP3 elkészült / MP3 created: {mp3_file}")
            
        print("\n🎉 Minden példa elkészült! / All examples completed!")
        print("\nFájlok / Files:")
        for i in range(1, len(example_texts) + 1):
            wav_path = f"example_output_{i}.wav"
            mp3_path = f"example_output_{i}.mp3"
            if os.path.exists(wav_path):
                print(f"   📄 {wav_path}")
            if os.path.exists(mp3_path):
                print(f"   🎵 {mp3_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Megszakítva / Interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Hiba / Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())