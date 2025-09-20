# XTTS v2 Magyar TTS - Telepítési Útmutató

## 🔧 Rendszerkövetelmények

- **Python**: 3.8-3.11 (ajánlott: 3.11)
- **GPU**: NVIDIA GPU CUDA 11.8 támogatással (ajánlott)
- **RAM**: Minimum 8GB, ajánlott 16GB
- **Storage**: ~5GB szabad hely (modellek + dependencies)

## 📦 Telepítési Módszerek

### Módszer 1: Automatikus Telepítés (Ajánlott)

```bash
# Windows
setup.bat

# Linux/macOS  
./setup.sh
```

### Módszer 2: Manuális Telepítés

#### 1. Virtual Environment Létrehozása
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 2. PyTorch CUDA Telepítés
```bash
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
```

#### 3. Fő Dependencies Telepítés
```bash
pip install -r requirements.txt
```

## ⚠️ Kritikus Verziók

### Kompatibilitási Problémák Elkerülése

A következő verziók **KÖTELEZŐK** a stabil működéshez:

- **torch==2.5.1** (NE torch >= 2.6.0!)
  - Elkerüli a `weights_only` parameter problémákat
  
- **transformers==4.35.0** (NE transformers >= 4.50.0!)
  - Biztosítja a `GPT2InferenceModel.generate()` metódus elérhetőségét
  
- **numpy==1.26.3** (NE numpy >= 2.0.0!)
  - Elkerüli a bináris kompatibilitási problémákat

### Ha Mégis Újabb Verziók Vannak Telepítve:

```bash
# Problémás verziók eltávolítása
pip uninstall torch torchaudio transformers numpy -y

# Megfelelő verziók telepítése
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.35.0 numpy==1.26.3
pip install TTS==0.22.0
```

## 🧪 Telepítés Ellenőrzése

### 1. Python Modulok Tesztelése
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
python -c "import TTS; from TTS.api import TTS; print('TTS import sikeres')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

### 2. XTTS Modell Tesztelése
```bash
python test_tts_system.py
```

### 3. Teljes Rendszer Tesztelése
```bash
python simple_xtts_hungarian.py --text "Teszt" --refs "processed_audio/optimized_clip_01.wav" --out test.wav --mp3
```

## 📁 Requirements Fájlok Magyarázata

- **requirements.txt**: Főbb dependencies pontos verziókkal
- **requirements-freeze.txt**: Teljes package lista (pip freeze kimenet)

## 🔍 Gyakori Telepítési Problémák

### PyTorch CUDA Probléma
```bash
# Hiba: "RuntimeError: No CUDA devices available"
# Megoldás: CUDA drivers frissítése vagy CPU használat
python simple_xtts_hungarian.py --device cpu [további paraméterek]
```

### TTS Compilation Probléma
```bash
# Hiba: "Microsoft Visual C++ 14.0 is required"
# Megoldás: Visual Studio Build Tools telepítése
# Letöltés: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Transformers Kompatibilitási Probléma
```bash
# Hiba: "'GPT2InferenceModel' object has no attribute 'generate'"
# Megoldás: Pontos transformers verzió
pip install transformers==4.35.0 --force-reinstall
```

### Memory Error
```bash
# Hiba: "RuntimeError: CUDA out of memory"
# Megoldás: CPU használat vagy kisebb batch size
export CUDA_VISIBLE_DEVICES=""  # CPU force
```

## ✅ Sikeres Telepítés Jelei

Ha minden működik, akkor:
- ✅ CUDA elérhető: `torch.cuda.is_available() == True`
- ✅ TTS modell betölthető hibamentesen
- ✅ Magyar szintézis működik naturális kiejtéssel
- ✅ MP3 export hibamentesen működik

## 🚀 Következő Lépések

1. **Audio előkészítés**: `python preprocess_audio.py --input your_voice.mp3`
2. **Optimalizálás**: `python advanced_preprocessing.py`
3. **Szintézis**: `python simple_xtts_hungarian.py --text "..." --refs "..." --out test.wav --mp3`

---

**💡 Tipp**: Ha bármilyen telepítési problémába ütközik, először próbálja a requirements.txt pontos verzióival, majd kérjen segítséget a hibaüzenet másolásával!