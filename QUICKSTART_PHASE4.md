# Phase 4 Training - Quick Start Guide

## ⚡ Quick Start (TL;DR)

```powershell
# 1. Update transcriptions in scripts/prepare_phase4_dataset.py
# 2. Run this:
.\START_PHASE4_TRAINING.ps1
```

That's it! The script handles everything else.

---

## 📋 Prerequisites Checklist

- [x] 40 audio samples in `prepared_sources/vago_samples_selected/`
- [ ] **Transcriptions updated** in `scripts/prepare_phase4_dataset.py` (CRITICAL!)
- [x] Checkpoint 1901 exists (`best_model_1901.pth`)
- [x] Conda environment ready (`I:/CODE/tts-2/.conda/`)
- [x] GPU available (RTX 5070 Ti)
- [ ] ~20 GB free disk space

---

## 🎯 What You Need To Do NOW

### 1. Update Transcriptions (MANDATORY!)

Open `scripts/prepare_phase4_dataset.py` and update the `TRANSCRIPTIONS` dictionary:

```python
TRANSCRIPTIONS = {
    # EXCITEMENT - Listen and update!
    "excitement/excitement1.wav": "YOUR EXACT TRANSCRIPTION HERE",
    "excitement/excitement2.wav": "YOUR EXACT TRANSCRIPTION HERE",
    # ... (all 10)
    
    # NEUTRAL - Listen and update!
    "neutral/neutral1.wav": "YOUR EXACT TRANSCRIPTION HERE",
    # ... (all 14)
    
    # QUESTION - Listen and update!
    "question/question1.wav": "YOUR EXACT TRANSCRIPTION HERE",
    # ... (all 16)
}
```

**How to do it:**
1. Play each audio file
2. Write down EXACTLY what is said
3. Include punctuation (. ? !)
4. Use correct Hungarian orthography

---

## 🚀 Training Process

### Automatic (Recommended)

```powershell
.\START_PHASE4_TRAINING.ps1
```

This will:
1. ✅ Prepare dataset (resample, create metadata)
2. ✅ Load checkpoint 1901
3. ✅ Train for 50 epochs (~2-4 hours)
4. ✅ Save best model automatically

### Manual (If you want control)

```powershell
# Step 1: Prepare dataset
I:/CODE/tts-2/.conda/python.exe scripts/prepare_phase4_dataset.py

# Step 2: Start training
I:/CODE/tts-2/.conda/python.exe scripts/train_phase4_continuation.py
```

---

## 📊 Monitor Progress

### Watch Training in Real-Time

```powershell
# Terminal output
Get-Content run/training_phase4_continuation/XTTS_Phase4_Continuation/train.log -Wait

# Key metrics to watch:
# - Mel CE: Should go from 2.971 → <2.5
# - Text CE: Should stay <0.03
# - Training Loss: Should decrease steadily
```

### Check Current Status

```powershell
# Find latest checkpoint
Get-ChildItem run/training_phase4_continuation/XTTS_Phase4_Continuation/ -Filter "*.pth" | Sort-Object LastWriteTime -Descending | Select-Object -First 3

# Check best model so far
Get-ChildItem run/training_phase4_continuation/XTTS_Phase4_Continuation/best_model_*.pth
```

---

## ⏱️ What To Expect

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| Dataset Prep | 5 min | Resampling audio, creating metadata |
| Model Loading | 2 min | Loading checkpoint 1901 |
| Epoch 1-10 | 30 min | Initial convergence |
| Epoch 11-30 | 1 hour | Main optimization |
| Epoch 31-50 | 1 hour | Fine refinement |
| **Total** | **2-4 hours** | Full training run |

**Progress Indicators:**
- ✅ Mel CE decreasing → Good!
- ✅ Text CE stable → Good!
- ❌ Mel CE increasing → Stop and check
- ❌ Text CE increasing → Stop immediately

---

## ✅ When It's Done

### Step 1: Find Best Model

```powershell
Get-ChildItem run/training_phase4_continuation/XTTS_Phase4_Continuation/best_model_*.pth
```

Look for the file with the **lowest Mel CE** in the filename.

### Step 2: Update Inference Script

Edit `scripts/generate_questions_and_answers.py`:

```python
# OLD:
MODEL_PATH = MODEL_DIR / "best_model_1901.pth"

# NEW:
MODEL_PATH = Path("run/training_phase4_continuation/XTTS_Phase4_Continuation/best_model_XXXX.pth")
```

### Step 3: Test It!

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/generate_questions_and_answers.py 2 2
```

Listen to the generated samples and compare with checkpoint 1901 samples.

---

## 🎯 Success = Mel CE < 2.5

### If Mel CE < 2.5:
🎉 **SUCCESS!** Your model is now excellent quality!
- Use it for production
- Generate full quiz question set
- Archive checkpoint 1901 as backup

### If Mel CE 2.5 - 2.9:
✅ **GOOD!** Improvement achieved, but can be better.
- Try continuing for 25 more epochs
- Or add 10-20 more diverse samples

### If Mel CE > 2.9:
⚠️ **NO IMPROVEMENT** - Need different approach:
1. Check transcriptions accuracy (most common issue)
2. Try lower learning rate (3e-7)
3. Add more diverse samples (60-80 total)
4. Consider different training strategy

---

## 🔥 Common Issues & Fixes

### "Checkpoint not found"
**Fix:** Update `RESUME_CHECKPOINT` path in `train_phase4_continuation.py`

### "Dataset not found"
**Fix:** Run `prepare_phase4_dataset.py` first

### Training stops immediately
**Fix:** Check GPU memory, close other applications

### Mel CE not improving
**Fix:** Verify transcriptions are 100% accurate

### Out of memory
**Fix:** Reduce `BATCH_SIZE` from 2 to 1 in training script

---

## 📞 Need Help?

1. Check `PHASE4_TRAINING_PLAN.md` for detailed info
2. Review training logs in `run/training_phase4_continuation/`
3. Compare with Phase 2 parameters in `scripts/train_combined_phase2.py`

---

**Quick Reference:**
- Starting checkpoint: `best_model_1901.pth` (Mel CE: 2.971)
- Target: Mel CE < 2.5
- Dataset: 40 samples (10 excitement, 14 neutral, 16 question)
- Duration: 2-4 hours
- Output: `run/training_phase4_continuation/`
