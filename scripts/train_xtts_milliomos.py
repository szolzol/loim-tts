"""
Train XTTS-v2 on the Milliomos dataset
Optimized for RTX 4070, Hungarian language, quiz show prosody
"""

import os
import sys
import torch
from pathlib import Path
from datetime import datetime

# Add TTS to path
try:
    from trainer import Trainer, TrainerArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    from TTS.tts.datasets import load_tts_samples
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    from TTS.utils.manage import ModelManager
except ImportError as e:
    print(f"❌ Error importing TTS: {e}")
    print("Please install: pip install TTS==0.22.0")
    sys.exit(1)

# ========================================
# CONFIGURATION
# ========================================

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"
OUTPUT_PATH = PROJECT_ROOT / "run" / "training_milliomos"
CHECKPOINTS_OUT_PATH = OUTPUT_PATH / "XTTS_v2.0_original_model_files"

# Training settings
RUN_NAME = f"XTTS_Vago_Milliomos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
PROJECT_NAME = "Vago_Milliomos_QuizShow"
DASHBOARD_LOGGER = "tensorboard"

# Hyperparameters (RTX 4070 - 12GB VRAM)
BATCH_SIZE = 3  # Slightly larger for 15min dataset
GRAD_ACUMM_STEPS = 84  # 3 * 84 = 252 effective batch
NUM_EPOCHS = 30  # More epochs for quiz show prosody
MAX_AUDIO_LENGTH = 255995  # ~11.6s at 22050Hz
LANGUAGE = "hu"  # Hungarian

# Learning rates
LR = 5e-06  # Conservative for fine-tuning
LR_SCHEDULER = "StepLR"
LR_STEP_SIZE = 10
LR_GAMMA = 0.75

# Audio config
SAMPLE_RATE = 22050

# GPU settings
USE_CUDA = torch.cuda.is_available()
if not USE_CUDA:
    print("⚠ CUDA not available! Training will be VERY slow.")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(0)


def download_xtts_checkpoint():
    """Download XTTS-v2 base model if not present"""
    print("\n" + "="*60)
    print("DOWNLOADING BASE MODEL")
    print("="*60)
    
    if CHECKPOINTS_OUT_PATH.exists() and len(list(CHECKPOINTS_OUT_PATH.glob("*"))) > 0:
        print(f"✓ Base model already exists at {CHECKPOINTS_OUT_PATH}")
        return
    
    CHECKPOINTS_OUT_PATH.mkdir(parents=True, exist_ok=True)
    
    print("Downloading XTTS-v2 base model...")
    manager = ModelManager()
    
    # Download the base model
    model_path = manager.download_model("tts_models/multilingual/multi-dataset/xtts_v2")
    
    print(f"✓ Model downloaded to: {model_path}")
    print(f"✓ Checkpoints directory: {CHECKPOINTS_OUT_PATH}")


def verify_dataset():
    """Verify dataset exists and has correct structure"""
    print("\n" + "="*60)
    print("DATASET VERIFICATION")
    print("="*60)
    
    metadata_file = DATASET_PATH / "metadata.csv"
    
    if not DATASET_PATH.exists():
        print(f"❌ Dataset directory not found: {DATASET_PATH}")
        return False
    
    if not metadata_file.exists():
        print(f"❌ metadata.csv not found: {metadata_file}")
        return False
    
    # Count files
    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        clip_count = len(lines) - 1  # Subtract header
    
    print(f"✓ Dataset found: {DATASET_PATH}")
    print(f"✓ Metadata file: {clip_count} entries")
    
    # Check audio files
    audio_dirs = [d for d in DATASET_PATH.iterdir() if d.is_dir()]
    print(f"✓ Categories: {len(audio_dirs)}")
    for d in sorted(audio_dirs):
        wav_count = len(list(d.glob("*.wav")))
        print(f"  - {d.name}: {wav_count} clips")
    
    return True


def setup_training():
    """Setup training configuration"""
    print("\n" + "="*60)
    print("TRAINING CONFIGURATION")
    print("="*60)
    
    # Dataset config
    config_dataset = BaseDatasetConfig(
        formatter="coqui",
        dataset_name="vago_milliomos",
        path=str(DATASET_PATH),
        meta_file_train="metadata.csv",
        language=LANGUAGE,
    )
    
    # Audio config
    audio_config = XttsAudioConfig(
        sample_rate=SAMPLE_RATE,
        dvae_sample_rate=SAMPLE_RATE,
        output_sample_rate=SAMPLE_RATE,
    )
    
    # GPT model config
    config = GPTTrainerConfig(
        output_path=str(OUTPUT_PATH),
        model_args=GPTArgs(
            max_conditioning_length=132300,  # 6 seconds of conditioning audio
            min_conditioning_length=66150,   # 3 seconds minimum
            debug_loading_failures=False,
            max_wav_length=MAX_AUDIO_LENGTH,  # Maximum ~11.6 seconds
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
        ),
        audio=audio_config,
        batch_size=BATCH_SIZE,
        batch_group_size=48,
        eval_batch_size=BATCH_SIZE,
        num_loader_workers=0,  # Windows-friendly
        eval_split_max_size=256,
        eval_split_size=0.01,
        print_step=50,
        plot_step=100,
        log_model_step=1000,
        save_step=5000,
        save_n_checkpoints=2,
        save_checkpoints=True,
        target_loss="loss",
        print_eval=False,
        run_eval=True,
        test_sentences=[
            # Quiz show phrases for testing
            {"text": "Gratulálok! Helyes válasz!", "speaker_wav": "greeting/greeting_001.wav", "language": LANGUAGE},
            {"text": "Jöjjön a következő kérdés!", "speaker_wav": "transition/transition_001.wav", "language": LANGUAGE},
            {"text": "Ez egy nehéz kérdés, gondolkodjon!", "speaker_wav": "tension/tension_001.wav", "language": LANGUAGE},
            {"text": "Nagyszerű teljesítmény!", "speaker_wav": "excitement/excitement_001.wav", "language": LANGUAGE},
        ],
        epochs=NUM_EPOCHS,
        batch_size=BATCH_SIZE,
        grad_acumm_steps=GRAD_ACUMM_STEPS,
        seq_len=1,
        lr=LR,
        lr_scheduler=LR_SCHEDULER,
        lr_scheduler_params={"step_size": LR_STEP_SIZE, "gamma": LR_GAMMA},
        test_sentences_file="",
        mel_norm_file="",
        datasets=[config_dataset],
        temperature=0.2,
        weighted_loss_attrs={
            "wav_loss": 1.0,
        },
        weighted_loss_multipliers={
            "text_ce": 0.01,
            "wav_ce": 1.0,
        },
        gpt_max_audio_tokens=605,
        gpt_max_text_tokens=402,
        gpt_max_prompt_tokens=70,
        gpt_layers=30,
        gpt_n_model_channels=1024,
        gpt_n_heads=16,
        gpt_number_text_tokens=6681,
        gpt_start_text_token=None,
        gpt_num_audio_tokens=1026,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )
    
    # Summary
    print(f"\nRun name: {RUN_NAME}")
    print(f"Project: {PROJECT_NAME}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Language: {LANGUAGE}")
    print(f"\nTraining parameters:")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Gradient accumulation: {GRAD_ACUMM_STEPS}")
    print(f"  Effective batch: {BATCH_SIZE * GRAD_ACUMM_STEPS}")
    print(f"  Epochs: {NUM_EPOCHS}")
    print(f"  Learning rate: {LR}")
    print(f"  Max audio length: {MAX_AUDIO_LENGTH/SAMPLE_RATE:.2f}s")
    print(f"\nGPU: {torch.cuda.get_device_name(0) if USE_CUDA else 'CPU'}")
    if USE_CUDA:
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    return config


def estimate_training_time(config):
    """Estimate training duration"""
    print("\n" + "="*60)
    print("TIME ESTIMATION")
    print("="*60)
    
    # Load dataset to count samples
    metadata_file = DATASET_PATH / "metadata.csv"
    with open(metadata_file, 'r', encoding='utf-8') as f:
        sample_count = len(f.readlines()) - 1  # Subtract header
    
    # Calculate steps
    effective_batch = BATCH_SIZE * GRAD_ACUMM_STEPS
    steps_per_epoch = sample_count / effective_batch
    total_steps = steps_per_epoch * NUM_EPOCHS
    
    # Estimate time (rough approximation)
    # RTX 4070: ~1.5-2 seconds per step with batch=3, grad_accum=84
    seconds_per_step = 1.8
    total_seconds = total_steps * seconds_per_step
    hours = total_seconds / 3600
    
    print(f"Dataset: {sample_count} samples")
    print(f"Effective batch size: {effective_batch}")
    print(f"Steps per epoch: {steps_per_epoch:.1f}")
    print(f"Total steps: {total_steps:.0f}")
    print(f"\nEstimated duration: {hours:.1f} hours ({total_seconds/60:.0f} minutes)")
    print(f"Expected finish: {datetime.now().strftime('%Y-%m-%d')} ~{int((datetime.now().timestamp() + total_seconds) % 86400 / 3600):02d}:00")


def main():
    """Main training entry point"""
    print("="*60)
    print("XTTS-V2 FINE-TUNING - ISTVÁN VÁGÓ MILLIOMOS")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify dataset
    if not verify_dataset():
        print("\n❌ Dataset verification failed!")
        sys.exit(1)
    
    # Download base model
    download_xtts_checkpoint()
    
    # Setup configuration
    config = setup_training()
    
    # Estimate time
    estimate_training_time(config)
    
    # Confirm
    print("\n" + "="*60)
    print("Ready to start training!")
    print("="*60)
    print("\nTensorBoard: Run in another terminal:")
    print(f"  tensorboard --logdir {OUTPUT_PATH}")
    print(f"\nCheckpoints will be saved every 5000 steps to:")
    print(f"  {OUTPUT_PATH}")
    
    response = input("\nStart training? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled.")
        sys.exit(0)
    
    # Initialize and train
    print("\n" + "="*60)
    print("TRAINING STARTED")
    print("="*60)
    
    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # Initialize trainer
    trainer = Trainer(
        TrainerArgs(
            restore_path=None,
            skip_train_epoch=False,
            continue_path=str(OUTPUT_PATH) if (OUTPUT_PATH / "checkpoint.pth").exists() else None,
        ),
        config=config,
        output_path=str(OUTPUT_PATH),
        model=GPTTrainer,
        train_samples=load_tts_samples(
            config.datasets,
            eval_split=False,
            eval_split_max_size=config.eval_split_max_size,
            eval_split_size=config.eval_split_size,
        ),
        eval_samples=load_tts_samples(
            config.datasets,
            eval_split=True,
            eval_split_max_size=config.eval_split_max_size,
            eval_split_size=config.eval_split_size,
        ),
    )
    
    # Start training
    trainer.fit()
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE!")
    print("="*60)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nModel saved to: {OUTPUT_PATH}")
    print(f"\nTest the model:")
    print(f"  python scripts\\zero_shot_inference.py --model_path {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
