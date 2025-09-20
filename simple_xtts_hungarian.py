#!/usr/bin/env python3
"""
Egyszerűsített XTTS v2 Magyar TTS Script
Direct TTS API használattal, PyTorch 2.6 kompatibilis
"""

import os
import sys
import argparse
import torch
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="XTTS v2 Hungarian TTS - Simplified")
    parser.add_argument("--text", required=True, help="Magyar szöveg szintézishez")
    parser.add_argument("--refs", required=True, help="Referencia hangfájl(ok) (vessző elválasztva)")
    parser.add_argument("--out", required=True, help="Kimeneti fájl")
    parser.add_argument("--mp3", action="store_true", help="MP3 kimenet is")
    
    args = parser.parse_args()
    
    print("XTTS v2 Magyar TTS - Egyszerűsített verzió")
    print("=" * 50)
    print(f"Szöveg: {args.text}")
    ref_count = len(args.refs.split(',')) if ',' in args.refs else 1
    print(f"Referenciák: {ref_count} fájl")
    print(f"Kimenet: {args.out}")
    
    try:
        # Import TTS API with compatibility fix
        import TTS
        from TTS.api import TTS as TTSApi
        
        # Set PyTorch weights_only to False for compatibility
        import torch
        
        print("\n🎤 XTTS modell betöltése...")
        
        # Temporary fix for PyTorch 2.6 compatibility
        original_load = torch.load
        def load_with_weights_only_false(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        torch.load = load_with_weights_only_false
        
        try:
            # Initialize TTS
            tts = TTSApi("tts_models/multilingual/multi-dataset/xtts_v2")
            print("✓ Modell betöltve")
            
            # Validate reference files
            ref_files = args.refs.split(',') if ',' in args.refs else [args.refs]
            valid_refs = []
            
            for ref_file in ref_files:
                ref_path = ref_file.strip()
                if os.path.exists(ref_path):
                    valid_refs.append(ref_path)
                    print(f"  ✓ {os.path.basename(ref_path)}")
                else:
                    print(f"  ✗ {ref_path} nem található")
            
            if not valid_refs:
                print("❌ Nem található érvényes referencia fájl!")
                return 1
            
            if len(valid_refs) > 1:
                print(f"🎤 {len(valid_refs)} referencia fájl használva")
                
            print(f"\n🔊 Szintézis: '{args.text}'")
            
            # Ensure output is WAV
            output_path = str(Path(args.out).with_suffix('.wav'))
            
            # Use multiple references or single reference
            speaker_wav = valid_refs if len(valid_refs) > 1 else valid_refs[0]
            
            # Synthesize
            tts.tts_to_file(
                text=args.text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language="hu"
            )
            
            print(f"✅ WAV létrehozva: {output_path}")
            
            # Convert to MP3 if requested
            if args.mp3:
                try:
                    from pydub import AudioSegment
                    mp3_path = str(Path(args.out).with_suffix('.mp3'))
                    audio = AudioSegment.from_wav(output_path)
                    audio.export(mp3_path, format="mp3", bitrate="192k")
                    print(f"✅ MP3 létrehozva: {mp3_path}")
                except ImportError:
                    print("⚠️  pydub nem elérhető, MP3 konverzió kihagyva")
                except Exception as e:
                    print(f"⚠️  MP3 konverzió sikertelen: {e}")
            
            print("\n🎉 Szintézis befejezve!")
            return 0
            
        finally:
            # Restore original torch.load
            torch.load = original_load
            
    except ImportError as e:
        print(f"❌ TTS library hiba: {e}")
        print("Telepítés: pip install TTS")
        return 1
    except Exception as e:
        print(f"❌ Hiba: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())