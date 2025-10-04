"""
Continue Combined Training - Phase 2
Resume from checkpoint_1500.pth to further improve Mel CE
Target: Mel CE < 2.5 (excellent quality)
"""

import os
from pathlib import Path
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig

# Configuration
OUTPUT_PATH = "run/training_combined_phase2"
DATASET_PATH = "dataset_combined"  # Combined Milliomos + Blikk
RESUME_CHECKPOINT = "run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_01+28PM-fb239cd/checkpoint_1900.pth"

# Training parameters - PHASE 2 (more aggressive)
BATCH_SIZE = 3  # Keep same for memory
NUM_EPOCHS = 30  # Additional 30 epochs
LEARNING_RATE = 1e-6  # Even lower for fine-tuning (was 1.5e-6)
EVAL_SPLIT_SIZE = 0.15

print("=" * 70)
print("🎯 COMBINED TRAINING - PHASE 2 (RESUMED)")
print("=" * 70)
print()
print("📊 Current Status:")
print("   • Starting Mel CE: 3.507 (Phase 1 end)")
print("   • Step 1900 Mel CE: 3.008 (Phase 2 progress)")
print("   • Target Mel CE: < 2.5 (excellent quality)")
print("   • Remaining improvement needed: -16.8%")
print()
print("🔧 Phase 2 Configuration:")
print(f"   • Resuming from: checkpoint_1900.pth (step 1900)")
print(f"   • Learning Rate: {LEARNING_RATE} (ultra-low for fine refinement)")
print(f"   • Additional Epochs: {NUM_EPOCHS}")
print(f"   • Focus: Ultra-smooth audio (Mel CE)")
print(f"   • Auto-cleanup: Enabled (saves disk space)")
print()
print("=" * 70)
print()

# Verify checkpoint exists
if not Path(RESUME_CHECKPOINT).exists():
    print(f"❌ ERROR: Checkpoint not found!")
    print(f"   Looking for: {RESUME_CHECKPOINT}")
    exit(1)

print(f"✅ Found checkpoint: {Path(RESUME_CHECKPOINT).name}")
print()

# RUN_NAME for this session
RUN_NAME = "XTTS_Combined_Phase2"

# DVAE checkpoint
DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth"
MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth"

# Download manager
CHECKPOINTS_OUT_PATH = Path("models/")
CHECKPOINTS_OUT_PATH.mkdir(parents=True, exist_ok=True)

def download_if_needed(url, filename):
    filepath = CHECKPOINTS_OUT_PATH / filename
    if not filepath.exists():
        print(f"   Downloading {filename}...")
        import requests
        response = requests.get(url)
        filepath.write_bytes(response.content)
        print(f"   ✅ Downloaded: {filename}")
    else:
        print(f"   ✅ Found: {filename}")
    return str(filepath)

# Download if needed
print("📥 Checking DVAE checkpoint...")

DVAE_CHECKPOINT = download_if_needed(DVAE_CHECKPOINT_LINK, "dvae.pth")
MEL_NORM_FILE = download_if_needed(MEL_NORM_LINK, "mel_stats.pth")

print()

# Dataset configuration
print("📂 Loading dataset...")
config_dataset = BaseDatasetConfig(
    formatter="coqui",
    dataset_name="combined_milliomos_blikk",
    path=DATASET_PATH,
    meta_file_train="metadata.csv",
    language="hu",
)

# Model paths from original training
model_path = "C:\\Users\\szolzol\\AppData\\Local\\tts\\tts_models--multilingual--multi-dataset--xtts_v2"

# Audio config
audio_config = XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000)

# XTTS GPT configuration - Phase 2 with lower LR
print("🔧 Configuring XTTS GPT Trainer...")
model_args = GPTArgs(
    max_conditioning_length=143677,  # 6 secs
    min_conditioning_length=66150,   # 3 secs
    debug_loading_failures=False,
    max_wav_length=255995,
    max_text_length=300,
    mel_norm_file=MEL_NORM_FILE,
    dvae_checkpoint=DVAE_CHECKPOINT,
    xtts_checkpoint=None,  # Will be loaded from resume
    tokenizer_file=f"{model_path}\\vocab.json",
    gpt_num_audio_tokens=1026,
    gpt_start_audio_token=1024,
    gpt_stop_audio_token=1025,
    gpt_use_masking_gt_prompt_approach=True,
    gpt_use_perceiver_resampler=True,
)

config = GPTTrainerConfig(
    epochs=NUM_EPOCHS,
    output_path=OUTPUT_PATH,
    model_args=model_args,
    run_name=RUN_NAME,
    project_name="XTTS_trainer",
    run_description="Phase 2 - Fine-tuning for ultra-smooth audio",
    dashboard_logger="tensorboard",
    logger_uri=None,
    audio=audio_config,
    batch_size=BATCH_SIZE,
    batch_group_size=0,
    eval_batch_size=BATCH_SIZE,
    num_loader_workers=0,
    eval_split_max_size=256,
    eval_split_size=EVAL_SPLIT_SIZE,
    print_step=50,
    plot_step=100,
    log_model_step=100,
    save_step=100,
    save_n_checkpoints=5,
    save_checkpoints=True,
    save_all_best=True,
    save_best_after=100,
    target_loss="loss",
    print_eval=True,
    run_eval=True,
    run_eval_steps=100,
    test_sentences=[],
    
    # Phase 2: Ultra-low learning rate for fine refinement
    lr=LEARNING_RATE,
    optimizer="AdamW",
    optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
    lr_scheduler="MultiStepLR",
    lr_scheduler_params={"milestones": [50000 * 18, 150000 * 18, 300000 * 18], "gamma": 0.5},
)

# Load samples
print("📊 Loading samples...")
train_samples, eval_samples = load_tts_samples(
    config_dataset,
    eval_split=True,
    eval_split_max_size=config.eval_split_max_size,
    eval_split_size=config.eval_split_size,
)

print(f"   Training samples: {len(train_samples)}")
print(f"   Evaluation samples: {len(eval_samples)}")
print()

# Initialize model from config
print("🤖 Initializing model...")
model = GPTTrainer.init_from_config(config)
print("   ✅ Model initialized")
print()

# Trainer - will restore from checkpoint
print("🎓 Setting up trainer (will restore from checkpoint)...")
trainer = Trainer(
    TrainerArgs(
        restore_path=RESUME_CHECKPOINT,  # Resume from Phase 1 checkpoint
        skip_train_epoch=False,
        start_with_eval=True,
        grad_accum_steps=1,
    ),
    config,
    output_path=OUTPUT_PATH,
    model=model,  # Pass initialized model
    train_samples=train_samples,
    eval_samples=eval_samples,
)

print("   ✅ Checkpoint loaded successfully")
print()

# Add automatic checkpoint cleanup to save disk space
print("🧹 Setting up automatic checkpoint cleanup...")
original_save_checkpoint = trainer.save_checkpoint

def save_checkpoint_with_cleanup():
    """Save checkpoint and immediately cleanup old ones to save disk space"""
    original_save_checkpoint()
    
    # Find and delete old checkpoints (keep only the latest)
    from pathlib import Path
    output_folder = Path(OUTPUT_PATH) / RUN_NAME
    if output_folder.exists():
        checkpoints = sorted(output_folder.glob("checkpoint_*.pth"))
        # Keep only the most recent checkpoint
        if len(checkpoints) > 1:
            for old_checkpoint in checkpoints[:-1]:
                try:
                    size_mb = old_checkpoint.stat().st_size / (1024**2)
                    old_checkpoint.unlink()
                    print(f"  🗑️  Deleted old checkpoint: {old_checkpoint.name} ({size_mb:.0f} MB freed)")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {old_checkpoint.name}: {e}")
        
        # Keep only the latest best_model (delete older best_model_*.pth files)
        best_models = sorted(output_folder.glob("best_model_*.pth"))
        if len(best_models) > 1:
            for old_best in best_models[:-1]:
                try:
                    size_mb = old_best.stat().st_size / (1024**2)
                    old_best.unlink()
                    print(f"  🗑️  Deleted old best model: {old_best.name} ({size_mb:.0f} MB freed)")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {old_best.name}: {e}")

trainer.save_checkpoint = save_checkpoint_with_cleanup
print("   ✅ Automatic cleanup enabled (keeps only latest checkpoint + best model)")
print()

print()
print("=" * 70)
print("🚀 STARTING PHASE 2 TRAINING")
print("=" * 70)
print()
print("📈 Progress Goals:")
print("   • Current: Mel CE 3.507 (high quality)")
print("   • Target: Mel CE < 2.5 (excellent quality)")
print("   • Strategy: Ultra-low LR (1e-6) for gentle refinement")
print()
print("⏱️  This will take several hours...")
print("💾 Best checkpoints saved automatically, old ones deleted")
print("🧹 Automatic cleanup saves ~5 GB per checkpoint")
print()
print("🔍 Monitor metrics:")
print("   • Mel CE should gradually decrease")
print("   • Text CE should remain < 0.03")
print("   • Training loss should decrease steadily")
print()
print("=" * 70)
print()

# Train!
trainer.fit()

print()
print("=" * 70)
print("✅ PHASE 2 TRAINING COMPLETE!")
print("=" * 70)
print()
print("📊 Check the results:")
print(f"   Training logs: {OUTPUT_PATH}")
print(f"   Best model: {OUTPUT_PATH}/best_model.pth")
print()
print("🎯 Next Steps:")
print("   1. Check training logs for final Mel CE")
print("   2. Generate test samples with new model")
print("   3. Compare quality with Phase 1 model")
print()
