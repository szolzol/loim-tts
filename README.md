# István Vágó Voice Clone - Production Ready 🎯

**Phase 2 training complete! GPU-optimized production-ready voice model.**

---

## 📊 Model Performance

- **Best Model**: `best_model_1901.pth` (Mel CE: 2.971)
- **Total Improvement**: -41.1% from baseline
- **Quality Rating**: 9/10 (production-ready)
- **Training**: 311 samples (Milliomos + Blikk), 4400+ steps
- **Inference**: GPU-accelerated (~3-5 seconds per question on RTX 5070 Ti)

---

## 🚀 Quick Start - Generate Quiz Questions

### Interactive Mode (Recommended)

```powershell
python scripts\generate_questions_and_answers.py
```

The script will prompt you for:

1. **Topic selection** (1-10): Choose from 9 specialized topics or "Vegyes" (mixed)
2. **Question quantity**: How many questions to generate

**Available Topics:**

1. Földrajz (Geography)
2. Történelem (History)
3. Tudomány (Science)
4. Irodalom (Literature)
5. Sport
6. Zene (Music)
7. Film
8. Természet (Nature)
9. Technológia (Technology)
10. **Vegyes** - Random mixed questions from all topics

### Command-Line Mode

```powershell
# Generate 5 music questions
python scripts\generate_questions_and_answers.py 6 5

# Generate 20 mixed questions from all topics
python scripts\generate_questions_and_answers.py 10 20
```

### Output

Samples are saved to `test_samples/` with format: `q001_topic.wav`, `q002_topic.wav`, etc.

---

## 💻 GPU Requirements & Setup

### ⚠️ CRITICAL: RTX 5070 Ti (Blackwell Architecture - sm_120)

**RTX 5070 Ti requires PyTorch 2.7.0+ with CUDA 12.8+**

The RTX 5070 Ti uses CUDA capability sm_120 (Blackwell architecture), which is **NOT supported** by:

- PyTorch 2.1.0 (supports up to sm_90)
- PyTorch 2.6.0 (supports up to sm_90)
- Any PyTorch version before 2.7.0

#### Installation for RTX 5070 Ti

```powershell
# Install PyTorch nightly with CUDA 12.8 support
pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force-reinstall --user

# Install soundfile (required to bypass torchcodec issues)
pip install soundfile
```

#### Verify GPU Support

```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'); print('Capability:', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else 'N/A')"
```

**Expected output for RTX 5070 Ti:**

```
CUDA: True
GPU: NVIDIA GeForce RTX 5070 Ti
Capability: (12, 0)  # This is sm_120 ✅
```

### For Older GPUs (RTX 4070 and earlier)

If you have a GPU with CUDA capability ≤ sm_90 (RTX 4090, 4080, 4070, 3090, etc.), use stable PyTorch:

```powershell
pip install torch==2.1.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install soundfile
```

---

## 📦 Installation

### 1. Clone Repository

```powershell
git clone https://github.com/szolzol/loim-tts.git
cd loim-tts
```

### 2. Install Dependencies

```powershell
# Install all requirements (automatically detects GPU type)
pip install -r requirements.txt

# OR manually for RTX 5070 Ti:
pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --user
pip install TTS==0.22.0 soundfile numpy>=1.26.4
```

### 3. Download Model

Download the Phase 2 trained model (30 GB):

- **Model**: `run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd/`
  - `best_model_1901.pth` (5.22 GB) ⭐
  - `config.json`
  - `vocab.json`

### 4. Verify Reference Audio

Ensure reference audio exists:

- `prepared_sources/neutral/neutral_002.wav`

---

## 📁 Project Structure

```
tts-2/
├── run/training_combined_phase2/
│   └── XTTS_Combined_Phase2-.../
│       ├── best_model_1901.pth   ⭐ Production model (5.22 GB)
│       ├── config.json
│       └── vocab.json
│
├── scripts/
│   ├── generate_questions_and_answers.py  ⭐ Quiz generator (GPU-optimized)
│   ├── prepare_dataset.py                 ⭐ Dataset preparation
│   └── train_combined_phase2.py           ⭐ Phase 2 training/fine-tuning
│
├── models/
│   ├── dvae.pth                          ⭐ Required for training
│   └── mel_stats.pth                     ⭐ Required for training
│
├── prepared_sources/                     ⭐ Prepared training audio (288 MB)
│   ├── metadata.csv                      Audio + transcript pairs
│   ├── neutral/neutral_002.wav           Reference audio for inference
│   └── [confirmation, excitement, question, etc.]/ Categorized samples
│
├── source_audio/                         📁 Full-length source recordings
│   └── Full quiz show WAV files with speaker voice
│
├── test_samples/                         📁 Script output folder
│   └── Generated quiz question samples (q001_topic.wav, etc.)
│
├── backup_obsolete/                      📁 Old files (gitignored)
│   └── Obsolete scripts, test samples, old documentation
│
└── Documentation:
    ├── README.md                         ⭐ This file
    ├── requirements.txt                  Dependencies
    ├── .gitignore                        Git ignore rules
    ├── ENVIRONMENT_FIX_GUIDE.md          GPU troubleshooting
    ├── TORCHCODEC_FIX.md                 Soundfile workaround
    └── PHASE2_SUCCESS_SUMMARY.md         Training results
```

### 📂 Folder Descriptions

- **`run/training_combined_phase2/`**: Contains the trained Phase 2 model checkpoint and configuration files
- **`scripts/`**: Essential scripts for generation, dataset prep, and training
- **`models/`**: Pre-trained DVAE and mel normalization files required for training
- **`prepared_sources/`**: Prepared audio samples with metadata for training (Milliomos + Blikk combined)
- **`source_audio/`**: Original full-length quiz show recordings (source WAV files)
- **`test_samples/`**: Output directory for generated quiz questions from the script
- **`backup_obsolete/`**: Old/experimental files moved here (added to .gitignore)

---

## 🎤 Generation Features

### Optimized Parameters

The script uses optimized inference parameters discovered through extensive testing:

- **Temperature**: 0.4 (ultra-stable, no waviness)
- **Top_p**: 0.88
- **Top_k**: 50
- **Repetition penalty**: 6.5
- **Length penalty**: 1.25
- **Text splitting**: Enabled (handles long texts better)
- **Reference**: Single `neutral_002.wav` (best quality)

### Automatic Phonetic Conversion

English names are automatically converted to phonetic Hungarian:

- "William Shakespeare" → "Vilyem Sékszpír"
- "Harrison Ford" → "Heriszon Ford"
- "Wolfgang Amadeus Mozart" → "Volfgáng Amádéusz Móczárt"

### Pause Structure

Natural pauses for quiz show format:

- **7 dots** after question: `"Kérdés?......."` (~1.5s pause)
- **5 dots** between answers: `"Áá. Válasz1..... Béé. Válasz2....."` (~0.8s pause)

---

## 🔧 Training & Fine-tuning

### Step 1: Prepare Dataset

```powershell
python scripts\prepare_dataset.py
```

This script creates `metadata.csv` with audio+transcript pairs in the correct format for training.

**Input:**
- Raw audio files in `source_audio/` or any folder
- Transcripts (text files or manual entry)

**Output:**
- `prepared_sources/metadata.csv`
- Organized audio files in categorized folders

### Step 2: Train or Fine-tune Model

```powershell
python scripts\train_combined_phase2.py
```

**Purpose:** 
- **Initial Training**: Train a new voice model from scratch
- **Fine-tuning (Phase 2)**: Continue training from an existing checkpoint to improve quality

**Requirements:**

- `models/dvae.pth` (auto-downloaded if missing)
- `models/mel_stats.pth` (auto-downloaded if missing)
- Prepared dataset with `metadata.csv` in `prepared_sources/`

**Configure in script:**

```python
OUTPUT_PATH = "run/training_combined_phase2"
DATASET_PATH = "prepared_sources"
RESUME_CHECKPOINT = "path/to/checkpoint.pth"  # Leave empty for training from scratch

# Training parameters
BATCH_SIZE = 3
NUM_EPOCHS = 30
LEARNING_RATE = 1e-6  # Lower for fine-tuning, higher (5e-6) for initial training
```

**Training Process:**
1. Loads dataset from `prepared_sources/`
2. Automatically downloads DVAE and mel_stats if needed
3. Resumes from checkpoint (if specified) or starts fresh
4. Saves checkpoints every 100 steps
5. Auto-cleanup keeps only last 2 checkpoints to save space
6. Final model saved as `best_model.pth`

**Expected Results:**
- Phase 1 (Initial): Mel CE ~3.5 after 1500-2000 steps
- Phase 2 (Fine-tune): Mel CE ~2.97 after additional 2000-3000 steps
- Training time: ~10-15 hours per phase on RTX 4070/5070 Ti

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
- **Training Time**: ~25 hours total

### Best Results

- **Mel CE**: 2.971 (excellent smoothness)
- **Text CE**: 0.0282 (excellent pronunciation)
- **Improvement**: -41.1% from baseline
- **Quality**: 9/10 (production-ready)

---

## 🐛 Troubleshooting

### GPU Not Detected

**Symptom**: Model loads on CPU instead of CUDA

**Solution for RTX 5070 Ti**:

```powershell
# Verify your PyTorch version supports sm_120
python -c "import torch; print(torch.__version__)"

# Should be 2.10.0.dev or later with cu128
# If not, reinstall:
pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force-reinstall --user
```

### Torchaudio Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'torchcodec'`

**Solution**: The script uses `soundfile` to bypass this issue automatically. Ensure `soundfile` is installed:

```powershell
pip install soundfile
```

### CUDA Out of Memory

**Symptom**: `CUDA out of memory` error during generation

**Solution**:

```powershell
# Restart Python to clear GPU memory
Get-Process python | Stop-Process -Force

# Then run script again
python scripts\generate_questions_and_answers.py
```

### Model Loading Error (vocab.json)

**Symptom**: `'NoneType' object has no attribute 'encode'`

**Solution**: Always ensure `vocab.json` is in the same directory as the model checkpoint. The script automatically loads it from the model directory.

---

## 💾 Disk Usage

| Component                 | Size       | Required      |
| ------------------------- | ---------- | ------------- |
| Phase 2 Model             | 30 GB      | ✅ Yes        |
| prepared_sources/         | 288 MB     | ✅ Yes        |
| models/ (dvae, mel_stats) | ~1 GB      | Training only |
| Generated Samples         | Varies     | No            |
| Documentation             | <1 MB      | No            |
| **Total (Minimum)**       | **~31 GB** |               |

---

## 📚 Additional Documentation

- **ENVIRONMENT_FIX_GUIDE.md**: Detailed GPU troubleshooting for RTX 5070 Ti
- **TORCHCODEC_FIX.md**: Technical details on soundfile workaround
- **PHASE2_SUCCESS_SUMMARY.md**: Complete training results and methodology

---

## 🏆 Key Achievements

✅ **Production-ready model** with 9/10 quality rating  
✅ **41.1% improvement** from baseline (Mel CE: 5.046 → 2.971)  
✅ **GPU-optimized inference** (~3-5 seconds per question on RTX 5070 Ti)  
✅ **9 specialized topics** + mixed mode for varied content  
✅ **Automatic phonetic conversion** for English names  
✅ **RTX 5070 Ti Blackwell (sm_120) support** fully working

---

## 📄 License

This is a personal research project for educational purposes.

---

## 🔗 References

- [Coqui TTS Documentation](https://docs.coqui.ai/)
- [XTTS-v2 Paper](https://arxiv.org/abs/2309.08519)
- [PyTorch CUDA Compatibility](https://pytorch.org/get-started/locally/)

---

_Model: best_model_1901.pth (Mel CE: 2.971)_  
_Status: Production-Ready ✅_  
_Last Updated: October 8, 2025_
