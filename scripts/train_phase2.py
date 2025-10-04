"""
Phase 2 Training - Continue from Best Checkpoint
Resume from checkpoint_1500.pth to further improve Mel CE
Target: Mel CE < 2.5 (excellent quality)
"""
import os
from pathlib import Path
import torch
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.xtts import Xtts, XttsAudioConfig

# GPU setup
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
torch_use_cuda_dsa = True

# Configuration
PHASE1_RUN_PATH = Path("run/training_combined/XTTS_Combined_20251003_2208-October-03-2025_10+08PM-fb239cd")
CHECKPOINT_PATH = PHASE1_RUN_PATH / "checkpoint_1500.pth"
OUTPUT_PATH = Path("run/training_phase2")
COMBINED_DATASET_PATH = Path("dataset_combined")
BATCH_SIZE = 3
NUM_EPOCHS = 25  # Additional 25 epochs to reach Mel CE < 2.5
LEARNING_RATE = 1e-6  # Even lower for fine fine-tuning

print("=" * 70)
print("🎯 PHASE 2 TRAINING - CONTINUE FROM CHECKPOINT")
print("=" * 70)
print()
print(f"📦 Phase 1 Status:")
print(f"   Checkpoint: {CHECKPOINT_PATH.name}")
print(f"   Current Mel CE: 3.507")
print(f"   Current Quality: 8.5/10")
print()
print(f"🎯 Phase 2 Target:")
print(f"   Target Mel CE: < 2.5 (excellent)")
print(f"   Target Quality: 9.0/10")
print(f"   Additional Epochs: {NUM_EPOCHS}")
print(f"   Learning Rate: {LEARNING_RATE} (ultra-fine tuning)")
print()

if not CHECKPOINT_PATH.exists():
    print(f"❌ Checkpoint not found: {CHECKPOINT_PATH}")
    exit(1)

# Dataset configuration
dataset_config = BaseDatasetConfig(
    formatter="ljspeech",
    dataset_name="combined",
    path=str(COMBINED_DATASET_PATH),
    meta_file_train="metadata.csv",
    language="hu",
)

# Audio configuration
audio_config = XttsAudioConfig(
    sample_rate=22050,
    dvae_sample_rate=22050,
    output_sample_rate=24000,
)

# Model configuration
config = XttsConfig(
    audio=audio_config,
    batch_size=BATCH_SIZE,
    eval_batch_size=BATCH_SIZE,
    num_loader_workers=4,
    num_eval_loader_workers=4,
    run_eval=True,
    test_sentences=[
        {
            "text": "Jó estét kívánok, kedves nézők! Üdvözlöm Önöket a műsorban!",
            "speaker_wav": str(COMBINED_DATASET_PATH / "wavs" / "milliomos_greeting_001.wav"),
            "language": "hu",
        }
    ],
    # Training parameters - ultra-fine tuning
    lr=LEARNING_RATE,
    epochs=NUM_EPOCHS,
    output_path=str(OUTPUT_PATH),
    datasets=[dataset_config],
    save_step=100,
    print_step=10,
    eval_step=100,
    dashboard_logger="tensorboard",
    # Checkpoint settings
    save_best_after=0,
    save_n_checkpoints=3,
    save_all_best=True,
)

# Load samples
train_samples, eval_samples = load_tts_samples(
    dataset_config,
    eval_split=True,
    eval_split_max_size=config.eval_split_max_size,
    eval_split_size=config.eval_split_size,
)

print(f"📊 Dataset:")
print(f"   Training samples: {len(train_samples)}")
print(f"   Evaluation samples: {len(eval_samples)}")
print()

# Initialize model
print("⏳ Initializing model from Phase 1 checkpoint...")
model = Xtts.init_from_config(config)

# Load checkpoint
print(f"📦 Loading checkpoint: {CHECKPOINT_PATH.name}")
checkpoint = torch.load(str(CHECKPOINT_PATH), map_location="cpu")
model.load_state_dict(checkpoint["model"], strict=False)
print("✅ Checkpoint loaded successfully")
print()

# Trainer arguments
trainer_args = TrainerArgs(
    restore_path=None,  # Don't restore trainer state, just model weights
    skip_train_epoch=False,
    start_with_eval=True,
)

# Initialize trainer
trainer = Trainer(
    args=trainer_args,
    config=config,
    output_path=str(OUTPUT_PATH),
    model=model,
    train_samples=train_samples,
    eval_samples=eval_samples,
)

print("=" * 70)
print("🚀 STARTING PHASE 2 TRAINING")
print("=" * 70)
print()
print("Training will run for approximately 8-10 hours...")
print("Monitor progress with: tensorboard --logdir=run/training_phase2")
print()

# Start training
trainer.fit()

print()
print("=" * 70)
print("✅ PHASE 2 TRAINING COMPLETE!")
print("=" * 70)
print()
print("Check the final results:")
print("  - Best model: run/training_phase2/best_model.pth")
print("  - Logs: run/training_phase2/trainer_0_log.txt")
print()
