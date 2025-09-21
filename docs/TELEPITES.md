# XTTS v2 Magyar TTS - Telepítési Útmutató

## 🔧 Rendszerkövetelmények

- **Python**: 3.8-3.11 (ajánlott: 3.11)
- **GPU**: NVIDIA GPU CUDA 11.8 támogatással (opcionális - CPU is működik!)
- **RAM**: Minimum 8GB, ajánlott 16GB
- **Storage**: ~5GB szabad hely (modellek + dependencies)

**⚠️ Fontos**: A rendszer CPU-n is teljesen működik! GPU nem kötelező.

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

### 1. Virtual Environment Aktiválás (KRITIKUS!)

```bash
# Windows
cd f:/CODE/tts
source venv/Scripts/activate

# Linux/Mac
cd /path/to/loim-tts
source venv/bin/activate

# Ellenőrzés - a következőt kell látnod:
# Virtual env: F:\CODE\tts\venv (vagy hasonló path)
python -c "import sys; print('Virtual env:', sys.prefix)"
```

### 2. Python Modulok Tesztelése

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
# FONTOS: Virtual environment aktiválás után!
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Teszt magyar szöveggel
python premium_xtts_hungarian.py \
  --text "Jöjjön a következő kérdés egymillió forintért!" \
  --refs "processed_audio/premium_clip_01.wav,processed_audio/premium_clip_02.wav,processed_audio/premium_clip_03.wav" \
  --out "teszt_egymillio.wav" \
  --mp3
```

**Sikeres kimenet jelei:**
```
✅ Premium XTTS modell betöltve (CPU)
> Text splitted to sentences.
> Processing time: 7.671572208404541
> Real-time factor: 1.7071508880522377
✅ Prémium szintézis kész: test_results\teszt_egymillio.wav
✅ MP3 export kész: test_results\teszt_egymillio.mp3
```

## 📁 Requirements Fájlok Magyarázata

- **requirements.txt**: Főbb dependencies pontos verziókkal
- **requirements-freeze.txt**: Teljes package lista (pip freeze kimenet)

## 🔍 Gyakori Telepítési Problémák

### Virtual Environment Nem Aktiválva

```bash
# Hiba: "No module named 'TTS'"
# OK: Virtual env: C:\Python311 (rossz!)
# Megoldás: Virtual environment aktiválás
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac
# OK: Virtual env: F:\CODE\tts\venv (jó!)
```

### PyTorch CUDA Probléma

```bash
# Hiba: "CUDA is not availabe on this machine"
# Megoldás: Automatikus CPU fallback (már beépített)
# A rendszer automatikusan "Premium XTTS modell betöltve (CPU)" módba vált
# CPU működés: ~1.7x real-time faktor, teljesen stabil
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

- ✅ Virtual environment aktiválva: `Virtual env: F:\CODE\tts\venv`
- ✅ TTS modell betölthető: `Premium XTTS modell betöltve (CPU)`
- ✅ Magyar szintézis működik: Processing time ~7-8 másodperc
- ✅ MP3 export hibamentesen: WAV és MP3 fájlok generálódnak
- ✅ Magyar karakterek kezelése: ő, ü, á, stb. helyesen működik

### Típikus Működési Példa

```bash
$ python premium_xtts_hungarian.py --text "Teszt magyar szöveg" --refs "..." --out test.wav --mp3
> tts_models/multilingual/multi-dataset/xtts_v2 is already downloaded.
✅ Premium XTTS modell betöltve (CPU)
> Text splitted to sentences.
> Processing time: 7.67
> Real-time factor: 1.70
✅ Prémium szintézis kész: test_results\test.wav
✅ MP3 export kész: test_results\test.mp3
```

## 🚀 Következő Lépések

1. **Virtual Environment**: `source venv/Scripts/activate` (MINDEN alkalommal!)
2. **Audio előkészítés**: `python preprocess_audio.py --input your_voice.mp3`
3. **Optimalizálás**: `python advanced_preprocessing.py`
4. **Szintézis**: 
   ```bash
   python premium_xtts_hungarian.py \
     --text "Jöjjön a következő kérdés egymillió forintért!" \
     --refs "processed_audio/premium_clip_01.wav,processed_audio/premium_clip_02.wav" \
     --out output.wav --mp3
   ```

---

**💡 Legfontosabb Tipp**: A virtual environment aktiválása a LEGGYAKORIBB probléma forrása! Mindig ellenőrizze, hogy a `Virtual env:` path a project mappájára mutat-e!
