# István Vágó Voice Clone - TTS API Ready 🎯

**Production-ready voice model with multi-reference inference and batch generation capabilities.**

---

## 🎉 Latest Updates (2025.10.08)

✅ **Multi-Reference Inference** - Successfully implemented 3-reference audio system  
✅ **Batch Generation** - JSON-based template system for mass production  
✅ **Segmented Mode** - Explicit pause control between answer options  
✅ **MP3/WAV Output** - Flexible output formats  
✅ **API Development Ready** - Prepared for FastAPI wrapper and Railway deployment

---

## 📊 Model Performance

- **Best Model**: `best_model_1901.pth` (Mel CE: 2.971)
- **Total Improvement**: -41.1% from baseline
- **Quality Rating**: 9/10 (production-ready)
- **Training**: 311 samples (Milliomos + Blikk), 4400+ steps
- **Multi-Reference**: 3 audio files (neutral, excitement, question)
- **Inference**: GPU-accelerated (~3-5 seconds per question on RTX 5070 Ti)

---

## ✨ Key Features

### 1. Multi-Reference Inference ✅

- **3 reference audios** used simultaneously for natural prosody
- Combines neutral, excitement, and question intonations
- Better quality than single-reference approach

### 2. Batch Generation from JSON ✅

- Edit `input_samples.json` template
- Generate multiple samples in one run
- Support for simple and segmented modes
- Automatic MP3 conversion

### 3. Segmented Generation ✅

- Explicit pause control (0.5s - 0.7s)
- Perfect for quiz questions with answer options
- No more rushed speech between answers
- Clean, distinct pauses

---

## 🚀 Quick Start

### Method 1: Batch Generation from JSON (Recommended) ⭐

Edit `input_samples.json` and run:

```powershell
python batch_generate.py
```

**Example JSON config:**

```json
{
  "generation_config": {
    "model_checkpoint": "best_model_1901.pth",
    "output_format": "mp3",
    "multi_reference": true,
    "parameters": {
      "temperature": 0.4,
      "top_p": 0.88,
      "repetition_penalty": 6.5
    }
  },
  "samples": [
    {
      "id": "greeting",
      "text": "Üdvözöllek a kvízjátékban!",
      "segmented": false
    },
    {
      "id": "quiz_question",
      "segmented": true,
      "segments": [
        { "text": "Ki írta a Rómeó és Júliát?", "pause_after": 0.5 },
        { "text": "A válaszlehetőségek:", "pause_after": 0.5 },
        { "text": "Áá, Shakespeare.", "pause_after": 0.7 },
        { "text": "Béé, Dickens.", "pause_after": 0.0 }
      ]
    }
  ]
}
```

**Output**: MP3 files in `generated_output/` directory  
**See**: `BATCH_GENERATOR_README.md` for full documentation

---

### Method 2: Quiz Questions Generator

#### Interactive Mode

```powershell
python scripts\generate_questions_and_answers.py
```

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
10. **Vegyes** - Random mixed questions

#### Command-Line Mode

```powershell
# Generate 5 music questions
python scripts\generate_questions_and_answers.py 6 5

# Generate 20 mixed questions
python scripts\generate_questions_and_answers.py 10 20
```

**Output**: WAV files in `test_samples/` directory

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

Ensure multi-reference audio exists:

- `prepared_sources/vago_samples_first_source/neutral/neutral_002.wav`
- `prepared_sources/vago_samples_first_source/excitement/excitement_005.wav`
- `prepared_sources/vago_samples_first_source/question/question_003.wav`

---

## 📁 Project Structure

```
tts-2/
├── batch_generate.py                     ⭐⭐ NEW: Batch generator from JSON
├── input_samples.json                    ⭐⭐ NEW: Editable template file
│
├── run/training_combined_phase2/
│   └── XTTS_Combined_Phase2-.../
│       ├── best_model_1901.pth           ⭐ Production model (5.22 GB)
│       ├── config.json
│       └── vocab.json
│
├── scripts/
│   ├── generate_questions_and_answers.py ⭐ Quiz generator (multi-ref + segmented)
│   ├── prepare_dataset.py                Dataset preparation
│   └── train_combined_phase2.py          Phase 2 training/fine-tuning
│
├── models/
│   ├── dvae.pth                          ⭐ Required for training
│   └── mel_stats.pth                     ⭐ Required for training
│
├── prepared_sources/
│   └── vago_samples_first_source/        ⭐⭐ Multi-reference audios
│       ├── neutral/neutral_002.wav       Neutral tone
│       ├── excitement/excitement_005.wav Excited tone
│       └── question/question_003.wav     Question intonation
│
├── generated_output/                     ⭐⭐ NEW: Batch generator output (MP3)
│   └── sample_001.mp3, sample_002.mp3, ...
│
├── test_samples/                         📁 Quiz generator output (WAV)
│   └── q001_irodalom.wav, q002_irodalom.wav, ...
│
├── Documentation:
│   ├── README.md                         ⭐ This file
│   ├── BATCH_GENERATOR_README.md         ⭐⭐ Batch generation guide
│   └── API_DEVELOPMENT_PLAN.md           ⭐⭐ API development roadmap
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

### Multi-Reference Inference ⭐⭐ NEW

The system now uses **3 reference audios simultaneously** for better prosody:

- **neutral_002.wav**: Baseline calm tone
- **excitement_005.wav**: Enthusiastic intonation
- **question_003.wav**: Question prosody

This creates more natural-sounding speech compared to single-reference mode.

### Optimized Parameters

Carefully tuned inference parameters:

- **Temperature**: 0.4 (ultra-stable, no waviness)
- **Top_p**: 0.88
- **Top_k**: 50
- **Repetition penalty**: 6.5 (prevents "uhhh" and repetitions)
- **Length penalty**: 1.25
- **Text splitting**: Enabled for long texts

### Segmented Generation Mode ⭐⭐ NEW

**Problem**: Previous versions rushed through answer options without pauses

**Solution**: Segmented generation with explicit silence

```json
{
  "segments": [
    { "text": "Question?", "pause_after": 0.5 },
    { "text": "A válaszlehetőségek:", "pause_after": 0.5 },
    { "text": "Áá, Answer 1.", "pause_after": 0.7 },
    { "text": "Béé, Answer 2.", "pause_after": 0.7 }
  ]
}
```

Each segment generates separately, then concatenates with **explicit silence** (0.5s - 0.7s).

**Results**:

- ✅ Clear pauses between answers
- ✅ Natural pacing
- ✅ No rushed speech
- ✅ Professional quiz show quality

### Automatic Phonetic Conversion

English names are automatically converted to phonetic Hungarian:

- "William Shakespeare" → "Vilyem Sékszpír"
- "Harrison Ford" → "Heriszon Ford"
- "Wolfgang Amadeus Mozart" → "Volfgáng Amádéusz Móczárt"

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
✅ **Multi-reference inference** (3 audios for natural prosody) ⭐⭐ NEW  
✅ **Batch generation** from JSON templates ⭐⭐ NEW  
✅ **Segmented mode** with explicit pauses ⭐⭐ NEW  
✅ **MP3/WAV output** flexibility ⭐⭐ NEW  
✅ **GPU-optimized inference** (~3-5 seconds per question on RTX 5070 Ti)  
✅ **9 specialized topics** + mixed mode for varied content  
✅ **Automatic phonetic conversion** for English names  
✅ **RTX 5070 Ti Blackwell (sm_120) support** fully working  
✅ **API-ready architecture** - prepared for FastAPI wrapper

---

## 🚀 Next Steps - API Development

**Current Status**: Infrastructure complete, ready for API wrapper

**Planned Features**:

1. FastAPI REST endpoints
2. POST `/generate/simple` - Single text to MP3
3. POST `/generate/segmented` - Quiz questions with pauses
4. Railway deployment with Docker
5. Model caching and optimization
6. Rate limiting and authentication

**See**: `API_DEVELOPMENT_PLAN.md` for detailed roadmap

---

## 📄 License

This is a personal research project for educational purposes.

---

## 🔗 References

- [Coqui TTS Documentation](https://docs.coqui.ai/)
- [XTTS-v2 Paper](https://arxiv.org/abs/2309.08519)
- [PyTorch CUDA Compatibility](https://pytorch.org/get-started/locally/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

_Model: best_model_1901.pth (Mel CE: 2.971)_  
_Status: Production-Ready + API-Ready ✅_  
_Last Updated: October 8, 2025_
