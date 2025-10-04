# István Vágó Voice Cloning - Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Environment Setup (5-10 minutes)

Open PowerShell in the project directory and run:

```powershell
# Run the setup script
.\scripts\setup_environment.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
.\scripts\setup_environment.ps1
```

This will:

- Create a Python virtual environment
- Install PyTorch with CUDA support
- Install all dependencies
- Verify your GPU

### Step 2: Prepare Dataset (2-3 minutes)

```powershell
# Activate environment
.\xtts_env\Scripts\Activate.ps1

# Run dataset preparation
python scripts\prepare_dataset.py
```

**⚠️ IMPORTANT BEFORE TRAINING:**

1. Open `dataset\metadata.csv`
2. Replace placeholder Hungarian text with ACCURATE transcriptions
3. Ensure proper Hungarian diacritics (á, é, í, ó, ö, ő, ú, ü, ű)

### Step 3: Train Model (4-8 hours)

```powershell
# Start training
python scripts\train_xtts.py

# Monitor with TensorBoard (in another terminal):
tensorboard --logdir run\training
# Open browser to: http://localhost:6006
```

### Step 4: Generate Speech

After training completes:

```powershell
# Run inference
python scripts\inference.py

# Follow the prompts to:
# 1. Generate sample quiz phrases
# 2. Enter custom Hungarian text
```

## 🔍 Pre-Flight Check

Before starting, run the system check:

```powershell
python scripts\check_system.py
```

This verifies:

- ✅ Python version (3.9-3.11)
- ✅ Required packages installed
- ✅ GPU/CUDA working
- ✅ Directory structure

## 📁 Project Structure

```
tts-2/
├── source_clips/          # Your original Vágó audio (13 files)
├── processed_clips/       # Preprocessed audio (auto-generated)
├── dataset/              # Training dataset
│   ├── wavs/            # Processed audio files
│   └── metadata.csv     # ⚠️ EDIT THIS with accurate Hungarian text
├── scripts/              # All Python scripts
│   ├── setup_environment.ps1  # Run first
│   ├── prepare_dataset.py     # Run second
│   ├── train_xtts.py          # Run third
│   ├── inference.py           # Run after training
│   └── check_system.py        # Diagnostic tool
├── run/                  # Training outputs
│   └── training/        # Checkpoints, logs, TensorBoard
└── output/               # Generated audio files
```

## ⚙️ Configuration

### Key Files to Review

1. **`scripts/prepare_dataset.py`** (Lines 25-39)

   - Edit TRANSCRIPTIONS dictionary with accurate Hungarian text

2. **`scripts/train_xtts.py`** (Lines 30-50)

   - Adjust BATCH_SIZE if you get GPU memory errors
   - Modify NUM_EPOCHS for longer/shorter training

3. **`scripts/inference.py`** (Lines 30-40)
   - Tune TEMPERATURE for voice consistency vs expressiveness

## 🎯 Expected Training Timeline

| GPU      | Batch Size | Hours/Epoch | Total (25 epochs) |
| -------- | ---------- | ----------- | ----------------- |
| RTX 4070 | 2          | 15-20 min   | 6-8 hours         |
| RTX 3080 | 2          | 20-25 min   | 8-10 hours        |
| CPU Only | 1          | 4-6 hours   | 100+ hours ⚠️     |

## 📊 Monitoring Training

### TensorBoard Metrics to Watch

1. **`train/total_loss`** - Should decrease over time
2. **`eval/total_loss`** - Should decrease and stabilize
3. **Gap between train and eval** - If too large = overfitting

### Listen to Generated Samples

During training, audio samples are generated every few epochs:

- Check `run/training/[run_name]/test_audios/`
- Listen to progression over epochs
- Stop training if quality starts degrading (overfitting)

## 🐛 Troubleshooting

### Issue: "Import TTS could not be resolved"

```powershell
# Make sure virtual environment is activated
.\xtts_env\Scripts\Activate.ps1

# Reinstall TTS
pip install --force-reinstall TTS==0.22.0
```

### Issue: CUDA out of memory

Edit `scripts/train_xtts.py`:

```python
BATCH_SIZE = 1  # Reduce from 2 to 1
```

### Issue: Training is very slow

1. Verify GPU is being used:

```powershell
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

2. Check GPU utilization:

```powershell
nvidia-smi
# Should show python.exe using GPU memory
```

### Issue: Poor quality output

1. **Not enough data**: Collect more Vágó clips (target: 15-30 min)
2. **Bad transcriptions**: Verify accuracy in metadata.csv
3. **Overfitting**: Reduce epochs or use early stopping
4. **Wrong inference parameters**: Adjust TEMPERATURE (try 0.65-0.85)

## 🎓 Next Steps After First Training

1. **Evaluate quality**: Listen to generated samples critically
2. **A/B test**: Compare with original Vágó audio
3. **Iterate**: Adjust hyperparameters based on results
4. **Collect more data**: If quality insufficient, get more audio
5. **Fine-tune**: Resume training from best checkpoint

## 📝 Important Notes

### About the Source Data

Your current dataset (~13 clips) is **minimal**. For production quality:

- **Good**: 15-20 minutes of clean audio
- **Better**: 30 minutes
- **Best**: 45+ minutes with diverse content

### About Hungarian Language

XTTS-v2 supports Hungarian, but quality depends on:

- Accurate transcriptions with proper diacritics
- Natural speaking patterns in training data
- Sufficient phonetic diversity

### About Training Time

- First training: ~6-8 hours (RTX 4070)
- Expect to iterate 2-4 times for optimal quality
- Total time investment: 2-3 days including data prep

## 🔗 Useful Links

- [README.md](README.md) - Detailed project information
- [QUALITY_GUIDE.md](QUALITY_GUIDE.md) - How to achieve ElevenLabs-level quality
- [Coqui TTS Docs](https://docs.coqui.ai/) - Official documentation
- [XTTS Paper](https://arxiv.org/abs/2309.08519) - Technical details

## ❓ Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Run `python scripts\check_system.py` for diagnostics
3. Review error messages carefully
4. Check GPU memory usage with `nvidia-smi`

## 🎯 Success Criteria

Your model is ready when:

- ✅ Generated speech sounds like István Vágó
- ✅ Hungarian pronunciation is accurate
- ✅ Natural prosody and intonation
- ✅ No artifacts (clicks, glitches, robotic sound)
- ✅ Consistent quality across different texts
- ✅ Native Hungarian speakers approve

Good luck! 🍀
