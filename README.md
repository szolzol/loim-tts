# István Vágó Voice Cloning Project - XTTS-v2

## 🎯 Project Goal
Fine-tune Coqui XTTS-v2 model to clone István Vágó's voice (famous Hungarian quiz show host) for building a high-quality quiz application. Target quality: ElevenLabs/Fish Audio level.

## 🖥️ System Requirements
- **OS**: Windows 10/11
- **GPU**: NVIDIA RTX 4070 (12GB VRAM)
- **CUDA**: 11.8 or 12.1
- **Python**: 3.9-3.11 (3.10 recommended)
- **RAM**: 16GB+ recommended

## 📁 Project Structure
```
tts-2/
├── source_clips/          # Original audio samples (István Vágó)
├── processed_clips/       # Preprocessed audio (22050Hz, mono)
├── source_text/          # Transcriptions (Hungarian text)
├── dataset/              # Final training dataset
├── checkpoints/          # Model checkpoints
├── output/               # Generated audio samples
├── scripts/              # Utility scripts
└── configs/              # Configuration files
```

## 🎤 Audio Requirements for Maximum Quality

### Dataset Specifications
- **Sample Rate**: 22050 Hz (for training), 24000 Hz (output)
- **Format**: WAV, mono
- **Duration per clip**: 3-15 seconds (optimal: 5-10s)
- **Total audio**: 10-30 minutes minimum (more = better)
- **Quality**: Clean, no background noise/music
- **SNR**: >20dB recommended
- **Dynamic Range**: Good variation in pitch and energy

### Text Requirements
- Accurate transcriptions in Hungarian
- Proper punctuation and diacritics (á, é, í, ó, ö, ő, ú, ü, ű)
- Natural speech patterns

## 🚀 Setup Instructions

### 1. Environment Setup
See `scripts/setup_environment.ps1`

### 2. Data Preparation
See `scripts/prepare_dataset.py`

### 3. Training
See `scripts/train_xtts.py`

### 4. Inference
See `scripts/inference.py`

## 📊 Quality Benchmarks (Target)
- **Naturalness**: 4.5+/5.0 (MOS score)
- **Intelligibility**: 95%+ word accuracy
- **Speaker Similarity**: 4.5+/5.0
- **Prosody**: Natural Hungarian intonation
- **Latency**: <500ms for real-time applications

## 🔧 Key Parameters for Quality

### Training
- Batch size: 2-4 (GPU dependent)
- Gradient accumulation: 64-126 steps
- Learning rate: 5e-6 to 1e-5
- Epochs: 15-30 (with early stopping)
- Temperature: 0.65-0.85 (inference)

### Audio Processing
- Noise reduction: Applied
- Normalization: Peak normalization + RMS leveling
- Silence trimming: Aggressive (speech only)

## 📝 Version Control
Git checkpoints at:
1. Initial setup
2. Dataset preparation complete
3. Training start
4. Best checkpoint milestone
5. Final model

## 🎓 Resources
- [Coqui TTS Documentation](https://docs.coqui.ai/)
- [XTTS-v2 Paper](https://arxiv.org/abs/2309.08519)
- [Hungarian Language Guide for TTS](https://github.com/coqui-ai/TTS/discussions)

## 📄 License
This is a personal research project for educational purposes.
