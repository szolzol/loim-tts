"""
Continue Fine-Tuning with Combined Dataset
Loads best model from Milliomos training and continues with expanded dataset
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Import training components
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig

# Paths
PROJECT_ROOT = Path("f:/CODE/tts-2")
COMBINED_DATASET = PROJECT_ROOT / "dataset_combined"
OUT_PATH = PROJECT_ROOT / "run" / "training_combined"

# Find best previous model
MILLIOMOS_DIR = PROJECT_ROOT / "run" / "training_milliomos"
PREVIOUS_RUNS = list(MILLIOMOS_DIR.glob("XTTS_*"))

if PREVIOUS_RUNS:
    RESTORE_PATH = max(PREVIOUS_RUNS, key=lambda p: p.stat().st_mtime)
    RESTORE_PATH = RESTORE_PATH / "best_model.pth"
else:
    RESTORE_PATH = None

# Training Configuration
RUN_NAME = f"XTTS_Combined_{datetime.now().strftime('%Y%m%d_%H%M')}"
PROJECT_NAME = "Vago_Combined"
LANGUAGE = "hu"

# Hyperparameters - Optimized for Mel CE improvement
BATCH_SIZE = 3
NUM_EPOCHS = 40  # Additional 40 epochs - more training for better smoothness
LEARNING_RATE = 1.5e-6  # Even lower for fine-tuning - focus on smoothness

# Audio settings
MAX_AUDIO_LENGTH = 22050 * 11  # ~11 seconds max

print("="*70)
print("CONTINUE FINE-TUNING - FOCUS ON MEL CE IMPROVEMENT")
print("István Vágó Voice Clone - Milliomos + Blikk Interview")
print("="*70)
print("\n🎯 TRAINING FOCUS: Improving Audio Smoothness (Mel CE)")
print("   Current Mel CE: 5.046")
print("   Target Mel CE: < 2.5 (excellent quality)")
print("   Strategy: Lower learning rate (1.5e-6) + More epochs (40)")
print("="*70)

if RESTORE_PATH and RESTORE_PATH.exists():
    print(f"\n✅ Found previous model:")
    print(f"   {RESTORE_PATH}")
    print(f"   Size: {RESTORE_PATH.stat().st_size / (1024**3):.2f} GB")
    print(f"\n🔄 Will continue fine-tuning from this checkpoint")
else:
    print(f"\n⚠️  No previous model found!")
    print(f"   Starting from base XTTS-v2 model")
    RESTORE_PATH = None

# Check combined dataset
if not COMBINED_DATASET.exists():
    print(f"\n❌ Combined dataset not found: {COMBINED_DATASET}")
    print(f"   Run: python scripts\\prepare_blikk_dataset.py")
    sys.exit(1)

metadata_file = COMBINED_DATASET / "metadata.csv"
if not metadata_file.exists():
    print(f"\n❌ Metadata not found: {metadata_file}")
    sys.exit(1)

# Count samples
import csv
with open(metadata_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    sample_count = len(list(reader))

print(f"\n📊 Combined dataset:")
print(f"   Location: {COMBINED_DATASET}")
print(f"   Samples: {sample_count}")
print(f"   Estimated duration: ~40 minutes")

print(f"\n⚙️  Training configuration:")
print(f"   Batch size: {BATCH_SIZE}")
print(f"   Epochs: {NUM_EPOCHS} (additional)")
print(f"   Learning rate: {LEARNING_RATE} (reduced for fine-tuning)")
print(f"   Language: {LANGUAGE}")

print(f"\n💾 Output:")
print(f"   Run name: {RUN_NAME}")
print(f"   Location: {OUT_PATH / RUN_NAME}")

print(f"\n" + "="*70)
print("TRAINING STARTED")
print("="*70)
print(f"\n⏱️  Estimated time: ~30-40 minutes")
print(f"📈 Progress will be shown below...")
print(f"⚠️  Press Ctrl+C to stop (model will be saved)\n")

def setup_training():
    """Setup training configuration with combined dataset"""
    
    # Dataset config
    config_dataset = BaseDatasetConfig(
        formatter="coqui",
        dataset_name="vago_combined",
        path=str(COMBINED_DATASET),
        meta_file_train="metadata.csv",
        language=LANGUAGE,
    )
    
    # Evaluation split - with ~310 samples, use 2% for eval
    eval_split_size = 0.02
    
    # Model paths
    model_path = "C:\\Users\\szolzol\\AppData\\Local\\tts\\tts_models--multilingual--multi-dataset--xtts_v2"
    
    # Audio config with compatibility handling
    try:
        audio_config = XttsAudioConfig(
            sample_rate=22050,
            dvae_sample_rate=22050,
            output_sample_rate=24000,
        )
    except TypeError:
        audio_config = XttsAudioConfig(
            sample_rate=22050,
            output_sample_rate=24000,
        )
        # Monkey-patch if needed
        audio_config.dvae_sample_rate = 22050
    
    # Model config
    model_args = GPTArgs(
        max_conditioning_length=143677,  # 6 secs
        min_conditioning_length=66150,   # 3 secs
        debug_loading_failures=False,
        max_wav_length=MAX_AUDIO_LENGTH,
        max_text_length=300,
        mel_norm_file=f"{model_path}\\mel_stats.pth",
        dvae_checkpoint=f"{model_path}\\dvae.pth",
        xtts_checkpoint=f"{model_path}\\model.pth" if not RESTORE_PATH else None,
        tokenizer_file=f"{model_path}\\vocab.json",
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )
    
    # Training config
    config = GPTTrainerConfig(
        output_path=str(OUT_PATH),
        model_args=model_args,
        audio=audio_config,
        run_name=RUN_NAME,
        project_name=PROJECT_NAME,
        run_description="Continue fine-tuning with Milliomos + Blikk interview data",
        dashboard_logger="tensorboard",
        logger_uri=None,
        batch_size=BATCH_SIZE,
        batch_group_size=48,
        eval_batch_size=BATCH_SIZE,
        num_loader_workers=0,
        eval_split_max_size=256,
        eval_split_size=eval_split_size,
        print_step=10,
        plot_step=500,
        log_model_step=500,
        save_step=500,  # Save only every 500 steps instead of 100
        save_n_checkpoints=1,  # Keep only 1 checkpoint instead of 2
        save_checkpoints=True,
        save_all_best=False,  # Don't save all best models, only the latest best
        save_best_after=1000,  # Start saving best model after 1000 steps
        target_loss="loss",
        print_eval=False,  # Reduce console output
        # Optimizer settings
        optimizer="AdamW",
        optimizer_wd_only_on_weights=True,
        optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-5},
        lr_scheduler="MultiStepLR",
        lr_scheduler_params={"milestones": [50000*18, 150000*18, 300000*18], "gamma": 0.5, "last_epoch": -1},
        test_sentences=[],
        datasets=[config_dataset],
        epochs=NUM_EPOCHS,
        lr=LEARNING_RATE,
    )
    
    return config, config_dataset


def main():
    """Main training function"""
    
    # Set encoding
    if sys.platform == 'win32':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Setup
    config, config_dataset = setup_training()
    
    # Initialize model
    model = GPTTrainer.init_from_config(config)
    
    # If restoring, copy vocab.json to output directory
    if RESTORE_PATH and RESTORE_PATH.exists():
        import shutil
        vocab_src = RESTORE_PATH.parent / "vocab.json"
        if vocab_src.exists():
            vocab_dst = OUT_PATH / RUN_NAME / "vocab.json"
            vocab_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vocab_src, vocab_dst)
            print(f"\n✓ Copied vocab.json for inference")
    
    # Load training samples
    train_samples, eval_samples = load_tts_samples(
        [config_dataset],
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )
    
    # Create trainer with restore path
    trainer = Trainer(
        TrainerArgs(
            restore_path=str(RESTORE_PATH) if RESTORE_PATH else None,
            skip_train_epoch=False,
            start_with_eval=True,
            grad_accum_steps=1,
        ),
        config,
        output_path=str(OUT_PATH),
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    
    # Add cleanup callback to delete old checkpoints automatically
    original_save_checkpoint = trainer.save_checkpoint
    
    def save_checkpoint_with_cleanup():
        """Save checkpoint and immediately cleanup old ones"""
        original_save_checkpoint()
        
        # Find and delete old checkpoints (keep only the latest)
        output_folder = OUT_PATH / RUN_NAME
        if output_folder.exists():
            checkpoints = sorted(output_folder.glob("checkpoint_*.pth"))
            # Keep only the most recent checkpoint
            if len(checkpoints) > 1:
                for old_checkpoint in checkpoints[:-1]:
                    try:
                        size_mb = old_checkpoint.stat().st_size / (1024**2)
                        old_checkpoint.unlink()
                        print(f"  🗑️  Deleted old checkpoint: {old_checkpoint.name} ({size_mb:.0f} MB)")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete {old_checkpoint.name}: {e}")
            
            # Keep only the latest best_model (delete older best_model_*.pth files)
            best_models = sorted(output_folder.glob("best_model_*.pth"))
            if len(best_models) > 1:
                for old_best in best_models[:-1]:
                    try:
                        size_mb = old_best.stat().st_size / (1024**2)
                        old_best.unlink()
                        print(f"  🗑️  Deleted old best model: {old_best.name} ({size_mb:.0f} MB)")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete {old_best.name}: {e}")
    
    trainer.save_checkpoint = save_checkpoint_with_cleanup
    
    # Train
    trainer.fit()
    
    print(f"\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"\n📁 Model saved to:")
    print(f"   {OUT_PATH / RUN_NAME}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Generate samples: python scripts\\generate_samples.py")
    print(f"   2. Compare to previous model")
    print(f"   3. Evaluate quality improvement")


if __name__ == "__main__":
    main()
