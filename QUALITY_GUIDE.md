# Achieving ElevenLabs/Fish Audio Quality with XTTS-v2

This guide documents best practices for achieving commercial-grade TTS quality with Coqui XTTS-v2.

## 🎯 Quality Targets

### Subjective Metrics (MOS - Mean Opinion Score, 1-5 scale)
- **Naturalness**: 4.5+ (sounds like real human speech)
- **Intelligibility**: 4.8+ (words are clear and understandable)
- **Speaker Similarity**: 4.5+ (sounds like the target speaker)
- **Prosody**: 4.3+ (natural rhythm, intonation, emphasis)

### Objective Metrics
- **Word Error Rate (WER)**: <5%
- **Signal-to-Noise Ratio**: >25 dB
- **Latency**: <500ms for real-time applications
- **Consistency**: Minimal variation between generations

## 📊 ElevenLabs vs Fish Audio vs XTTS-v2

### ElevenLabs Strengths
- Extremely natural prosody
- Excellent emotional control
- Very low latency (<200ms)
- Consistent quality across languages

### Fish Audio Strengths  
- High fidelity in target language
- Excellent cloning with minimal data
- Good preservation of voice characteristics
- Fast inference

### XTTS-v2 Strengths
- **Open source** and locally runnable
- Multi-lingual by design (17 languages)
- Can match commercial quality with proper tuning
- Full control over model and data
- No API costs or rate limits

## 🎤 Dataset Preparation (Critical for Quality)

### 1. Audio Quality Requirements

#### Minimum Standards
- **Sample Rate**: 22050 Hz (training), 24000 Hz (output)
- **Bit Depth**: 16-bit or higher
- **Format**: WAV (lossless)
- **Channels**: Mono
- **SNR**: >20 dB (higher is better)
- **Dynamic Range**: Good variation (avoid over-compression)

#### Optimal Standards
- Clean studio recordings
- No background music or noise
- Consistent recording environment
- Minimal reverb (unless characteristic of voice)
- No audio processing artifacts
- Proper mic technique (no pops, clicks, distortion)

### 2. Audio Preprocessing Pipeline

```python
# Our pipeline (implemented in prepare_dataset.py):

1. Load audio → mono, 22050 Hz
2. Noise reduction (subtle, 0.8 reduction)
3. Aggressive silence trimming
4. RMS normalization (target: 0.1)
5. Peak limiting (prevent clipping at 0.95)
6. Duration filtering (2-15 seconds)
```

### 3. Dataset Size

| Duration | Quality Expected |
|----------|------------------|
| 5-10 min | Acceptable for testing |
| 10-20 min | Good quality possible |
| 20-30 min | Very good quality |
| 30+ min | Excellent quality |

**István Vágó Dataset**: ~13 clips × 8 seconds = ~1.7 minutes
- ⚠️ This is MINIMAL - recommend collecting 15-30 minutes for production quality

### 4. Text Transcriptions

**Critical Importance**: Transcription accuracy directly affects quality!

#### Hungarian Specific Considerations
- Use proper diacritics: á, é, í, ó, ö, ő, ú, ü, ű
- Accurate punctuation for prosody
- Natural sentence structure
- Match speaking style (quiz show formal/enthusiastic tone)

#### Transcription Guidelines
```
✅ GOOD: "Üdvözlöm önöket a kvízműsorban!"
❌ BAD:  "Udvozlom onoket a kviзmusorban!" (wrong encoding)
❌ BAD:  "udvozlom onoket a kvizmusorban" (no capitals, accents)
```

## ⚙️ Training Hyperparameters for Quality

### Learning Rate Strategy
```python
# Conservative for quality
LEARNING_RATE = 5e-6  # Start conservative

# Learning rate scheduling
lr_scheduler = "StepLR"
step_size = 50  # Reduce every 50 steps
gamma = 0.5  # Halve learning rate
```

### Batch Size and Accumulation
```python
# RTX 4070 (12GB) optimized
BATCH_SIZE = 2
GRAD_ACCUM_STEPS = 126
# Effective batch size = 2 × 126 = 252 ✅

# Why 252? XTTS paper recommends ≥252 for stable training
```

### Training Duration
```python
EPOCHS = 25  # Start here
# Monitor validation loss - stop when plateaus
# Typical: 15-30 epochs for fine-tuning
```

### Early Stopping
```python
# Stop training if validation loss doesn't improve for N steps
# Prevents overfitting while maintaining quality
```

## 🎛️ Inference Parameters for Maximum Quality

### Temperature (Diversity vs Consistency)
```python
TEMPERATURE = 0.75  # Sweet spot for quality
# 0.5-0.7: More consistent, less expressive
# 0.75-0.85: Balanced (RECOMMENDED)
# 0.9-1.2: More expressive, less consistent
```

### Sampling Parameters
```python
TOP_P = 0.85  # Nucleus sampling
TOP_K = 50    # Top-k sampling
REPETITION_PENALTY = 5.0  # Prevent word repetition
LENGTH_PENALTY = 1.0  # Natural length
```

### Speaker Conditioning
```python
# Use 2-3 high-quality reference clips
REFERENCE_AUDIO = [
    "clip1.wav",  # Clear, representative
    "clip2.wav",  # Different prosody
    "clip3.wav",  # Different content
]
```

## 🔬 Quality Evaluation Methods

### 1. Subjective Listening Tests
- **ABX Testing**: Compare your model vs reference
- **MOS Scoring**: Rate 1-5 on naturalness, similarity, etc.
- **Native Speaker Evaluation**: Critical for Hungarian accuracy

### 2. Objective Metrics
```python
# Automated testing (implement after training)
- WER (Word Error Rate) using ASR
- MCD (Mel Cepstral Distortion)
- Speaker embedding distance (cosine similarity)
- Prosody similarity metrics
```

### 3. A/B Testing Against Benchmarks
- Generate same text with:
  - Your model
  - Original Vágó audio (if available)
  - ElevenLabs (for comparison)
  - Fish Audio (for comparison)

## 🚀 Advanced Techniques for Quality Boost

### 1. Data Augmentation (Carefully!)
```python
# Subtle augmentations that preserve voice characteristics
- Slight pitch variation (±5%)
- Mild time stretching (±5%)
- Subtle EQ variations
⚠️ Over-augmentation can hurt quality!
```

### 2. Multi-Stage Training
```python
# Stage 1: Warm-up (5 epochs, lr=1e-6)
# Stage 2: Main training (15 epochs, lr=5e-6)
# Stage 3: Fine-tuning (5 epochs, lr=1e-6)
```

### 3. Ensemble Reference Audio
```python
# Use diverse references for conditioning
- Different emotions/tones
- Different phonetic content
- Different speaking rates
```

### 4. Post-Processing (Minimal!)
```python
# Light post-processing can help
- Gentle normalization
- Subtle de-essing
- Light compression (1.5:1 max)
⚠️ Avoid heavy processing - it introduces artifacts
```

## 📈 Quality Progression Timeline

### Week 1: Setup & Data Preparation
- Collect and clean audio
- Accurate transcriptions
- Verify dataset quality
- **Checkpoint**: Dataset ready

### Week 2: Initial Training
- First training run (15 epochs)
- Monitor validation loss
- Generate samples every 5 epochs
- **Checkpoint**: First working model

### Week 3: Iteration & Optimization
- Adjust hyperparameters based on results
- Collect more data if needed
- Fine-tune with best checkpoint
- **Checkpoint**: Optimized model

### Week 4: Evaluation & Refinement
- Comprehensive quality testing
- A/B comparisons
- Final adjustments
- **Checkpoint**: Production-ready model

## 🎯 Hungarian Language Specific Tips

### Phonetic Considerations
- Hungarian has 14 vowels (including long vowels)
- Consonant clusters need clear articulation
- Vowel harmony patterns
- Characteristic intonation patterns

### Training Data Composition
```
Recommended mix for quiz show voice:
- 60% Questions (rising intonation)
- 20% Answers/confirmations (falling intonation)
- 10% Excitement/enthusiasm
- 10% Explanations (neutral)
```

### Common Pitfalls
```
❌ English phoneme substitution
❌ Missing vowel length distinctions
❌ Incorrect stress patterns
❌ Unnatural intonation
```

## 📚 Resources & References

### Papers
- XTTS: [Massively Multilingual Zero-Shot Speech Synthesis](https://arxiv.org/abs/2309.08519)
- VITS: [Conditional Variational Autoencoder with Adversarial Learning](https://arxiv.org/abs/2106.06103)

### Tools
- Audacity: Audio editing and cleaning
- Praat: Phonetic analysis
- TensorBoard: Training monitoring
- WaveSurfer: Visual waveform analysis

### Communities
- Coqui TTS Discord
- r/speechtech
- Hungarian NLP communities

## 🎬 Production Checklist

Before deploying your model:

- [ ] Validation loss converged
- [ ] Generated samples sound natural
- [ ] No artifacts (clicks, pops, glitches)
- [ ] Consistent quality across different texts
- [ ] Speaker similarity verified
- [ ] Native Hungarian speaker approved
- [ ] Inference speed acceptable (<500ms)
- [ ] Model size reasonable for deployment
- [ ] Proper error handling in inference code
- [ ] Batch inference tested (for quiz app)

## 💡 Pro Tips

1. **Quality over quantity**: 10 minutes of perfect audio > 30 minutes of noisy audio
2. **Listen critically**: Your ears are the best metric
3. **Iterate quickly**: Don't wait for perfect data - start training, learn, improve
4. **Monitor training**: Check generated samples frequently
5. **A/B test everything**: Objective comparison beats subjective guessing
6. **Document everything**: Track what works and what doesn't
7. **Native speaker validation**: Essential for Hungarian accuracy
8. **Start conservative**: Easier to increase diversity than fix overfitting

## 🔧 Troubleshooting Quality Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Robotic voice | Overfitting | More data, lower LR, early stopping |
| Inconsistent quality | High temperature | Lower to 0.65-0.75 |
| Wrong pronunciation | Bad transcriptions | Fix metadata.csv |
| Artifacts/glitches | Noisy training data | Better preprocessing |
| Loss of voice character | Not enough data | More diverse samples |
| Slow/monotone | Lack of prosody variation | More expressive samples |

---

Remember: **Achieving commercial quality takes time and iteration.** Don't expect perfection on the first try. Each training run teaches you something new!
