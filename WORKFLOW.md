# István Vágó XTTS-v2 Voice Cloning Project
## Complete Workflow & Implementation Plan

---

## 📋 Project Overview

**Objective**: Create a production-quality Hungarian voice clone of István Vágó (legendary quiz show host) using Coqui XTTS-v2 for building an interactive quiz application.

**Target Quality**: ElevenLabs / Fish Audio level
- Naturalness: 4.5+/5.0 MOS
- Speaker Similarity: 4.5+/5.0
- Intelligibility: 95%+
- Natural Hungarian prosody and intonation

**Environment**:
- OS: Windows 10/11
- GPU: NVIDIA RTX 4070 (12GB VRAM)
- Python: 3.9-3.11
- CUDA: 11.8

---

## 🗺️ Complete Workflow

### Phase 1: Environment Setup ⚙️
**Duration**: 10-15 minutes  
**Status**: ✅ Ready to execute

**Steps**:
1. ✅ Run `scripts\setup_environment.ps1`
2. ✅ Verify installation with `scripts\check_system.py`
3. ✅ **Git Checkpoint**: "Environment setup complete"

**Deliverables**:
- Python virtual environment (`xtts_env/`)
- All dependencies installed
- GPU verified and functional

---

### Phase 2: Dataset Preparation 📊
**Duration**: 30-60 minutes (including manual transcription)  
**Status**: ⏳ Ready to start

**Steps**:

#### 2.1 Automatic Preprocessing
```powershell
python scripts\prepare_dataset.py
```

This script:
- ✅ Loads 13 audio clips from `source_clips/`
- ✅ Converts to mono, 22050 Hz
- ✅ Applies noise reduction
- ✅ Trims silence aggressively
- ✅ Normalizes audio (RMS + peak limiting)
- ✅ Saves to `dataset/wavs/`
- ✅ Creates initial `dataset/metadata.csv`
- ✅ Generates quality statistics

#### 2.2 Manual Transcription (CRITICAL!)
```powershell
# Edit this file with accurate Hungarian text:
dataset\metadata.csv
```

**Format** (pipe-delimited):
```
filename|transcription|speaker_name
1_vago_finetune2|Üdvözlöm önöket a kvízműsorban!|istvan_vago
```

**Requirements**:
- ✅ Accurate word-for-word transcription
- ✅ Proper Hungarian diacritics (á, é, í, ó, ö, ő, ú, ü, ű)
- ✅ Natural punctuation for prosody
- ✅ Match speaking style and emphasis

**Pro Tip**: Use a native Hungarian speaker to verify transcriptions!

#### 2.3 Validation
```powershell
# Run dataset prep again to verify
python scripts\prepare_dataset.py
```

Check output:
- ✅ Total duration: 10+ minutes ideal (currently ~1.7 min - may need more data)
- ✅ Average SNR: >20 dB
- ✅ All files processed successfully
- ✅ No errors in metadata.csv

**Git Checkpoint**: "Dataset prepared and validated"

---

### Phase 3: Initial Training 🚀
**Duration**: 6-8 hours (RTX 4070)  
**Status**: ⏳ Pending dataset completion

**Steps**:

#### 3.1 Pre-Training Check
```powershell
# Verify everything is ready
python scripts\check_system.py
```

#### 3.2 Start Training
```powershell
python scripts\train_xtts.py
```

**What happens**:
1. Downloads XTTS-v2 base model (~1.5 GB)
2. Loads training dataset
3. Initializes model with Hungarian support
4. Trains for 25 epochs (~15-20 min per epoch)
5. Saves checkpoints every 500 steps
6. Generates test audio every few epochs

#### 3.3 Monitor Training
```powershell
# In a separate terminal
tensorboard --logdir run\training
# Open: http://localhost:6006
```

**Key metrics to watch**:
- `train/total_loss` - Should decrease steadily
- `eval/total_loss` - Should plateau (not increase)
- Gap between train/eval - If too large = overfitting

#### 3.4 Listen to Samples
Check generated test audio during training:
```
run\training\[run_name]\test_audios\
```

Listen for:
- ✅ Voice similarity to István Vágó
- ✅ Clear Hungarian pronunciation
- ✅ Natural prosody
- ❌ Robotic sound (sign of issues)
- ❌ Artifacts (clicks, pops)

**Git Checkpoint**: "First training run complete"

---

### Phase 4: Evaluation & Iteration 🔍
**Duration**: 2-4 hours  
**Status**: ⏳ After training

**Steps**:

#### 4.1 Generate Test Samples
```powershell
python scripts\inference.py
```

Choose option 1: Generate quiz show samples

#### 4.2 Quality Assessment

**Subjective Evaluation** (listen to outputs):
- [ ] Sounds like István Vágó? (1-5 score)
- [ ] Natural Hungarian speech? (1-5 score)
- [ ] Clear pronunciation? (1-5 score)
- [ ] Appropriate prosody/emotion? (1-5 score)
- [ ] No artifacts/glitches? (yes/no)

**Objective Evaluation**:
```powershell
# Compare with original Vágó clips
# Use audio analysis tools to measure similarity
```

#### 4.3 Identify Issues

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Robotic | Overfitting | Reduce epochs, more data |
| Wrong words | Bad transcriptions | Fix metadata.csv |
| Monotone | Not enough prosody | More expressive samples |
| Artifacts | Noisy data | Better preprocessing |
| Wrong accent | Wrong language code | Verify LANGUAGE = "hu" |

#### 4.4 Iteration Plan

If quality insufficient:
1. **More data**: Collect additional Vágó clips (target: 15-30 min)
2. **Better transcriptions**: Re-verify accuracy
3. **Hyperparameter tuning**: Adjust learning rate, temperature
4. **Resume training**: Load best checkpoint and continue

**Git Checkpoint**: "Evaluation complete - iteration plan defined"

---

### Phase 5: Optimization & Fine-Tuning 🎯
**Duration**: Variable (multiple training runs)  
**Status**: ⏳ After evaluation

**Strategies**:

#### 5.1 Data Enhancement
- Collect more István Vágó audio (YouTube, TV archives)
- Ensure diverse content (questions, answers, excitement)
- Target: 20-30 minutes total

#### 5.2 Hyperparameter Optimization
```python
# In scripts/train_xtts.py

# Try different learning rates
LEARNING_RATE = 3e-6  # More conservative
LEARNING_RATE = 7e-6  # More aggressive

# Adjust training duration
NUM_EPOCHS = 20  # Shorter (if overfitting)
NUM_EPOCHS = 30  # Longer (if underfit)
```

#### 5.3 Inference Tuning
```python
# In scripts/inference.py

# For more consistency
TEMPERATURE = 0.65

# For more expressiveness
TEMPERATURE = 0.85

# For better quality (experiment)
TOP_P = 0.90
REPETITION_PENALTY = 6.0
```

#### 5.4 Multi-Stage Training
```python
# Stage 1: Warm-up (5 epochs, lr=1e-6)
# Stage 2: Main (15 epochs, lr=5e-6)  
# Stage 3: Polish (5 epochs, lr=1e-6)
```

**Git Checkpoint**: "Optimized model - quality improved"

---

### Phase 6: Production Deployment 🎬
**Duration**: 1-2 days  
**Status**: ⏳ After quality approval

**Steps**:

#### 6.1 Final Model Selection
- Choose best checkpoint based on evaluations
- Document final hyperparameters
- Archive training logs

#### 6.2 Quiz Application Integration
```python
# Example integration for quiz app

from scripts.inference import load_model, compute_speaker_latents, synthesize_speech

# Load once at app startup
model = load_model()
latents = compute_speaker_latents(model)

# Generate quiz audio on demand
def generate_quiz_audio(question_text):
    output_path = f"quiz_audio/{question_id}.wav"
    synthesize_speech(
        model, 
        question_text, 
        latents[0], 
        latents[1], 
        output_path
    )
    return output_path
```

#### 6.3 Performance Optimization
- Batch inference for multiple questions
- Caching commonly used phrases
- GPU memory management

#### 6.4 Quality Assurance Testing
- Generate 50+ quiz questions
- Native speaker review
- A/B testing with users
- Stress testing (many requests)

**Git Checkpoint**: "Production ready - v1.0"

---

## 📊 Current Status

### Completed ✅
- [x] Project structure created
- [x] Environment setup script (PowerShell)
- [x] Dataset preparation script
- [x] Training script (Windows/RTX 4070 optimized)
- [x] Inference script with quiz mode
- [x] Documentation (README, QUICKSTART, QUALITY_GUIDE)
- [x] System check utility
- [x] Git repository initialized
- [x] Initial git checkpoint created

### In Progress 🔄
- [ ] Dataset transcriptions (manual task)
- [ ] First training run
- [ ] Quality evaluation

### Pending ⏳
- [ ] Iteration and optimization
- [ ] Final model selection
- [ ] Quiz app integration
- [ ] Production deployment

---

## 🎯 Success Metrics

### Technical Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Training Loss | <2.0 | TBD | ⏳ |
| Eval Loss | <2.5 | TBD | ⏳ |
| Audio Duration | 15+ min | ~1.7 min | ⚠️ Need more |
| SNR | >20 dB | TBD | ⏳ |
| Inference Time | <500ms | TBD | ⏳ |

### Quality Metrics (MOS 1-5)
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Naturalness | 4.5+ | TBD | ⏳ |
| Speaker Similarity | 4.5+ | TBD | ⏳ |
| Intelligibility | 4.8+ | TBD | ⏳ |
| Prosody | 4.3+ | TBD | ⏳ |

---

## 🚨 Known Issues & Risks

### Critical ⚠️
1. **Limited training data** (~1.7 min vs 15+ min recommended)
   - **Risk**: Poor quality, overfitting
   - **Mitigation**: Collect more István Vágó audio ASAP

2. **Transcription accuracy** (currently placeholders)
   - **Risk**: Model learns wrong pronunciations
   - **Mitigation**: Native Hungarian speaker verification

### Important ❗
3. **GPU memory constraints** (12GB RTX 4070)
   - **Risk**: OOM errors during training
   - **Mitigation**: BATCH_SIZE=2, gradient accumulation

4. **Hungarian language specifics** (diacritics, phonemes)
   - **Risk**: Loss of language characteristics
   - **Mitigation**: Accurate transcriptions, proper tokenization

### Nice to Have 💡
5. **Training time** (~6-8 hours per run)
   - **Impact**: Slow iteration
   - **Optimization**: Use cloud GPU for parallel experiments

---

## 📚 Resource Links

### Documentation
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Step-by-step guide
- [QUALITY_GUIDE.md](QUALITY_GUIDE.md) - Achieving top quality

### Scripts
- `scripts/setup_environment.ps1` - Environment setup
- `scripts/prepare_dataset.py` - Dataset preprocessing
- `scripts/train_xtts.py` - Training pipeline
- `scripts/inference.py` - Audio generation
- `scripts/check_system.py` - System diagnostics
- `scripts/git_checkpoint.ps1` - Version control

### External Resources
- [Coqui TTS Docs](https://docs.coqui.ai/)
- [XTTS-v2 Paper](https://arxiv.org/abs/2309.08519)
- [Hungarian TTS Resources](https://github.com/coqui-ai/TTS/discussions)

---

## 🎬 Next Actions (Priority Order)

1. **IMMEDIATE**: Run environment setup
   ```powershell
   .\scripts\setup_environment.ps1
   ```

2. **TODAY**: Prepare dataset
   ```powershell
   python scripts\prepare_dataset.py
   ```

3. **TODAY**: Create accurate transcriptions
   - Edit `dataset\metadata.csv`
   - Verify with native speaker if possible

4. **TODAY**: Start first training run
   ```powershell
   python scripts\train_xtts.py
   ```

5. **TOMORROW**: Evaluate results and plan iteration

6. **THIS WEEK**: 
   - Collect more István Vágó audio (critical!)
   - Iterate on hyperparameters
   - Optimize for quality

7. **NEXT WEEK**: 
   - Finalize production model
   - Integrate with quiz app
   - User testing

---

## 💾 Git Checkpoints

Create checkpoints at these milestones:

```powershell
# After environment setup
.\scripts\git_checkpoint.ps1 -CheckpointName "Environment-Setup" -Message "Python env, dependencies, GPU verified"

# After dataset prep
.\scripts\git_checkpoint.ps1 -CheckpointName "Dataset-Ready" -Message "Audio preprocessed, transcriptions complete"

# After first training
.\scripts\git_checkpoint.ps1 -CheckpointName "Training-V1" -Message "First training run complete, 25 epochs"

# After optimization
.\scripts\git_checkpoint.ps1 -CheckpointName "Optimized-Model" -Message "Hyperparameters tuned, quality improved"

# Production release
.\scripts\git_checkpoint.ps1 -CheckpointName "Production-V1.0" -Message "Production-ready model, quality approved"
```

---

## 🎓 Learning & Iteration Log

Document your findings as you go:

```markdown
### Training Run #1 (2025-10-02)
- Hyperparameters: LR=5e-6, EPOCHS=25, BATCH=2
- Duration: ~6 hours
- Results: [quality score, observations]
- Issues: [any problems encountered]
- Next steps: [improvements to try]

### Training Run #2 (2025-10-03)
- Changes: [what you modified]
- Results: [improved? worse?]
- Learnings: [insights gained]
```

---

**Remember**: Achieving commercial-grade TTS quality is iterative. Don't expect perfection on the first try. Each training run teaches you something valuable! 🚀
