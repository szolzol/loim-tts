# 🎙️ XTTS Batch TTS Generator - Dokumentáció

## ✅ Állapot: **MŰKÖDIK**

### Multi-reference Inference: ✅ SIKERES

- 3 referencia audio egyidejű használata
- Természetes hanglejtés kombinálás
- Szegmentált generálás támogatással

---

## 📋 Áttekintés

Ez a rendszer lehetővé teszi:

1. **JSON alapú input fájlokból** TTS generálást
2. **Egyszerű** és **szegmentált** (explicit szünetek) módot
3. **MP3 vagy WAV** kimenetet
4. **Multi-reference** hangklónozást

---

## 🚀 Használat

### 1. Input Fájl Sablon

Szerkeszd az `input_samples.json` fájlt:

```json
{
  "generation_config": {
    "model_checkpoint": "best_model_1901.pth",
    "output_format": "mp3",
    "output_directory": "generated_output",
    "sample_rate": 24000,
    "language": "hu",
    "multi_reference": true,
    "references": [
      "prepared_sources/vago_samples_first_source/neutral/neutral_002.wav",
      "prepared_sources/vago_samples_first_source/excitement/excitement_005.wav",
      "prepared_sources/vago_samples_first_source/question/question_003.wav"
    ],
    "parameters": {
      "temperature": 0.4,
      "top_p": 0.88,
      "top_k": 50,
      "repetition_penalty": 6.5,
      "length_penalty": 1.25
    }
  },
  "samples": [
    {
      "id": "sample_001",
      "text": "Ez a generálandó szöveg.",
      "description": "Minta leírás",
      "segmented": false
    }
  ]
}
```

### 2. Egyszerű Minta

```json
{
  "id": "hello",
  "text": "Üdvözöllek! Jó napot kívánok!",
  "description": "Üdvözlés",
  "segmented": false
}
```

### 3. Szegmentált Minta (Explicit Szünetek)

```json
{
  "id": "quiz_question",
  "description": "Kvíz kérdés válaszokkal",
  "segmented": true,
  "segments": [
    {
      "type": "question",
      "text": "Melyik városban található az Eiffel-torony?",
      "pause_after": 0.5
    },
    {
      "type": "transition",
      "text": "A válaszlehetőségek:",
      "pause_after": 0.5
    },
    {
      "type": "answer",
      "text": "Áá, London.",
      "pause_after": 0.7
    },
    {
      "type": "answer",
      "text": "Béé, Párizs.",
      "pause_after": 0.7
    },
    {
      "type": "answer",
      "text": "Céé, Berlin.",
      "pause_after": 0.7
    },
    {
      "type": "answer",
      "text": "Déé, Róma.",
      "pause_after": 0.0
    }
  ]
}
```

---

## 🎬 Generálás Futtatása

### Alapértelmezett (input_samples.json használata):

```bash
python batch_generate.py
```

### Egyedi input fájl:

```bash
python batch_generate.py custom_input.json
```

### WAV kimenet kényszerítése (MP3 helyett):

```bash
python batch_generate.py input_samples.json --format wav
```

---

## 📊 Példa Kimenet

```
================================================================================
🎙️  BATCH TTS GENERATOR
================================================================================

📄 Config file: input_samples.json
📁 Output directory: generated_output
🎵 Output format: MP3
🗣️  Language: hu
🎛️  Multi-reference: True

✅ Model and 3 references found
✅ Model loaded on CUDA
✅ Speaker latents computed from 3 references

================================================================================
GENERATING 5 SAMPLES
================================================================================

[1/5] sample_001
  📝 Nyitó üdvözlés
  📄 Text: Üdvözöllek a Legyen Ön is Milliomos kvízjátékban! Készülj fe...
  🔧 Mode: Simple
  ✅ Saved: sample_001.mp3 (116.8 KB, 5.9s)

[3/5] sample_003_segmented
  📝 Kvíz kérdés válaszokkal - szegmentált
  🔧 Mode: Segmented (6 parts)
  ✅ Saved: sample_003_segmented.mp3 (281.3 KB, 14.3s)

✅ BATCH GENERATION COMPLETE!
```

---

## 🛠️ Konfigurációs Paraméterek

### `generation_config` mezők:

| Paraméter          | Típus  | Leírás                            | Alapértelmezett       |
| ------------------ | ------ | --------------------------------- | --------------------- |
| `model_checkpoint` | string | Model fájl neve                   | `best_model_1901.pth` |
| `output_format`    | string | `mp3` vagy `wav`                  | `mp3`                 |
| `output_directory` | string | Kimenet mappa                     | `generated_output`    |
| `sample_rate`      | int    | Mintavételi ráta (Hz)             | `24000`               |
| `language`         | string | Nyelv kód                         | `hu`                  |
| `multi_reference`  | bool   | Multi-reference használata        | `true`                |
| `references`       | array  | Referencia audio fájlok útvonalai | `[...]`               |

### `parameters` mezők:

| Paraméter            | Típus | Leírás                    | Ajánlott érték |
| -------------------- | ----- | ------------------------- | -------------- |
| `temperature`        | float | Kreativitás vs stabilitás | `0.4`          |
| `top_p`              | float | Nucleus sampling          | `0.88`         |
| `top_k`              | int   | Top-K sampling            | `50`           |
| `repetition_penalty` | float | Ismétlés büntetése        | `6.5`          |
| `length_penalty`     | float | Hossz büntetése           | `1.25`         |

---

## 📦 Kimenet Struktúra

```
generated_output/
├── sample_001.mp3          (116.8 KB, 5.9s)
├── sample_002.mp3          (79.7 KB, 4.0s)
├── sample_003_segmented.mp3 (281.3 KB, 14.3s)
├── sample_004.mp3          (110.2 KB, 5.6s)
└── sample_005.mp3          (64.3 KB, 3.2s)
```

---

## 🔍 Szegmentált Generálás Előnyei

### Miért használj szegmentált módot?

1. **Explicit szünetek** - Pontos kontroll a szünetek hossza felett
2. **Természetes hanglejtés** - Minden szegmens külön generálódik
3. **Kvíz kérdések** - Ideális válaszlehetőségekkel ellátott kérdésekhez
4. **Tiszta kimenet** - Nem rohan át a válaszokon

### Szünet idők (másodpercben):

- **Kérdés után**: `0.5s` - Rövid szünet
- **Átmeneti kifejezés után**: `0.5s` - Rövid szünet
- **Válaszok között**: `0.7s` - Hosszabb szünet (tiszta elkülönítés)
- **Utolsó válasz után**: `0.0s` - Nincs szünet

---

## 🎯 Következő Lépések - API Fejlesztés

### Fázis 1: ✅ Input Fájl Sablon Rendszer (KÉSZ)

- JSON alapú konfigurációk
- Batch generálás
- Egyszerű + szegmentált módok

### Fázis 2: FastAPI Wrapper (KÖVETKEZŐ)

```python
POST /generate
{
  "text": "Szöveg...",
  "segmented": false
}
→ Response: MP3 fájl
```

### Fázis 3: Railway Deployment

- Dockerfile
- Model betöltés optimalizálás
- API endpoint dokumentáció
- Environment változók

---

## 📝 Példa Workflow

1. **Szerkeszd** `input_samples.json`-t
2. **Add hozzá** új sample-okat:
   ```json
   {
     "id": "my_new_sample",
     "text": "Ez az új mintám.",
     "segmented": false
   }
   ```
3. **Futtasd** a generálást:
   ```bash
   python batch_generate.py
   ```
4. **Ellenőrizd** a `generated_output/` mappát
5. **Hallgasd meg** az MP3 fájlokat

---

## ⚙️ Rendszer Követelmények

- Python 3.11+
- CUDA támogatással rendelkező GPU (RTX 5070 Ti ajánlott)
- PyTorch 2.10.0+cu128
- TTS 0.22.0
- 8GB+ VRAM

---

## 🐛 Hibaelhárítás

### "Model not found"

- Ellenőrizd a `MODEL_DIR` útvonalat a `batch_generate.py`-ban
- Bizonyosodj meg róla, hogy `best_model_1901.pth` létezik

### "Reference not found"

- Ellenőrizd a `references` útvonalakat az `input_samples.json`-ban
- Használj relatív útvonalakat a project root-hoz képest

### "CUDA out of memory"

- Csökkentsd a `batch_size`-t (ha van)
- Generálj kevesebb sample-t egyszerre
- Használj rövidebb szövegeket

---

## 📚 További Információk

- **XTTS Dokumentáció**: https://docs.coqui.ai/en/latest/models/xtts.html
- **TTS GitHub**: https://github.com/coqui-ai/TTS
- **Project Root**: `I:/CODE/tts-2`

---

**Verzió**: 1.0  
**Utolsó frissítés**: 2025. október 8.  
**Állapot**: ✅ Működőképes - API fejlesztés következik
