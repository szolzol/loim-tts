"""
Phase 4 Training - Continue from Checkpoint 1901
================================================
Continue fine-tuning with new 40 selected Vágó samples
Starting point: best_model_1901.pth (Mel CE: 2.971)
Target: Mel CE < 2.5 (excellent quality)

New dataset: 40 high-quality samples with distinct characteristics
- 10 excitement samples
- 14 neutral samples
- 16 question samples
"""

import os
from pathlib import Path

# ⚠️ CRITICAL FIX: Monkey-patch TTS load_audio to use soundfile instead of torchcodec
# PyTorch nightly + torchcodec is broken on Windows, use soundfile directly
import soundfile as sf
import torch
import numpy as np

def load_audio_soundfile(audiopath, sample_rate=22050):
    """Load audio using soundfile instead of torchaudio/torchcodec"""
    audio, sr = sf.read(audiopath)
    # Convert to torch tensor
    audio = torch.FloatTensor(audio)
    # Soundfile returns shape: (samples,) for mono or (samples, channels) for stereo
    # We need shape: (channels, samples) for TTS compatibility
    if audio.dim() == 1:
        # Mono audio - add channel dimension: (samples,) -> (1, samples)
        audio = audio.unsqueeze(0)
    else:
        # Stereo - transpose: (samples, channels) -> (channels, samples)
        audio = audio.transpose(0, 1)
        # Convert to mono by averaging channels
        if audio.shape[0] > 1:
            audio = audio.mean(dim=0, keepdim=True)
    
    # Resample if needed
    if sr != sample_rate:
        import torchaudio.transforms as T
        resampler = T.Resample(sr, sample_rate)
        audio = resampler(audio)
    
    return audio  # Shape: (1, samples) for mono audio

# Monkey-patch the load_audio function in TTS
import TTS.tts.models.xtts
TTS.tts.models.xtts.load_audio = load_audio_soundfile
print("✅ Audio loading patched to use soundfile (avoiding torchcodec issues)")

from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig

# Configuration
OUTPUT_PATH = "run/training_phase4_continuation"
DATASET_PATH = "dataset_phase4"  # New 40 selected samples
RESUME_CHECKPOINT = "run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd/best_model_1901.pth"

# Training parameters - PHASE 4 (focused fine-tuning)
BATCH_SIZE = 2  # Smaller batch for focused learning
NUM_EPOCHS = 50  # Extended training for deeper learning
LEARNING_RATE = 5e-7  # Very low for fine refinement from 2.971
EVAL_SPLIT_SIZE = 0.15  # 15% for evaluation (~6 samples, ensures valid eval set)

print("=" * 80)
print("🎯 PHASE 4 TRAINING - CONTINUATION FROM CHECKPOINT 1901")
print("=" * 80)
print()
print("📊 Current Status:")
print("   • Starting Mel CE: 2.971 (checkpoint 1901)")
print("   • Target Mel CE: < 2.5 (excellent quality)")
print("   • Improvement needed: -15.8%")
print()
print("📦 New Dataset:")
print("   • 40 high-quality selected samples")
print("   • 10 excitement + 14 neutral + 16 question")
print("   • Distinct characteristics for better prosody")
print()
print("🔧 Phase 4 Configuration:")
print(f"   • Resuming from: best_model_1901.pth")
print(f"   • Learning Rate: {LEARNING_RATE} (ultra-low)")
print(f"   • Batch Size: {BATCH_SIZE} (focused learning)")
print(f"   • Epochs: {NUM_EPOCHS}")
print(f"   • Focus: Mel CE improvement + prosody diversity")
print()
print("=" * 80)
print()

# Verify checkpoint exists
if not Path(RESUME_CHECKPOINT).exists():
    print(f"❌ ERROR: Checkpoint not found!")
    print(f"   Looking for: {RESUME_CHECKPOINT}")
    exit(1)

print(f"✅ Found checkpoint: {Path(RESUME_CHECKPOINT).name}")
print()

# Verify dataset exists
if not Path(DATASET_PATH).exists():
    print(f"❌ ERROR: Dataset not found!")
    print(f"   Looking for: {DATASET_PATH}")
    print()
    print("💡 Run this first:")
    print("   python scripts/prepare_phase4_dataset.py")
    exit(1)

print(f"✅ Found dataset: {DATASET_PATH}")
print()

# RUN_NAME for this session
RUN_NAME = "XTTS_Phase4_Continuation"

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
    dataset_name="phase4_selected_vago",
    path=DATASET_PATH,
    meta_file_train="metadata.csv",
    language="hu",
)

# Model paths from original training
model_path = "C:\\Users\\szolzol\\AppData\\Local\\tts\\tts_models--multilingual--multi-dataset--xtts_v2"

# Audio config
audio_config = XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000)

# XTTS GPT configuration - Phase 4 ultra-low LR
print("🔧 Configuring XTTS GPT Trainer...")
model_args = GPTArgs(
    max_conditioning_length=143677,  # 6 secs
    min_conditioning_length=66150,   # 3 secs
    debug_loading_failures=False,
    max_wav_length=530000,  # ~24 seconds (increased for longer samples)
    max_text_length=400,  # Increased for longer transcriptions
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
    run_description="Phase 4 - Continue from 1901 with selected samples for Mel CE < 2.5",
    dashboard_logger="tensorboard",
    logger_uri=None,
    audio=audio_config,
    batch_size=BATCH_SIZE,
    batch_group_size=0,
    eval_batch_size=BATCH_SIZE,
    num_loader_workers=0,
    eval_split_max_size=256,
    eval_split_size=EVAL_SPLIT_SIZE,
    print_step=25,  # More frequent prints for small dataset
    plot_step=50,
    log_model_step=50,
    save_step=50,  # Save more frequently
    save_n_checkpoints=3,  # Keep last 3 checkpoints
    save_checkpoints=True,
    save_all_best=True,
    save_best_after=50,
    target_loss="loss",
    print_eval=False,  # Disable eval printing
    run_eval=False,  # Disable evaluation (samples being filtered out)
    run_eval_steps=None,  # No eval steps
    test_sentences=[],
    
    # Phase 4: Ultra-low learning rate for gentle refinement
    lr=LEARNING_RATE,
    optimizer="AdamW",
    optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
    lr_scheduler="MultiStepLR",
    lr_scheduler_params={"milestones": [50000 * 18, 150000 * 18], "gamma": 0.5},
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

# Validate dataset size
if len(train_samples) < 20:
    print("⚠️  WARNING: Very small training set!")
    print("   Consider adding more samples for better results")
    print()

# Initialize model from config
print("🤖 Initializing model...")
model = GPTTrainer.init_from_config(config)
print("   ✅ Model initialized")
print()

# Trainer - will restore from checkpoint
print("🎓 Setting up trainer (will restore from checkpoint 1901)...")
trainer = Trainer(
    TrainerArgs(
        restore_path=RESUME_CHECKPOINT,  # Resume from best_model_1901
        skip_train_epoch=False,
        start_with_eval=False,  # Skip initial eval to avoid filtering issues
        grad_accum_steps=1,
    ),
    config,
    output_path=OUTPUT_PATH,
    model=model,
    train_samples=train_samples,
    eval_samples=eval_samples,
)

print("   ✅ Checkpoint 1901 loaded successfully")
print()

# Add automatic checkpoint cleanup
print("🧹 Setting up automatic checkpoint cleanup...")
original_save_checkpoint = trainer.save_checkpoint

def save_checkpoint_with_cleanup():
    """Save checkpoint and cleanup old ones"""
    original_save_checkpoint()
    
    from pathlib import Path
    output_folder = Path(OUTPUT_PATH) / RUN_NAME
    if output_folder.exists():
        # Keep only last 3 checkpoints
        checkpoints = sorted(output_folder.glob("checkpoint_*.pth"))
        if len(checkpoints) > 3:
            for old_checkpoint in checkpoints[:-3]:
                try:
                    size_mb = old_checkpoint.stat().st_size / (1024**2)
                    old_checkpoint.unlink()
                    print(f"  🗑️  Deleted: {old_checkpoint.name} ({size_mb:.0f} MB freed)")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {old_checkpoint.name}: {e}")

trainer.save_checkpoint = save_checkpoint_with_cleanup
print("   ✅ Auto-cleanup enabled (keeps last 3 checkpoints)")
print()

print()
print("=" * 80)
print("🚀 STARTING PHASE 4 TRAINING")
print("=" * 80)
print()
print("📈 Training Strategy:")
print("   • Small dataset (40 samples) = focused learning")
print("   • Ultra-low LR (5e-7) = gentle refinement")
print("   • Extended epochs (50) = deep optimization")
print("   • Starting from best_model_1901 (Mel CE: 2.971)")
print()
print("🎯 Goals:")
print("   1. Mel CE < 2.5 (excellent quality)")
print("   2. Maintain Text CE < 0.03")
print("   3. Improve prosody diversity (3 distinct categories)")
print("   4. Preserve Vágó voice characteristics")
print()
print("⏱️  Estimated time: 2-4 hours")
print("💾 Best models saved automatically")
print("📊 Check TensorBoard for real-time metrics")
print()
print("🔍 Key Metrics to Watch:")
print("   • Mel CE (target < 2.5)")
print("   • Text CE (should stay < 0.03)")
print("   • Training Loss (should decrease steadily)")
print("   • Eval Loss (should follow training loss)")
print()
print("=" * 80)
print()

# Train!
trainer.fit()

print()
print("=" * 80)
print("✅ PHASE 4 TRAINING COMPLETE!")
print("=" * 80)
print()
print("📊 Results Location:")
print(f"   Output folder: {OUTPUT_PATH}/{RUN_NAME}")
print(f"   Best model: {OUTPUT_PATH}/{RUN_NAME}/best_model_*.pth")
print(f"   Checkpoints: {OUTPUT_PATH}/{RUN_NAME}/checkpoint_*.pth")
print()
print("🎯 Next Steps:")
print("   1. Check final Mel CE score in logs")
print("   2. Update generate_questions_and_answers.py with new model path")
print("   3. Generate test samples to verify quality")
print("   4. Compare with checkpoint 1901 samples")
print()
print("💡 If Mel CE < 2.5:")
print("   ✅ Mission accomplished! Use this model for production")
print()
print("💡 If Mel CE still > 2.5:")
print("   • Continue training for more epochs")
print("   • Add more diverse samples to dataset")
print("   • Consider adjusting learning rate")
print()
