"""
István Vágó Voice Cloning - XTTS-v2 Fine-tuning
Windows-optimized training script for RTX 4070

Key adaptations:
- Windows path handling
- RTX 4070 optimized batch sizes
- Hungarian language support
- Quality-focused hyperparameters
"""

import os
import sys
import time
import torch
from pathlib import Path
from datetime import datetime

# Add TTS to path if needed
try:
    from trainer import Trainer, TrainerArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    from TTS.tts.datasets import load_tts_samples
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    from TTS.utils.manage import ModelManager
except ImportError as e:
    print(f"❌ Error importing TTS: {e}")
    print("Please ensure TTS is installed: pip install TTS==0.22.0")
    sys.exit(1)

# ========================================
# CONFIGURATION
# ========================================

# Paths (Windows-friendly)
PROJECT_ROOT = Path("f:/CODE/tts-2")
DATASET_PATH = PROJECT_ROOT / "dataset"
OUTPUT_PATH = PROJECT_ROOT / "run" / "training"
CHECKPOINTS_OUT_PATH = OUTPUT_PATH / "XTTS_v2.0_original_model_files"

# Training metadata
RUN_NAME = f"XTTS_Vago_Hungarian_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
PROJECT_NAME = "Vago_Voice_Clone"
DASHBOARD_LOGGER = "tensorboard"

# Training hyperparameters (RTX 4070 optimized)
BATCH_SIZE = 2  # Safe for 12GB VRAM
GRAD_ACUMM_STEPS = 126  # BATCH_SIZE * GRAD_ACUMM_STEPS = 252 (recommended minimum)
NUM_EPOCHS = 25
LEARNING_RATE = 5e-6  # Conservative for better quality
SAVE_STEP = 500
EVAL_STEP = 250

# Quality settings
OPTIMIZER_WD_ONLY_ON_WEIGHTS = True  # Better for single GPU
START_WITH_EVAL = True
NUM_LOADER_WORKERS = 4  # Adjust based on CPU cores

# Language
LANGUAGE = "hu"  # Hungarian

# ========================================
# MODEL CHECKPOINT URLS
# ========================================

# DVAE and mel norm files
DVAE_CHECKPOINT_LINK = "https://huggingface.co/coqui/XTTS-v2/resolve/main/dvae.pth"
MEL_NORM_LINK = "https://huggingface.co/coqui/XTTS-v2/resolve/main/mel_stats.pth"

# XTTS v2.0 checkpoint files
TOKENIZER_FILE_LINK = "https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json"
XTTS_CHECKPOINT_LINK = "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth"


def setup_directories():
    """Create necessary directories"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS_OUT_PATH.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created output directory: {OUTPUT_PATH}")
    print(f"✅ Created checkpoints directory: {CHECKPOINTS_OUT_PATH}")


def download_model_files():
    """Download required XTTS model files if not present"""
    
    print("\n📥 Checking XTTS model files...")
    
    files_to_download = {
        "dvae.pth": DVAE_CHECKPOINT_LINK,
        "mel_stats.pth": MEL_NORM_LINK,
        "vocab.json": TOKENIZER_FILE_LINK,
        "model.pth": XTTS_CHECKPOINT_LINK,
    }
    
    for filename, url in files_to_download.items():
        file_path = CHECKPOINTS_OUT_PATH / filename
        
        if file_path.exists():
            print(f"  ✅ Found: {filename}")
        else:
            print(f"  📥 Downloading: {filename}...")
            try:
                ModelManager._download_model_files([url], str(CHECKPOINTS_OUT_PATH), progress_bar=True)
                print(f"  ✅ Downloaded: {filename}")
            except Exception as e:
                print(f"  ❌ Error downloading {filename}: {e}")
                return False
    
    return True


def check_dataset():
    """Verify dataset exists and is properly formatted"""
    
    print("\n📊 Checking dataset...")
    
    wavs_dir = DATASET_PATH / "wavs"
    metadata_file = DATASET_PATH / "metadata.csv"
    
    if not DATASET_PATH.exists():
        print(f"❌ Error: Dataset directory not found: {DATASET_PATH}")
        print("Run scripts/prepare_dataset.py first!")
        return False
    
    if not metadata_file.exists():
        print(f"❌ Error: metadata.csv not found: {metadata_file}")
        return False
    
    if not wavs_dir.exists():
        print(f"❌ Error: wavs directory not found: {wavs_dir}")
        return False
    
    wav_files = list(wavs_dir.glob("*.wav"))
    if len(wav_files) == 0:
        print(f"❌ Error: No WAV files found in {wavs_dir}")
        return False
    
    print(f"  ✅ Found {len(wav_files)} audio files")
    
    # Check total duration
    import librosa
    total_duration = 0
    for wav_file in wav_files[:5]:  # Sample first 5
        y, sr = librosa.load(wav_file, sr=None)
        total_duration += len(y) / sr
    
    avg_duration = total_duration / min(5, len(wav_files))
    estimated_total = avg_duration * len(wav_files) / 60
    print(f"  ℹ️ Estimated total duration: ~{estimated_total:.1f} minutes")
    
    if estimated_total < 10:
        print("  ⚠️ Warning: Dataset might be too small for optimal results (recommend 15+ minutes)")
    
    return True


def get_speaker_reference_files():
    """Get speaker reference audio files"""
    
    wavs_dir = DATASET_PATH / "wavs"
    wav_files = sorted(list(wavs_dir.glob("*.wav")))
    
    if not wav_files:
        return []
    
    # Use first 3 files as speaker references (or all if less than 3)
    num_refs = min(3, len(wav_files))
    return [str(f) for f in wav_files[:num_refs]]


def check_gpu():
    """Check GPU availability and print info"""
    
    print("\n🖥️ GPU Information:")
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        print(f"  ✅ GPU: {gpu_name}")
        print(f"  ✅ VRAM: {gpu_memory:.1f} GB")
        print(f"  ✅ CUDA Version: {torch.version.cuda}")
        
        # Test CUDA
        try:
            test_tensor = torch.zeros(1).cuda()
            del test_tensor
            torch.cuda.empty_cache()
            print("  ✅ CUDA test: Passed")
        except Exception as e:
            print(f"  ⚠️ CUDA test warning: {e}")
        
        return True
    else:
        print("  ❌ No CUDA GPU detected!")
        print("  ⚠️ Training will be extremely slow on CPU")
        return False


def create_training_config():
    """Create XTTS training configuration"""
    
    print("\n⚙️ Creating training configuration...")
    
    # Dataset configuration
    config_dataset = BaseDatasetConfig(
        formatter="ljspeech",  # Uses pipe-delimited format
        dataset_name="vago_hungarian",
        path=str(DATASET_PATH),
        meta_file_train=str(DATASET_PATH / "metadata.csv"),
        language=LANGUAGE,
    )
    
    # Model arguments
    model_args = GPTArgs(
        max_conditioning_length=132300,  # ~6 seconds at 22050 Hz
        min_conditioning_length=66150,   # ~3 seconds at 22050 Hz
        debug_loading_failures=False,
        max_wav_length=255780,  # ~11.6 seconds
        max_text_length=200,
        mel_norm_file=str(CHECKPOINTS_OUT_PATH / "mel_stats.pth"),
        dvae_checkpoint=str(CHECKPOINTS_OUT_PATH / "dvae.pth"),
        xtts_checkpoint=str(CHECKPOINTS_OUT_PATH / "model.pth"),
        tokenizer_file=str(CHECKPOINTS_OUT_PATH / "vocab.json"),
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )
    
    # Audio configuration
    audio_config = XttsAudioConfig(
        sample_rate=22050,
        dvae_sample_rate=22050,
        output_sample_rate=24000
    )
    
    # Speaker reference files
    speaker_refs = get_speaker_reference_files()
    if not speaker_refs:
        print("  ⚠️ Warning: No speaker reference files found")
    
    # Test sentences for evaluation (Hungarian)
    test_sentences = [
        {
            "text": "Üdvözlöm önöket a kvízműsorban! Kezdjük is a mai adást.",
            "speaker_wav": speaker_refs,
            "language": LANGUAGE,
        },
        {
            "text": "Ez egy rendkívül érdekes kérdés lesz. Figyeljünk együtt, és gondolkodjunk!",
            "speaker_wav": speaker_refs,
            "language": LANGUAGE,
        },
        {
            "text": "Gratulálok a helyes válaszhoz! Fantasztikus teljesítmény volt.",
            "speaker_wav": speaker_refs,
            "language": LANGUAGE,
        }
    ]
    
    # Training configuration
    config = GPTTrainerConfig(
        output_path=str(OUTPUT_PATH),
        model_args=model_args,
        run_name=RUN_NAME,
        project_name=PROJECT_NAME,
        run_description="""
            XTTS-v2 fine-tuning for István Vágó Hungarian voice cloning.
            Optimized for RTX 4070, quality-focused hyperparameters.
        """,
        dashboard_logger=DASHBOARD_LOGGER,
        logger_uri=None,
        audio=audio_config,
        batch_size=BATCH_SIZE,
        batch_group_size=48,
        eval_batch_size=BATCH_SIZE,
        num_loader_workers=NUM_LOADER_WORKERS,
        eval_split_max_size=256,
        print_step=50,
        plot_step=100,
        log_model_step=100,
        save_step=SAVE_STEP,
        save_n_checkpoints=3,  # Keep best 3 checkpoints
        save_checkpoints=True,
        print_eval=True,
        # Optimizer settings
        optimizer="AdamW",
        optimizer_wd_only_on_weights=OPTIMIZER_WD_ONLY_ON_WEIGHTS,
        optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-5},
        lr=LEARNING_RATE,
        lr_scheduler="StepLR",
        lr_scheduler_params={"step_size": 50, "gamma": 0.5, "last_epoch": -1},
        # Epochs
        epochs=NUM_EPOCHS,
        # Test sentences
        test_sentences=test_sentences,
        # Datasets
        datasets=[config_dataset],
    )
    
    print("  ✅ Configuration created")
    return config


def main():
    """Main training pipeline"""
    
    print("=" * 70)
    print("  István Vágó XTTS-v2 Voice Cloning Training")
    print("  Hungarian Quiz Show Host Voice")
    print("=" * 70)
    
    # Setup
    setup_directories()
    
    # Check GPU
    has_gpu = check_gpu()
    if not has_gpu:
        response = input("\n⚠️ No GPU detected. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Download model files
    if not download_model_files():
        print("❌ Failed to download model files. Exiting...")
        return
    
    # Check dataset
    if not check_dataset():
        print("❌ Dataset check failed. Exiting...")
        return
    
    # Create config
    config = create_training_config()
    
    # Initialize model
    print("\n🤖 Initializing XTTS model...")
    try:
        model = GPTTrainer.init_from_config(config)
        print("  ✅ Model initialized")
    except Exception as e:
        print(f"  ❌ Error initializing model: {e}")
        return
    
    # Load training samples
    print("\n📚 Loading training samples...")
    try:
        train_samples, eval_samples = load_tts_samples(
            config.datasets,
            eval_split=True,
            eval_split_max_size=config.eval_split_max_size,
            eval_split_size=config.eval_split_size,
        )
        print(f"  ✅ Training samples: {len(train_samples)}")
        print(f"  ✅ Evaluation samples: {len(eval_samples)}")
        
        # Show first sample
        if train_samples:
            print(f"\n  Sample data point:")
            sample = train_samples[0]
            print(f"    Text: {sample.get('text', 'N/A')[:50]}...")
            print(f"    Audio: {sample.get('audio_file', 'N/A')}")
            
    except Exception as e:
        print(f"  ❌ Error loading samples: {e}")
        return
    
    # Initialize trainer
    print("\n🚀 Initializing trainer...")
    try:
        trainer = Trainer(
            TrainerArgs(
                restore_path=None,
                skip_train_epoch=False,
                start_with_eval=START_WITH_EVAL,
                grad_accum_steps=GRAD_ACUMM_STEPS,
            ),
            config,
            output_path=str(OUTPUT_PATH),
            model=model,
            train_samples=train_samples,
            eval_samples=eval_samples,
        )
        print("  ✅ Trainer initialized")
    except Exception as e:
        print(f"  ❌ Error initializing trainer: {e}")
        return
    
    # Training info
    print("\n" + "=" * 70)
    print("📊 Training Information:")
    print(f"  Run name: {RUN_NAME}")
    print(f"  Output path: {OUTPUT_PATH}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Gradient accumulation steps: {GRAD_ACUMM_STEPS}")
    print(f"  Effective batch size: {BATCH_SIZE * GRAD_ACUMM_STEPS}")
    print(f"  Learning rate: {LEARNING_RATE}")
    print(f"  Epochs: {NUM_EPOCHS}")
    print(f"  Training samples: {len(train_samples)}")
    print(f"  Eval samples: {len(eval_samples)}")
    print("=" * 70)
    
    # Start training
    print("\n🎯 Starting training...")
    print("⏰ This will take several hours. Monitor with TensorBoard:")
    print(f"   tensorboard --logdir {OUTPUT_PATH}")
    print()
    
    try:
        start_time = time.time()
        trainer.fit()
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("✅ Training completed successfully!")
        print(f"⏱️ Total time: {elapsed/3600:.2f} hours")
        print(f"📁 Model saved to: {OUTPUT_PATH}")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        print(f"📁 Checkpoints saved to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        torch.cuda.empty_cache()
        print("\n🧹 Cleaned up GPU memory")


if __name__ == "__main__":
    main()
