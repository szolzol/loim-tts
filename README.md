# XTTS v2 Magyar TTS - ElevenLabs Minőségű Hangszintézis

Ez a projekt a Coqui XTTS v2 modellt használja kiváló minőségű magyar hangszintézishez, amely ElevenLabs/Fish-Audio közeli minőséget ér el megfelelő beállításokkal.

## Főbb jellemzők

- **Magyar nyelv támogatás**: Natív `language="hu"` beállítás
- **Többreferenciás kondicionálás**: 3-6 darab 6-12 mp-es referencia klip használata
- **Optimalizált paraméterek**: `gpt_cond_len=8`, enhanced conditioning
- **24 kHz natív minőség**: XTTS v2 eredeti felbontása
- **MP3/WAV kimenet**: Rugalmas formátum támogatás
- **CLI interfész**: Egyszerű parancssori használat

## Telepítés

### 1. Automatikus telepítés (Windows)

```bash
# Futtassa a setup scriptet
setup.bat
```

### 2. Manuális telepítés

```bash
# Virtual environment létrehozása
python -m venv venv
venv\Scripts\activate

# PyTorch CUDA támogatással
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Egyéb függőségek
pip install -r requirements.txt
```

## Referencia audió előkészítés

### Ideális specifikációk:

- **Hossz**: 6-12 másodperc klippenként
- **Formátum**: WAV, mono, 24 kHz
- **Loudness**: -23 LUFS körüli
- **Minőség**: Nagyon tiszta, egységes beszédstílusú
- **Kerülendő**: Zene, zaj, más beszélők, visszhang

### Előfeldolgozás (ajánlott):

```python
# Audacity vagy programozottan:
# 1. Mono konverzió
# 2. 24 kHz újramintavételezés
# 3. Loudness normalizálás
# 4. Csendes részek levágása
# 5. VAD (Voice Activity Detection) alkalmazása
```

## Használat

### Alapvető szintézis

```bash
python xtts_hungarian_tts.py \
  --text "Jó reggelt, üdv mindenkinek!" \
  --refs voice1.wav \
  --refs voice2.wav \
  --refs voice3.wav \
  --out output.wav
```

### MP3 kimenettel

```bash
python xtts_hungarian_tts.py \
  --text "Szép napot kívánok!" \
  --refs reference_voice.wav \
  --out greeting.wav \
  --mp3
```

### Finomhangolt paraméterek

```bash
python xtts_hungarian_tts.py \
  --text "Köszönöm szépen a figyelmet." \
  --refs voice1.wav --refs voice2.wav \
  --out presentation.wav \
  --temperature 0.6 \
  --gpt-cond-len 8 \
  --gpt-cond-chunk-len 6 \
  --mp3
```

## Paraméterek magyarázata

### Kötelező paraméterek:

- `--text`: Szintetizálandó magyar szöveg
- `--refs`: Referencia hangfájl(ok) - többször megadható
- `--out`: Kimeneti fájl útvonala

### Opcionális paraméterek:

- `--mp3`: MP3 kimenet is létrehozása
- `--temperature` (0.7): Hangszín variabilitás (0.5-0.8 ajánlott)
- `--gpt-cond-len` (8): Kondicionálás hossza (6-8 magyarnál)
- `--gpt-cond-chunk-len` (6): Kondicionálás chunk mérete
- `--device`: 'cuda' vagy 'cpu' (auto-detect alapértelmezett)

## Minőség optimalizálás

### 1. Referencia klipek

```
✅ IDEÁLIS:
- 3-6 darab 6-12 mp-es klip
- Azonos mikrofon, azonos beszédstílus
- Egységes loudness (-23 LUFS)
- Tiszta, zaj nélküli felvétel

❌ KERÜLENDŐ:
- Túl hosszú (>15 mp) vagy rövid (<5 mp) klipek
- Vegyes minőségű felvételek
- Zene, zaj, visszhang
- Különböző beszélési stílusok
```

### 2. Szöveg formázás

```python
# Magyar írásjelek használata a megfelelő dallamért
text = "Jó reggelt! Hogy vagy? Remélem, jól érzed magad."

# Kerülje az angol írásjeleket vagy formázást
text = "Jo reggelt. Hogy vagy. Remelem jol erzed magad."  # ❌
```

### 3. Kondicionálás hangolása

```python
# Egységes hangszín: alacsonyabb temperature
temperature = 0.6

# Expresszívebb előadás: magasabb conditioning
gpt_cond_len = 8

# Stabil proszódia: length_penalty beállítása
length_penalty = 1.0
```

## Hibakezelés

### Gyakori problémák:

**"Nem magyar a kiejtés"**

- Ellenőrizze: `language="hu"` (script automatikusan beállítja)
- Magyar írásjeleket használjon (kérdőjel, vesszők)
- Referencia klipek magyarul legyenek

**"Monoton/idegen hangszín"**

- Használjon 2-4 klipet azonos stílusban
- Növelje `gpt_cond_len`-t 6→8-ra
- Ellenőrizze referencia klipek minőségét

**"Zajos kondicionálás"**

- Alkalmazzon VAD-et a referencia klipekre
- Normalize-olja a hangosságot
- Távolítsa el a háttérzajt

**"CUDA hiba"**

- Ellenőrizze PyTorch CUDA telepítést
- Használja `--device cpu` paramétert
- Frissítse a GPU driver-eket

## Példa workflow

```bash
# 1. Környezet aktiválása
venv\Scripts\activate

# 2. Referencia klipek előkészítése (6-12 mp, 24kHz, mono)
# voice_sample_1.wav, voice_sample_2.wav, voice_sample_3.wav

# 3. Szintézis futtatása
python xtts_hungarian_tts.py \
  --text "Üdvözlöm a prezentációmon! Ma a mesterséges intelligencia fejlődéséről beszélek." \
  --refs voice_sample_1.wav \
  --refs voice_sample_2.wav \
  --refs voice_sample_3.wav \
  --out presentation_intro.wav \
  --mp3 \
  --temperature 0.7 \
  --verbose

# 4. Eredmény: presentation_intro.wav és presentation_intro.mp3
```

## Finetune (opcionális nagy minőségugráshoz)

További minőségjavításhoz követheti az AllTalk XTTS Finetuning útmutatókat:

- 2-5 perc egységes, tiszta magyar beszéd
- Karakterhű hangszintézis
- Saját checkpoint használata

## Rendszerkövetelmények

### Minimális:

- Python 3.8+
- 8 GB RAM
- 4 GB GPU VRAM (CUDA) vagy CPU

### Ajánlott:

- Python 3.10+
- 16 GB RAM
- 8+ GB GPU VRAM (RTX 3070+)
- SSD tárhely

## Licenc

Ez a script a Coqui TTS könyvtárat használja, amely Mozilla Public License 2.0 alatt áll.

## Támogatás

Hibajelentés vagy kérdés esetén nyisson issue-t a GitHub repository-ban.

---

**Tipp**: A legjobb eredményért használjon 3-4 darab nagyon tiszta, 8-10 mp-es magyar referencia klipet, `gpt_cond_len=8` beállítással és `temperature=0.7` értékkel.
