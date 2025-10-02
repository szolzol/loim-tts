# Troubleshooting Guide - István Vágó XTTS-v2 Voice Cloning

Common issues and solutions for Windows/RTX 4070 environment.

---

## 🔧 Environment Setup Issues

### Issue: PowerShell script execution disabled

**Error**:
```
.\scripts\setup_environment.ps1 : File cannot be loaded because running scripts is disabled
```

**Solution**:
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script again
.\scripts\setup_environment.ps1
```

---

### Issue: Python not found

**Error**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:
1. Install Python 3.9-3.11 from python.org
2. Or use `py` instead:
   ```powershell
   py -3.10 -m venv xtts_env
   ```

---

### Issue: pip install fails with SSL error

**Error**:
```
Could not fetch URL https://pypi.org/simple/: There was a problem confirming the ssl certificate
```

**Solution**:
```powershell
# Upgrade pip with trusted host
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

---

### Issue: PyTorch CUDA version mismatch

**Error**:
```
RuntimeError: CUDA version mismatch
```

**Solution**:
```powershell
# Uninstall existing PyTorch
pip uninstall torch torchaudio torchvision

# Reinstall with correct CUDA version
pip install torch==2.1.0+cu118 torchaudio==2.1.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

---

## 🎤 Dataset Preparation Issues

### Issue: "No module named 'librosa'"

**Error**:
```
ModuleNotFoundError: No module named 'librosa'
```

**Solution**:
```powershell
# Activate environment first
.\xtts_env\Scripts\Activate.ps1

# Install missing package
pip install librosa soundfile noisereduce
```

---

### Issue: Audio files not found

**Error**:
```
❌ Error: No WAV files found in source_clips
```

**Solution**:
1. Verify files are in correct location:
   ```powershell
   dir source_clips\*.wav
   ```
2. Check if files have .wav extension (not .mp3, .flac, etc.)
3. Convert non-WAV files:
   ```powershell
   # Use ffmpeg or any audio converter
   ffmpeg -i input.mp3 output.wav
   ```

---

### Issue: "Audio too short" warnings

**Warning**:
```
⚠️ Too short: 1.5s < 2.0s
```

**Solution**:
- Acceptable: Some clips can be short
- Problem if many clips: Consider adjusting MIN_DURATION in `prepare_dataset.py`:
  ```python
  MIN_DURATION = 1.5  # Allow shorter clips
  ```
- Better solution: Get longer audio clips (3-10 seconds ideal)

---

### Issue: Poor SNR (noisy audio)

**Warning**:
```
⚠️ SNR: Could be better (12.3 dB)
```

**Solutions**:
1. **Re-record with better equipment**
2. **Apply manual noise reduction** (Audacity, Adobe Audition)
3. **Adjust noise reduction aggressiveness**:
   ```python
   # In prepare_dataset.py, line ~70
   reduced = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample, prop_decrease=0.9)  # Increase from 0.8
   ```

---

### Issue: Unicode/encoding errors in transcriptions

**Error**:
```
UnicodeDecodeError: 'charmap' codec can't decode byte...
```

**Solution**:
```python
# Ensure metadata.csv is saved with UTF-8 encoding
# In Notepad: Save As → Encoding: UTF-8
# In VS Code: Bottom right corner → Select encoding → UTF-8
```

---

## 🚀 Training Issues

### Issue: CUDA out of memory

**Error**:
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
```

**Solutions**:

1. **Reduce batch size**:
   ```python
   # In scripts/train_xtts.py, line 37
   BATCH_SIZE = 1  # Reduce from 2
   ```

2. **Increase gradient accumulation**:
   ```python
   GRAD_ACUMM_STEPS = 252  # Keep effective batch size = 252
   ```

3. **Clear cache before training**:
   ```powershell
   python -c "import torch; torch.cuda.empty_cache()"
   ```

4. **Close other GPU applications**:
   ```powershell
   # Check what's using GPU
   nvidia-smi
   
   # Close Chrome, games, other Python processes, etc.
   ```

---

### Issue: "Import TTS could not be resolved"

**Error**:
```
ModuleNotFoundError: No module named 'TTS'
```

**Solution**:
```powershell
# Activate environment
.\xtts_env\Scripts\Activate.ps1

# Reinstall TTS
pip install --force-reinstall TTS==0.22.0

# If that fails, try:
pip uninstall coqui-TTS -y
pip install TTS==0.22.0
```

---

### Issue: Training extremely slow

**Symptoms**: Each epoch takes 2+ hours

**Diagnose**:
```powershell
# Check if GPU is being used
nvidia-smi
# Should show python.exe using ~10+ GB GPU memory

# In Python:
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}'); print(f'Current device: {torch.cuda.current_device()}')"
```

**Solutions**:
1. **Verify CUDA is detected** (see above)
2. **Check CPU usage** (should be low, GPU should be high)
3. **Reduce batch size if GPU memory is full**
4. **Check for background processes stealing GPU**

---

### Issue: "Trainer has no attribute 'fit'"

**Error**:
```
AttributeError: 'Trainer' object has no attribute 'fit'
```

**Solution**:
```powershell
# Wrong TTS version installed
pip uninstall TTS -y
pip install TTS==0.22.0

# Also check trainer package
pip install trainer==0.0.24
```

---

### Issue: Loss not decreasing (stuck)

**Symptom**: Training loss stays constant at ~3.5

**Solutions**:
1. **Learning rate too low**: Increase to 1e-5
2. **Learning rate too high**: Decrease to 1e-6
3. **Bad data**: Check transcriptions are accurate
4. **Model not loading correctly**: Verify checkpoints downloaded

---

### Issue: Validation loss increasing (overfitting)

**Symptom**: Train loss decreases but eval loss increases

**Solutions**:
1. **Stop training early**: Use current best checkpoint
2. **More data**: Collect additional audio
3. **Reduce epochs**: Try 15-20 instead of 25
4. **Adjust regularization**: Increase weight decay

---

## 🎙️ Inference Issues

### Issue: Generated audio is robotic

**Symptom**: Speech sounds mechanical, not human

**Solutions**:
1. **Overfitting**: Retrain with more data or fewer epochs
2. **Temperature too low**: Increase from 0.75 to 0.85
3. **Reference audio quality**: Use better reference files

---

### Issue: Wrong language/accent

**Symptom**: Doesn't sound Hungarian

**Solutions**:
1. **Check language code**:
   ```python
   # In inference.py
   LANGUAGE = "hu"  # Must be "hu" for Hungarian
   ```
2. **Verify training data**: Ensure metadata.csv has Hungarian text
3. **Check model loaded correctly**: Verify checkpoint path

---

### Issue: Audio has artifacts (clicks, pops)

**Solutions**:
1. **Lower temperature**: Try 0.65-0.70
2. **Better reference audio**: Use cleaner clips
3. **Adjust sampling parameters**:
   ```python
   TOP_P = 0.80  # Lower from 0.85
   TOP_K = 30    # Lower from 50
   ```

---

### Issue: Inconsistent quality between generations

**Symptom**: Same text produces different quality

**Solutions**:
1. **Lower temperature**: More consistent at 0.65-0.70
2. **Use multiple reference clips**: 2-3 diverse samples
3. **Seed randomness**:
   ```python
   import torch
   torch.manual_seed(42)
   ```

---

### Issue: "No module named 'TTS.tts.configs'"

**Error**:
```
ModuleNotFoundError: No module named 'TTS.tts.configs'
```

**Solution**:
```powershell
# Wrong directory structure
# Ensure you're in the right directory
cd f:\CODE\tts-2

# Activate environment
.\xtts_env\Scripts\Activate.ps1

# Verify TTS installation
python -c "from TTS.tts.configs.xtts_config import XttsConfig; print('OK')"
```

---

## 🐛 Windows-Specific Issues

### Issue: Path too long error

**Error**:
```
OSError: [Errno 2] No such file or directory: 'f:\\CODE\\...very long path...'
```

**Solution**:
1. **Enable long paths in Windows**:
   - Run as Admin: `REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f`
2. **Use shorter project path**: Move to `C:\tts\`

---

### Issue: Antivirus blocking downloads

**Symptom**: Model files fail to download

**Solution**:
- Temporarily disable antivirus
- Or add exception for Python, pip, and project directory

---

### Issue: NumPy version conflicts

**Error**:
```
ImportError: numpy.core.multiarray failed to import
```

**Solution**:
```powershell
pip uninstall numpy -y
pip install numpy==1.24.3
```

---

## 📊 Diagnostic Commands

### Check GPU
```powershell
nvidia-smi
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### Check Installed Packages
```powershell
pip list | Select-String -Pattern "torch|TTS|librosa|numpy"
```

### Check Python Environment
```powershell
python --version
python -c "import sys; print(sys.executable)"
```

### Check CUDA
```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}'); print(f'cuDNN: {torch.backends.cudnn.version()}')"
```

### Check Project Structure
```powershell
dir -Recurse -Depth 2 | Select-Object FullName
```

---

## 🆘 Getting Help

If issues persist:

1. **Run system check**:
   ```powershell
   python scripts\check_system.py
   ```

2. **Check error logs**:
   - Training logs: `run\training\[run_name]\`
   - Python errors: Copy full traceback

3. **Verify versions**:
   ```powershell
   python --version
   pip show TTS torch torchaudio
   nvidia-smi
   ```

4. **Gather information**:
   - OS version: `winver`
   - GPU model: `nvidia-smi`
   - Error message: Full text
   - Steps to reproduce

5. **Community resources**:
   - Coqui TTS GitHub Issues
   - Coqui TTS Discord
   - Stack Overflow (tag: coqui-tts)

---

## 🎯 Quality Issues

### Not sounding like István Vágó

**Diagnosis checklist**:
- [ ] Enough training data? (15+ minutes recommended)
- [ ] Accurate transcriptions?
- [ ] Trained long enough? (15-25 epochs)
- [ ] Not overfitted? (eval loss not increasing)
- [ ] Using good reference audio for inference?
- [ ] Correct language setting? (LANGUAGE = "hu")

**Solutions**:
1. Collect more István Vágó audio
2. Verify transcription accuracy
3. Try different checkpoints (earlier/later in training)
4. Adjust inference temperature
5. Use 2-3 diverse reference clips

---

## 💡 Pro Tips

1. **Always activate environment first**: `.\xtts_env\Scripts\Activate.ps1`
2. **Monitor GPU memory**: Keep `nvidia-smi` open in another window
3. **Start small**: Test with 1 epoch first to catch errors early
4. **Save checkpoints**: Use `git_checkpoint.ps1` frequently
5. **Listen during training**: Check test audio after each epoch
6. **Document everything**: Keep notes on what works/doesn't

---

## 📞 Emergency Recovery

If everything breaks:

```powershell
# Nuclear option: Start fresh

# 1. Backup important files
Copy-Item dataset\metadata.csv dataset\metadata_backup.csv

# 2. Remove environment
Remove-Item -Recurse -Force xtts_env

# 3. Clear pip cache
pip cache purge

# 4. Reinstall from scratch
.\scripts\setup_environment.ps1

# 5. Verify
python scripts\check_system.py
```

---

**Remember**: Most issues have simple solutions. Check this guide first before panicking! 😊
