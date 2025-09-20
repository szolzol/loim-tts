#!/usr/bin/env python3
"""
XTTS v2 Hungarian TTS Script
Supports multiple reference clips, enhanced conditioning, and high-quality Hungarian speech synthesis.
"""

import argparse
import os
import sys
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import logging

try:
    from TTS.api import TTS
    from TTS.utils.audio import AudioProcessor
except ImportError:
    print("Error: TTS library not found. Install with: pip install TTS")
    sys.exit(1)

try:
    from pydub import AudioSegment
    from pydub.utils import which
except ImportError:
    print("Warning: pydub not found. MP3 conversion will not be available.")
    AudioSegment = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XTTSHungarianTTS:
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2", device: Optional[str] = None):
        """
        Initialize XTTS v2 model for Hungarian TTS.
        
        Args:
            model_name: XTTS model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        self.tts_api = None
        self.model = None
        self.config = None
        self.ap = None
        self.sample_rate = 24000  # XTTS native sample rate
        
        self._load_model(model_name)
    
    def _load_model(self, model_name: str) -> None:
        """Load XTTS model and configuration."""
        try:
            logger.info(f"Loading XTTS model: {model_name}")
            
            # Use TTS API instead of direct model loading
            from TTS.api import TTS
            self.tts_api = TTS(model_name, progress_bar=False)
            
            # For direct model access, use the TTS.api's model
            self.model = self.tts_api.synthesizer.tts_model
            
            if self.device == 'cuda' and torch.cuda.is_available():
                self.model.cuda()
            
            # Initialize audio processor
            self.ap = AudioProcessor(sample_rate=self.sample_rate)
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _validate_audio_file(self, audio_path: str) -> bool:
        """Validate audio file exists and is readable."""
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        try:
            # Try to load audio to validate format
            waveform, sr = torchaudio.load(audio_path)
            logger.debug(f"Audio file {audio_path}: {waveform.shape}, {sr}Hz")
            return True
        except Exception as e:
            logger.error(f"Cannot read audio file {audio_path}: {e}")
            return False
    
    def _preprocess_audio(self, audio_path: str) -> torch.Tensor:
        """
        Preprocess audio file for XTTS conditioning.
        - Load and resample to 24kHz
        - Convert to mono
        - Normalize
        """
        try:
            waveform, sr = torchaudio.load(audio_path)
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample to 24kHz if needed
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
            
            # Normalize to [-1, 1]
            waveform = waveform / torch.max(torch.abs(waveform))
            
            return waveform.squeeze()
            
        except Exception as e:
            logger.error(f"Error preprocessing audio {audio_path}: {e}")
            raise
    
    def get_conditioning_latents(self, 
                               reference_files: List[str],
                               gpt_cond_len: int = 8,
                               gpt_cond_chunk_len: int = 6,
                               max_ref_length: int = 30) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate conditioning latents from multiple reference audio files.
        
        Args:
            reference_files: List of reference audio file paths
            gpt_cond_len: GPT conditioning length (6-8 recommended for Hungarian)
            gpt_cond_chunk_len: GPT conditioning chunk length
            max_ref_length: Maximum reference length in seconds
            
        Returns:
            Tuple of (gpt_cond_latent, speaker_embedding)
        """
        logger.info(f"Generating conditioning latents from {len(reference_files)} files")
        
        # Validate all reference files
        valid_files = []
        for ref_file in reference_files:
            if self._validate_audio_file(ref_file):
                valid_files.append(ref_file)
        
        if not valid_files:
            raise ValueError("No valid reference files found")
        
        try:
            # Get conditioning latents
            gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
                audio_path=valid_files,
                max_ref_length=max_ref_length,
                gpt_cond_len=gpt_cond_len,
                gpt_cond_chunk_len=gpt_cond_chunk_len
            )
            
            logger.info("Conditioning latents generated successfully")
            return gpt_cond_latent, speaker_embedding
            
        except Exception as e:
            logger.error(f"Error generating conditioning latents: {e}")
            raise
    
    def synthesize(self,
                  text: str,
                  reference_files: List[str],
                  output_path: str,
                  language: str = "hu",
                  temperature: float = 0.7,
                  length_penalty: float = 1.0,
                  repetition_penalty: float = 5.0,
                  top_k: int = 50,
                  top_p: float = 0.85,
                  gpt_cond_len: int = 8,
                  gpt_cond_chunk_len: int = 6,
                  enable_text_splitting: bool = True) -> str:
        """
        Synthesize speech from text using Hungarian XTTS.
        """
        if language != "hu":
            logger.warning(f"Language changed from {language} to 'hu' for Hungarian synthesis")
            language = "hu"
        
        logger.info(f"Synthesizing Hungarian text: {text[:50]}...")
        
        # Validate reference files
        valid_files = []
        for ref_file in reference_files:
            if self._validate_audio_file(ref_file):
                valid_files.append(ref_file)
        
        if not valid_files:
            raise ValueError("No valid reference files found")
        
        try:
            # Use TTS API for synthesis
            output_path = str(Path(output_path).with_suffix('.wav'))
            
            # Use the first reference file or combine them
            speaker_wav = valid_files[0] if len(valid_files) == 1 else valid_files
            
            self.tts_api.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language,
                split_sentences=enable_text_splitting
            )
            
            logger.info(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error during synthesis: {e}")
            raise
    
    def convert_to_mp3(self, wav_path: str, mp3_path: Optional[str] = None, bitrate: str = "192k") -> Optional[str]:
        """
        Convert WAV to MP3 using pydub.
        
        Args:
            wav_path: Input WAV file path
            mp3_path: Output MP3 file path (optional)
            bitrate: MP3 bitrate
            
        Returns:
            Path to MP3 file or None if conversion failed
        """
        if AudioSegment is None:
            logger.warning("pydub not available, skipping MP3 conversion")
            return None
        
        if not which("ffmpeg"):
            logger.warning("ffmpeg not found, skipping MP3 conversion")
            return None
        
        try:
            if mp3_path is None:
                mp3_path = str(Path(wav_path).with_suffix('.mp3'))
            
            audio = AudioSegment.from_wav(wav_path)
            audio.export(mp3_path, format="mp3", bitrate=bitrate)
            
            logger.info(f"MP3 saved to: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            logger.error(f"Error converting to MP3: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(
        description="XTTS v2 Hungarian TTS with multiple reference support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python xtts_hungarian_tts.py --text "Jó reggelt, üdv mindenkinek!" --refs ref1.wav --refs ref2.wav --out output.wav
  python xtts_hungarian_tts.py --text "Szép napot!" --refs voice_sample.wav --out greeting.wav --mp3
        """
    )
    
    parser.add_argument("--text", required=True, help="Hungarian text to synthesize")
    parser.add_argument("--refs", action="append", required=True, 
                       help="Reference audio files (can be used multiple times)")
    parser.add_argument("--out", required=True, help="Output file path (WAV)")
    parser.add_argument("--mp3", action="store_true", help="Also create MP3 output")
    parser.add_argument("--mp3-bitrate", default="192k", help="MP3 bitrate (default: 192k)")
    
    # Advanced parameters
    parser.add_argument("--temperature", type=float, default=0.7, 
                       help="Sampling temperature (default: 0.7)")
    parser.add_argument("--length-penalty", type=float, default=1.0,
                       help="Length penalty (default: 1.0)")
    parser.add_argument("--gpt-cond-len", type=int, default=8,
                       help="GPT conditioning length (default: 8)")
    parser.add_argument("--gpt-cond-chunk-len", type=int, default=6,
                       help="GPT conditioning chunk length (default: 6)")
    parser.add_argument("--device", choices=["cuda", "cpu"], 
                       help="Device to use (auto-detect if not specified)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    if not args.refs:
        print("Error: At least one reference file must be provided")
        return 1
    
    for ref_file in args.refs:
        if not os.path.exists(ref_file):
            print(f"Error: Reference file not found: {ref_file}")
            return 1
    
    try:
        # Initialize TTS
        tts = XTTSHungarianTTS(device=args.device)
        
        # Synthesize
        output_wav = tts.synthesize(
            text=args.text,
            reference_files=args.refs,
            output_path=args.out,
            temperature=args.temperature,
            length_penalty=args.length_penalty,
            gpt_cond_len=args.gpt_cond_len,
            gpt_cond_chunk_len=args.gpt_cond_chunk_len
        )
        
        print(f"✓ WAV output: {output_wav}")
        
        # Convert to MP3 if requested
        if args.mp3:
            mp3_path = tts.convert_to_mp3(output_wav, bitrate=args.mp3_bitrate)
            if mp3_path:
                print(f"✓ MP3 output: {mp3_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Detailed error information:")
        return 1

if __name__ == "__main__":
    sys.exit(main())