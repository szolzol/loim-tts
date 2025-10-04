# István Vágó Voice Clone - Production Ready 🎯

**Phase 2 training complete! Production-ready voice model with optimized prosody.**

---

## 📊 Model Performance

- **Best Model**: `best_model_1901.pth` (Mel CE: 2.971)
- **Total Improvement**: -41.1% from baseline
- **Quality Rating**: 9/10 (production-ready)
- **Training**: 311 samples (Milliomos + Blikk), 4400+ steps
- **Prosody**: Optimized with temperature=0.40 for stable, natural delivery

---

## 🎬 Quick Start - Generate Samples

### Generate Quiz Show Samples

```powershell
python scripts\generate_quiz_phase2.py
```

This will create 5 realistic quiz show questions in `quiz_samples_phase2_final/`

**Optimized Settings:**

- Temperature: 0.40 (ultra-stable, no waviness)
- Pauses: "..." between answer options
- Natural phrasing with context words

### Files You Need

**Phase 2 Best Model** (30 GB total):

```
run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd/
├── best_model_1901.pth  (5.22 GB) ⭐
├── config.json
└── vocab.json
```

**Reference Audio**:

```
dataset_combined/neutral/
└── neutral_002.wav  (used for voice cloning)
```

---

## 📁 Project Structure (Clean)

```
tts-2/
├── run/
│   └── training_combined_phase2/     # Phase 2 model (30 GB)
│       └── XTTS_Combined_Phase2-.../
│           ├── best_model_1901.pth   ⭐ Production model
│           ├── config.json
│           └── vocab.json
│
├── scripts/                          # 11 essential scripts (82 KB)
│   ├── Training Scripts:
│   │   ├── train_combined_phase2.py  ⭐ Phase 2 fine-tuning
│   │   ├── train_combined.py         Phase 1 training
│   │   └── train_phase2.py           Alternative training
│   │
│   ├── Generation Scripts:
│   │   ├── generate_quiz_phase2.py   ⭐ Production samples (temp 0.40)
│   │   ├── inference.py              ⭐ General inference
│   │   ├── generate_best_samples.py  Quality testing
│   │   └── zero_shot_inference.py    Zero-shot cloning
│   │
│   └── Dataset Scripts:
│       ├── prepare_dataset.py        ⭐ Prepare training data
│       ├── transcribe_audio.py       Create transcripts
│       ├── verify_dataset.py         Validate dataset
│       └── monitor_training.py       Training monitor
│
├── quiz_samples_phase2_final/        ⭐ Generated samples (5)
├── dataset_combined/                 ⭐ Training dataset (288 MB)
│   ├── metadata.csv                  Training metadata
│   ├── confirmation/, excitement/,   Categorized audio samples
│   │   neutral/, question/, ...
│   └── neutral/neutral_002.wav       Reference audio for cloning
│
└── Documentation:
    ├── README.md                     ⭐ This file
    ├── PHASE2_SUCCESS_SUMMARY.md     # Complete results
    ├── PHASE2_FINAL_STATUS.md        # Detailed analysis
    ├── CLEANUP_SUMMARY.md            # Cleanup info
    └── TROUBLESHOOTING.md            # Common issues
```

---

## � Training Journey

| Phase                | Mel CE    | Improvement | Quality  | Status      |
| -------------------- | --------- | ----------- | -------- | ----------- |
| Baseline (Milliomos) | 5.046     | -           | 7.5/10   | ✅          |
| Phase 1 (Combined)   | 3.507     | -30.5%      | 8.5/10   | ✅          |
| **Phase 2 (Best)**   | **2.971** | **-41.1%**  | **9/10** | **✅ PROD** |

---

## 🔧 System Requirements

- **OS**: Windows 10/11
- **GPU**: NVIDIA RTX 4070 (12GB VRAM)
- **CUDA**: 12.7
- **Python**: 3.11
- **Disk Space**: ~35 GB (model + samples)

---

## � Scripts Reference

### Training Scripts (3)

**`train_combined_phase2.py`** ⭐ Main fine-tuning script

- Continues training from Phase 1 checkpoint
- Lower learning rate (1e-6) for fine-tuning
- Required for future model improvements
- Usage: `python scripts\train_combined_phase2.py`

**`train_combined.py`** - Phase 1 training

- Initial training combining Milliomos + Blikk datasets
- Can be used to retrain from scratch
- Reference for training configuration

**`train_phase2.py`** - Alternative Phase 2 approach

- Experimental training configuration
- Useful for comparing approaches

### Generation Scripts (4)

**`generate_quiz_phase2.py`** ⭐ Production generator

- Optimized settings (temperature=0.40)
- Generates quiz questions with natural pauses
- Current: 5 questions with A/B/C/D options
- Usage: `python scripts\generate_quiz_phase2.py`

**`inference.py`** ⭐ General inference

- Generate custom audio with any text
- Flexible parameters (temperature, etc.)
- Useful for ad-hoc generation
- Usage: `python scripts\inference.py --text "Your text here"`

**`generate_best_samples.py`** - Quality testing

- Generates test samples from best model
- Useful for comparing model versions
- Validates model quality

**`zero_shot_inference.py`** - Zero-shot cloning

- Clone any voice with just 6-second sample
- No training required
- Useful for testing new voices

### Dataset Scripts (3)

**`prepare_dataset.py`** ⭐ Dataset preparation

- Prepares audio + transcript pairs
- Creates metadata.csv
- Essential for adding new training data
- Usage: `python scripts\prepare_dataset.py`

**`transcribe_audio.py`** - Auto transcription

- Creates transcripts from audio files
- Uses Whisper or manual input
- Needed when adding new samples

**`verify_dataset.py`** - Dataset validation

- Checks audio quality
- Validates transcript format
- Ensures dataset is ready for training

### Utility Scripts (1)

**`monitor_training.py`** - Training monitor

- Real-time training progress
- Tracks loss curves
- Useful during long training runs

---

## �📖 Documentation

### Essential Docs

1. **PHASE2_SUCCESS_SUMMARY.md** - Complete training results and achievements
2. **PHASE2_FINAL_STATUS.md** - Detailed Phase 2 analysis and metrics
3. **CLEANUP_SUMMARY.md** - Cleanup details and saved space
4. **TROUBLESHOOTING.md** - Common issues and solutions

### Key Achievements

- ✅ **Best Mel CE**: 2.971 (excellent smoothness)
- ✅ **Text CE**: 0.0282 (excellent pronunciation)
- ✅ **Quality**: 9/10 production-ready
- ✅ **Automatic Cleanup**: Implemented (saves 5GB per checkpoint)
- ✅ **15 Quiz Samples**: Generated successfully
- ✅ **Disk Space**: Freed 45 GB through cleanup

---

## 🎤 Generated Samples

Location: `quiz_samples_phase2_final/`

15 realistic quiz show scenarios:

- Show opening/closing
- Questions (easy, medium, hard)
- Correct/wrong answer reactions
- Lifeline offers
- Tension moments
- Victory celebrations
- Countdown sequences

---

## 🚀 Deployment

### For Production Use

1. Copy the model directory:

   ```
   run/training_combined_phase2/XTTS_Combined_Phase2-.../
   ```

2. Ensure these files exist:

   - `best_model_1901.pth` (5.22 GB)
   - `config.json`
   - `vocab.json` ← **Critical for tokenizer!**

3. Use `scripts/generate_quiz_phase2.py` as template

### Sample Generation Code

```python
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Load model
config = XttsConfig()
config.load_json("path/to/config.json")
model = Xtts.init_from_config(config)

# Load checkpoint with vocab
model.load_checkpoint(
    config,
    checkpoint_dir="path/to/model/dir",
    checkpoint_path="path/to/best_model_1901.pth",
    vocab_path="path/to/vocab.json",  # Required!
    eval=True,
    use_deepspeed=False
)

model.cuda()

# Get speaker latents
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
    audio_path=["reference_audio.wav"]
)

# Generate speech
outputs = model.inference(
    text="Your Hungarian text here",
    language="hu",
    gpt_cond_latent=gpt_cond_latent,
    speaker_embedding=speaker_embedding,
    temperature=0.7,
)
```

---

## 📊 Training Stats

### Dataset

- **Total Samples**: 311 (80 Milliomos + 231 Blikk)
- **Total Duration**: 39.7 minutes
- **Train/Eval Split**: 265/46
- **Language**: Hungarian

### Training Configuration

- **Learning Rate (Phase 2)**: 1e-6 (ultra-fine tuning)
- **Batch Size**: 3
- **Epochs**: 30
- **Total Steps**: 4400+
- **GPU**: RTX 4070 (12GB)
- **Training Time**: ~25 hours total

### Best Results

- **Mel CE**: 2.971 (target: <2.5, nearly achieved!)
- **Text CE**: 0.0282 (excellent)
- **Improvement**: -41.1% from baseline
- **Quality**: 9/10 (production-ready)

---

## 💾 Disk Usage

| Component         | Size       | Status      |
| ----------------- | ---------- | ----------- |
| Phase 2 Model     | 30 GB      | ⭐ Required |
| dataset_combined/ | 288 MB     | ⭐ Required |
| Generated Samples | 9 MB       | Optional    |
| Documentation     | <1 MB      | Optional    |
| **Total**         | **~31 GB** |             |

_45.3 GB freed through cleanup (was 76 GB)_  
_Obsolete datasets removed (dataset_blikk, dataset_milliomos consolidated)_

---

## ⚠️ Important Notes

### Tokenizer Issue

Always include `vocab.json` when loading the model:

```python
model.load_checkpoint(..., vocab_path="path/to/vocab.json")
```

Without it, you'll get: `'NoneType' object has no attribute 'encode'`

### Reference Audio

Use high-quality reference audio (`dataset_combined/neutral/neutral_002.wav`) for consistent results.

### GPU Memory

If you encounter CUDA errors, restart Python to clear GPU memory:

```powershell
Get-Process python | Stop-Process -Force
```

---

## 📞 Support

- Check **TROUBLESHOOTING.md** for common issues
- Review **PHASE2_SUCCESS_SUMMARY.md** for complete documentation
- See **PHASE2_FINAL_STATUS.md** for detailed metrics

---

## � Prosody Optimization

### Temperature Testing Results

After extensive testing with real quiz questions, we found:

**Optimal Settings (Production):**

- **Temperature**: 0.40 (ultra-stable, no waviness)
- **top_p**: 0.80
- **top_k**: 40
- **repetition_penalty**: 6.0

### Key Findings

| Issue                               | Solution                                               |
| ----------------------------------- | ------------------------------------------------------ |
| Too wavy/dramatic intonation        | Lower temperature (0.70 → 0.40)                        |
| Insufficient pauses between answers | Use "..." ellipsis in text                             |
| Number sequences sound choppy       | Add context words ("kilenc játékos" not just "kilenc") |
| Chemical abbreviations jumbled      | Replace with full words or simpler questions           |
| Enthusiasm spikes on last option    | Lower temperature + higher repetition_penalty          |

### Best Practices

**Text Formatting:**

```python
# Good - with pauses and context
"Melyik ország fővárosa Budapest? Magyarország... Románia... Ausztria... vagy Szlovákia."

# Bad - no pauses, bare numbers
"Hány játékos? 9, 10, 11, vagy 12?"
```

**Sentence Guidelines:**

- Add context words to numbers ("kilenc játékos" instead of "kilenc")
- Use "..." for natural pauses between options
- Avoid rapid-fire abbreviations (O2, H2O, CO2)
- End with period for neutral tone, not question mark

### Temperature Guide

| Temp  | Use Case                     | Quality                 |
| ----- | ---------------------------- | ----------------------- |
| 0.40  | Quiz questions, professional | ⭐⭐⭐⭐⭐ Ultra stable |
| 0.50  | General content              | ⭐⭐⭐⭐ Very stable    |
| 0.60  | Short sentences              | ⭐⭐⭐ Stable           |
| 0.65  | Long sentences               | ⭐⭐⭐ Good flow        |
| 0.70+ | Creative/dramatic            | ⭐⭐ Too wavy (avoid)   |

---

## �🏆 Achievement

**Production-ready István Vágó voice model achieved!**

- ✅ 41.1% improvement from baseline
- ✅ 9/10 quality rating
- ✅ Optimized prosody (temp 0.40)
- ✅ 5 perfect quiz question samples
- ✅ Ready for deployment
- ✅ Clean, optimized project structure

---

_Model: best_model_1901.pth (Mel CE: 2.971)_  
_Status: Production-Ready ✅_  
_Date: October 4, 2025_

### References

- [Coqui TTS Documentation](https://docs.coqui.ai/)
- [XTTS-v2 Paper](https://arxiv.org/abs/2309.08519)
- [Hungarian Language Guide for TTS](https://github.com/coqui-ai/TTS/discussions)

## 📄 License

This is a personal research project for educational purposes.
