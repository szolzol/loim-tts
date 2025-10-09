# Phase 4 Training Plan - Checkpoint 1901 Continuation

## 📊 Current Status

**Starting Point:**

- Model: `best_model_1901.pth`
- Mel CE: **2.971** (very good quality)
- Text CE: < 0.03 (excellent)
- Training epochs: 1901

**Target:**

- Mel CE: **< 2.5** (excellent quality)
- Improvement needed: **-15.8%**
- Expected: More natural prosody, better voice consistency

---

## 📦 New Dataset - Phase 4

**Location:** `prepared_sources/vago_samples_selected/`

**Contents:**

- **10 excitement samples** - High energy, enthusiastic tone
- **14 neutral samples** - Calm, professional quiz presenter tone
- **16 question samples** - Clear question intonation

**Total:** 40 high-quality samples with distinct prosody characteristics

**Quality criteria:**

- Clear audio, no background noise
- Authentic Vágó István voice
- Distinct emotional characteristics
- Well-separated categories for targeted learning

---

## 🎯 Training Strategy

### Phase 4 Configuration

```python
LEARNING_RATE = 5e-7      # Ultra-low for gentle refinement
BATCH_SIZE = 2            # Focused learning on small dataset
NUM_EPOCHS = 50           # Extended for deep optimization
EVAL_SPLIT = 0.20         # 8 samples for evaluation
```

### Why These Parameters?

1. **Ultra-low LR (5e-7)**

   - Starting from Mel CE 2.971 (already very good)
   - Need gentle refinement, not aggressive changes
   - Prevents overfitting on small dataset

2. **Small Batch Size (2)**

   - 40 samples total = small dataset
   - Batch size 2 = 20 steps per epoch
   - More frequent updates = faster convergence

3. **Extended Epochs (50)**

   - Small dataset needs more passes
   - 50 epochs × 20 steps = 1000 total steps
   - Enough for Mel CE convergence

4. **20% Eval Split**
   - 32 training samples
   - 8 evaluation samples
   - Good balance for monitoring overfitting

### Expected Timeline

- **Dataset Preparation:** 5 minutes (manual transcription verification)
- **Training Duration:** 2-4 hours on RTX 5070 Ti
- **Checkpoints:** Every 50 steps (saves ~3 GB each)
- **Total Storage:** ~10-15 GB for all checkpoints

---

## 📝 Step-by-Step Instructions

### Step 1: Verify Transcriptions

**CRITICAL:** You must update transcriptions before training!

1. Open `scripts/prepare_phase4_dataset.py`
2. Listen to each audio file in `prepared_sources/vago_samples_selected/`
3. Update the `TRANSCRIPTIONS` dictionary with exact text
4. Current transcriptions are **PLACEHOLDERS**

Example:

```python
TRANSCRIPTIONS = {
    "excitement/excitement1.wav": "Fantasztikus! Gratulálok!",  # UPDATE THIS
    "neutral/neutral1.wav": "Üdvözlöm önöket.",                 # UPDATE THIS
    # ... etc
}
```

### Step 2: Run Dataset Preparation

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/prepare_phase4_dataset.py
```

This will:

- ✅ Resample all audio to 22050 Hz
- ✅ Create `dataset_phase4/` directory
- ✅ Generate `metadata.csv` with transcriptions
- ✅ Validate all files exist

### Step 3: Start Training

**Option A: PowerShell Script (Recommended)**

```powershell
.\START_PHASE4_TRAINING.ps1
```

**Option B: Direct Python**

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/train_phase4_continuation.py
```

### Step 4: Monitor Training

**Watch these metrics:**

- ✅ **Mel CE** - Should decrease from 2.971 → < 2.5
- ✅ **Text CE** - Should stay < 0.03
- ✅ **Training Loss** - Should decrease steadily
- ✅ **Eval Loss** - Should follow training loss (no overfitting)

**Check logs:**

```powershell
# Real-time monitoring
Get-Content run/training_phase4_continuation/XTTS_Phase4_Continuation/train.log -Wait

# TensorBoard (optional)
tensorboard --logdir run/training_phase4_continuation
```

### Step 5: Test New Model

After training completes:

1. Find best model:

```powershell
Get-ChildItem run/training_phase4_continuation/XTTS_Phase4_Continuation/best_model_*.pth
```

2. Update `generate_questions_and_answers.py`:

```python
MODEL_PATH = MODEL_DIR / "best_model_XXXX.pth"  # Update XXXX with new checkpoint number
```

3. Generate test samples:

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/generate_questions_and_answers.py 2 2
```

4. Compare quality:
   - Listen to new samples
   - Compare with checkpoint 1901 samples
   - Check for improved prosody and reduced roboticness

---

## 🎯 Success Criteria

### Primary Goal: Mel CE < 2.5

- **Current:** 2.971
- **Target:** < 2.5
- **Improvement:** -15.8%

### Secondary Goals:

- ✅ Text CE remains < 0.03
- ✅ No overfitting (eval loss follows training loss)
- ✅ Improved prosody diversity (3 distinct categories)
- ✅ Maintained Vágó voice characteristics

### Quality Indicators:

- More natural question intonation
- Better excitement energy without overemphasis
- Smoother neutral tone transitions
- Reduced first-syllable overemphasis (`KÉ!rdezzük` → `Kérdezzük`)
- Less robotic overall feel

---

## 🔧 Troubleshooting

### If Mel CE doesn't improve:

1. **Check transcriptions accuracy** - Wrong text = poor learning
2. **Extend training** - Try 100 epochs instead of 50
3. **Adjust learning rate** - Try 8e-7 or 3e-7
4. **Add more samples** - 40 may not be enough diversity

### If Text CE increases:

1. **Stop training** - Model is degrading
2. **Lower learning rate** - Try 3e-7 or 2e-7
3. **Check transcriptions** - Must be 100% accurate

### If overfitting occurs:

1. **Stop early** - Use earlier checkpoint
2. **Add more samples** - Need more diversity
3. **Increase eval split** - Try 30% instead of 20%

### If training is too slow:

1. **Check GPU usage** - Should be 95-100%
2. **Increase batch size** - Try 3 or 4 (if memory allows)
3. **Reduce epochs** - Start with 25 to test

---

## 📊 Expected Results

### Best Case Scenario:

- Mel CE: 2.3 - 2.4 (excellent quality)
- Training time: 2-3 hours
- Voice quality: Noticeably better than 1901
- Prosody: More natural, less robotic

### Realistic Scenario:

- Mel CE: 2.5 - 2.7 (very good quality)
- Training time: 3-4 hours
- Voice quality: Slight improvement over 1901
- Prosody: Improved diversity in categories

### If No Improvement:

- Mel CE stays > 2.9
- Possible causes:
  - Transcriptions incorrect
  - Dataset too small
  - Learning rate too low
  - Need different samples

---

## 🚀 After Training

### If Successful (Mel CE < 2.5):

1. ✅ Use new model for production
2. ✅ Update all inference scripts
3. ✅ Generate full quiz question set
4. ✅ Document new parameters
5. ✅ Archive checkpoint 1901 as backup

### If Needs More Work:

1. ⏭️ Continue training (Phase 5)
2. 📦 Add 20-30 more diverse samples
3. 🔧 Adjust hyperparameters
4. 🎯 Try alternative architectures (YourTTS, Tortoise)

---

## 📁 File Structure

```
i:/CODE/tts-2/
├── prepared_sources/
│   └── vago_samples_selected/          # NEW: 40 selected samples
│       ├── excitement/ (10 files)
│       ├── neutral/ (14 files)
│       └── question/ (16 files)
├── dataset_phase4/                     # Created by prepare script
│   ├── excitement/
│   ├── neutral/
│   ├── question/
│   └── metadata.csv
├── scripts/
│   ├── prepare_phase4_dataset.py       # NEW: Dataset preparation
│   └── train_phase4_continuation.py    # NEW: Training script
├── run/
│   ├── training_combined_phase2/       # Existing: checkpoint 1901
│   └── training_phase4_continuation/   # NEW: Phase 4 output
└── START_PHASE4_TRAINING.ps1           # NEW: Convenience script
```

---

## 💡 Tips & Best Practices

1. **Before Training:**

   - ✅ Verify all transcriptions are accurate
   - ✅ Check audio quality (no clipping, noise)
   - ✅ Ensure GPU drivers updated
   - ✅ Close other GPU applications

2. **During Training:**

   - 📊 Monitor Mel CE every 100 steps
   - 🔍 Watch for overfitting signs
   - 💾 Don't interrupt mid-training
   - 🔌 Ensure stable power supply

3. **After Training:**
   - 🎧 Listen to test samples immediately
   - 📈 Compare metrics with checkpoint 1901
   - 💾 Backup best model
   - 📝 Document results

---

## 📞 Support

If you encounter issues:

1. Check training logs in `run/training_phase4_continuation/`
2. Review this document's troubleshooting section
3. Compare with Phase 2 training parameters
4. Consider adjusting learning rate or epochs

---

**Created:** October 9, 2025  
**Starting Checkpoint:** best_model_1901.pth (Mel CE: 2.971)  
**Target:** Mel CE < 2.5  
**Dataset:** 40 selected Vágó samples (excitement, neutral, question)
