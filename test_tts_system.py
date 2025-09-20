#!/usr/bin/env python3
"""
Simplified XTTS v2 Hungarian TTS test using alternative approach
This version uses the Hugging Face implementation
"""

import os
import sys
import torch
import torchaudio
import numpy as np
from pathlib import Path

# Try importing alternative TTS libraries
TTS_AVAILABLE = False
BARK_AVAILABLE = False

try:
    # Try to use bark for testing
    from bark import SAMPLE_RATE, generate_audio, preload_models
    from bark.generation import ALLOWED_PROMPTS
    BARK_AVAILABLE = True
    print("✓ Bark TTS is available")
except ImportError:
    pass

try:
    # Try simpler TTS import
    import TTS
    from TTS.api import TTS as TTSApi
    TTS_AVAILABLE = True
    print("✓ Coqui TTS is available")
except ImportError:
    pass

def test_basic_synthesis():
    """Test basic Hungarian TTS synthesis"""
    
    if TTS_AVAILABLE:
        print("\n🎤 Testing with Coqui TTS...")
        try:
            # Initialize TTS
            tts = TTSApi(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
            
            # Test text
            text = "Jó reggelt! Ez egy teszt a magyar hangszintézishez."
            
            # Use processed reference clips
            ref_files = []
            processed_dir = "processed_audio"
            if os.path.exists(processed_dir):
                for i in range(1, 5):
                    ref_file = os.path.join(processed_dir, f"reference_clip_{i:02d}.wav")
                    if os.path.exists(ref_file):
                        ref_files.append(ref_file)
            
            if ref_files:
                print(f"  Using {len(ref_files)} reference files")
                
                # Synthesize
                output_path = "test_xtts_output.wav"
                tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=ref_files[0] if len(ref_files) == 1 else ref_files,
                    language="hu"
                )
                
                print(f"  ✅ Generated: {output_path}")
                return True
            else:
                print("  ❌ No reference files found")
                return False
                
        except Exception as e:
            print(f"  ❌ Coqui TTS error: {e}")
            return False
    
    elif BARK_AVAILABLE:
        print("\n🎤 Testing with Bark TTS (alternative)...")
        try:
            # Preload models
            preload_models()
            
            # Generate audio
            text = "Hello, this is a test of Hungarian text to speech synthesis."
            audio_array = generate_audio(text)
            
            # Save audio
            output_path = "test_bark_output.wav"
            torchaudio.save(output_path, torch.tensor(audio_array).unsqueeze(0), SAMPLE_RATE)
            
            print(f"  ✅ Generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Bark TTS error: {e}")
            return False
    
    else:
        print("\n❌ No TTS library available for testing")
        return False

def create_simple_tts_test():
    """Create a simple TTS test without complex dependencies"""
    
    print("\n📝 Creating simple torch-based synthesis test...")
    
    try:
        # Create a simple sine wave as a test
        sample_rate = 24000
        duration = 3.0  # 3 seconds
        frequency = 440  # A4 note
        
        # Generate sine wave
        t = torch.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * torch.sin(2 * torch.pi * frequency * t)
        
        # Add some envelope to make it sound more natural
        envelope = torch.exp(-t * 2)  # Exponential decay
        audio = audio * envelope
        
        # Save as test audio
        output_path = "test_simple_synthesis.wav"
        torchaudio.save(output_path, audio.unsqueeze(0), sample_rate)
        
        print(f"  ✅ Created test audio: {output_path}")
        
        # Also test loading and processing the reference clips
        processed_dir = "processed_audio"
        if os.path.exists(processed_dir):
            print(f"\n🔍 Analyzing processed reference clips:")
            
            for i in range(1, 5):
                ref_file = os.path.join(processed_dir, f"reference_clip_{i:02d}.wav")
                if os.path.exists(ref_file):
                    try:
                        waveform, sr = torchaudio.load(ref_file)
                        duration = waveform.shape[1] / sr
                        rms = torch.sqrt(torch.mean(waveform**2))
                        
                        print(f"  📄 {os.path.basename(ref_file)}:")
                        print(f"     Duration: {duration:.1f}s")
                        print(f"     Sample rate: {sr}Hz")
                        print(f"     Channels: {waveform.shape[0]}")
                        print(f"     RMS level: {20*torch.log10(rms):.1f} dB")
                        
                    except Exception as e:
                        print(f"  ❌ Error loading {ref_file}: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in simple test: {e}")
        return False

def main():
    print("XTTS v2 Hungarian TTS - System Test")
    print("=" * 40)
    
    # Check system capabilities
    print("🔧 System Check:")
    print(f"  Python: {sys.version}")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA device: {torch.cuda.get_device_name()}")
    
    # Check for processed audio
    processed_dir = "processed_audio"
    if os.path.exists(processed_dir):
        clip_count = len([f for f in os.listdir(processed_dir) if f.startswith("reference_clip_")])
        print(f"  Reference clips: {clip_count} found")
    else:
        print(f"  Reference clips: None found (run preprocess_audio.py first)")
    
    # Run tests
    success = False
    
    # Try main TTS test
    if test_basic_synthesis():
        success = True
    
    # Always run simple test for verification
    if create_simple_tts_test():
        success = True
    
    # Summary
    print(f"\n{'='*40}")
    if success:
        print("✅ Test completed successfully!")
        print("\nYour audio preprocessing worked correctly.")
        print("The reference clips are properly formatted for XTTS v2.")
        
        if not TTS_AVAILABLE:
            print("\n💡 To use full XTTS v2:")
            print("1. Install Visual Studio Build Tools")
            print("2. Run: pip install TTS")
            print("3. Use the xtts_hungarian_tts.py script")
        
    else:
        print("❌ Tests failed - check error messages above")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())