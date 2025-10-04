# Phase 3: Hangsúlyozás és Prozódia Javítási Terv

**Dátum:** 2025-10-04  
**Jelenlegi állapot:** Phase 2 best model (Mel CE: 2.971)  
**Cél:** Hangsúlyozás és természetesség további javítása

---

## 🎯 Probléma Azonosítása

### Jelenlegi Helyzet

**Erősségek:**
- ✅ Mel CE: 2.971 (kiváló simítás)
- ✅ Text CE: 0.0282 (kiváló kiejtés)
- ✅ Általános minőség: 9/10

**Gyengeség:**
- ⚠️ **Hangsúlyozás furcsaság** - A mondat hangsúlyok nem mindig természetesek
- ⚠️ **Prozódia** - Néha robotikus/monoton részek
- ⚠️ **Intonáció** - Kérdések/felkiáltások hanglejtése javítható

---

## 📊 Metrikák Elemzése

### Mel CE vs Prozódia

A **Mel CE (2.971)** azt méri:
- ✅ Spektrogram simítás
- ✅ Audio minőség
- ✅ Zajszint

De **NEM méri**:
- ❌ Hangsúlyozás helyességét
- ❌ Prozódiát (ritmus, hanglejtés)
- ❌ Érzelmi kifejezőkészséget
- ❌ Magyar nyelvi hangsúlyokat

### Text CE vs Kiejtés

A **Text CE (0.0282)** azt méri:
- ✅ Betűnkénti pontosság
- ✅ Szavak helyes kiejtése

De **NEM méri**:
- ❌ Szótaghangsúlyokat
- ❌ Mondathangsúlyokat
- ❌ Természetes beszéd ritmusát

---

## 🔍 Lehetséges Okok

### 1. **Túl Alacsony Learning Rate (1e-6)**

**Probléma:**
- Az ultra-alacsony LR elsősorban a Mel CE-t javítja (audio simítást)
- Nem elég merész a prozódia/hangsúly minták tanulásához
- Túl óvatos → túl kevés változás a hanglejtésben

**Bizonyíték:**
- Phase 2: 1e-6 LR → Mel CE: 5.046 → 2.971 (41% javulás)
- De a hangsúlyozás nem javult annyit

### 2. **GPT Attention rész nincs elég finomítva**

**Probléma:**
- Az XTTS modellben a **GPT rész** felelős a prozódiáért
- A Mel decoder rész felelős az audio minőségért
- Ha csak a Mel CE-t optimalizáljuk → GPT attention nem változik

**Megoldás:**
- GPT-specifikus loss weight növelése
- Attention loss hozzáadása

### 3. **Hiányzó Prozódia Annotációk**

**Probléma:**
- Az adathalmazban nincs explicit hangsúly jelölés
- A modell "találgatja" a hangsúlyokat a referencia audio alapján
- Magyar nyelv sajátos hangsúlyai (első szótag) nem tanult elég jól

**Megoldás:**
- Prozódia-gazdag minták kiválasztása
- Reference audio váltogatása

### 4. **Temperature Beállítás**

**Jelenlegi:**
```python
temperature = 0.7  # Általános beállítás
```

**Probléma:**
- Alacsonyabb temperature (0.5-0.6) → biztonságosabb, de monotonabb
- Magasabb temperature (0.75-0.85) → változatosabb hangsúlyok

---

## 🚀 Javítási Stratégiák

### Stratégia 1: **Learning Rate Dinamikus Beállítás** ⭐ AJÁNLOTT

**Módszer:**
```python
# Phase 3 konfiguráció
LEARNING_RATE = 3e-6  # 3x magasabb mint Phase 2
EPOCHS = 10
GPT_LR_MULTIPLIER = 1.5  # GPT rész 50%-kal gyorsabban tanul
```

**Előny:**
- Gyorsabb prozódia tanulás
- Meg őrzi a már elért Mel CE-t
- GPT attention jobban finomodik

**Hátrány:**
- Kicsi az esély Mel CE romlásra (~0.1-0.2 növekedés)

**Várható eredmény:**
- Mel CE: 2.971 → ~3.0-3.1 (kis romlás)
- Prozódia: Jelentős javulás
- Hangsúlyozás: Természetesebb

---

### Stratégia 2: **Prosody-Focused Dataset Filtering**

**Módszer:**
Válaszd ki a legjobb hangsúlyú mintákat:

```python
# dataset_combined/metadata.csv módosítás
# Csak a "question", "excitement", "tension" kategóriák
# Ezekben erősebb a prozódia

FILTERED_CATEGORIES = [
    "question",      # Kérdő hanglejtés
    "excitement",    # Lelkesedés
    "tension",       # Feszültség
    "confirmation",  # Megerősítés
]
```

**Előny:**
- Prozódia-gazdag minták
- Változatos intonációk
- Erősebb hangsúlyok

**Hátrány:**
- Kisebb dataset (csak ~120 minta)
- Lehet kevés a diversity

**Várható eredmény:**
- Kifejezőbb hangsúlyok
- Jobb kérdő hanglejtés

---

### Stratégia 3: **GPT Loss Weight Növelés** ⭐⭐ LEGJOBB

**Módszer:**
Módosítsd a loss funkciókat:

```python
# scripts/train_combined_phase3.py

# Jelenlegi súlyok
losses = {
    'mel_loss': mel_loss * 1.0,      # Mel CE
    'text_loss': text_loss * 1.0,    # Text CE
    'gpt_loss': gpt_loss * 1.0,      # GPT (prozódia)
}

# Új súlyok Phase 3-hoz
losses = {
    'mel_loss': mel_loss * 0.7,      # ↓ Csökkentjük (már elég jó)
    'text_loss': text_loss * 1.0,    # = Megtartjuk
    'gpt_loss': gpt_loss * 1.5,      # ↑ Növeljük (prozódia fókusz)
}
```

**Előny:**
- Direkt prozódia optimalizáció
- Hangsúlyok tanulása prioritás
- Mel CE nem romlik túl sokat

**Hátrány:**
- Kód módosítás szükséges
- Kis Mel CE növekedés várható

**Várható eredmény:**
- Mel CE: 2.971 → ~3.0-3.2
- Prozódia/Hangsúly: Jelentős javulás
- Text CE: Változatlan

---

### Stratégia 4: **Temperature Tuning Inference-nél**

**Módszer:**
Generálásnál magasabb temperature:

```python
# scripts/generate_quiz_phase3.py

outputs = model.inference(
    text=text,
    language="hu",
    gpt_cond_latent=gpt_cond_latent,
    speaker_embedding=speaker_embedding,
    temperature=0.85,  # ↑ Magasabb (volt: 0.7)
    length_penalty=1.2,
    repetition_penalty=2.0,
)
```

**Előny:**
- Nincs újra-training
- Azonnal tesztelhető
- Változatosabb hangsúlyok

**Hátrány:**
- Lehet kevésbé stabil
- Néha túl dramatikus

**Tesztelés:**
```python
# Próbáld ki különböző értékekkel
for temp in [0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
    generate_sample(temperature=temp)
```

---

### Stratégia 5: **Reference Audio Váltogatás**

**Módszer:**
Használj különböző referencia audioket:

```python
# Jelenlegi: Mindig ugyanaz
ref_audio = "processed_clips/vago_vagott_01.wav"

# Új: Váltogatás prozódia szerint
ref_audios = {
    "excited": "processed_clips/excitement_001.wav",
    "question": "processed_clips/question_003.wav", 
    "neutral": "processed_clips/neutral_002.wav",
    "tension": "processed_clips/tension_002.wav",
}

# Mondat típus szerint válassz
if "?" in text:
    ref_audio = ref_audios["question"]
elif "!" in text:
    ref_audio = ref_audios["excited"]
```

**Előny:**
- Nincs újra-training
- Kontextusfüggő hangsúly
- Változatos prozódia

**Hátrány:**
- Kézi kategorizálás kell
- Több referencia audio kell

---

## 📋 Ajánlott Phase 3 Terv

### Lépések Prioritás Szerint

#### 1️⃣ **ELSŐ: Temperature Tesztek** (30 perc)
```bash
# Nincs training, azonnal tesztelhető
python scripts/generate_quiz_phase2.py --temperature 0.85
python scripts/generate_quiz_phase2.py --temperature 0.80
python scripts/generate_quiz_phase2.py --temperature 0.75
```

**Ha jó → Kész, nincs szükség Phase 3 trainingre!**

---

#### 2️⃣ **MÁSODIK: Reference Audio Váltogatás** (1 óra)
```python
# Módosítsd generate_quiz_phase2.py-t
# Add hozzá a váltogatást
```

**Ha jó → Kész, használd ezt production-ben!**

---

#### 3️⃣ **HARMADIK: Phase 3 Training - GPT Focus** (4-6 óra)

**Konfiguráció:**
```python
# scripts/train_combined_phase3.py

LEARNING_RATE = 3e-6          # 3x magasabb
NUM_EPOCHS = 10               # Rövid training
GPT_LOSS_WEIGHT = 1.5         # GPT prioritás
MEL_LOSS_WEIGHT = 0.7         # Mel háttérbe
RESUME_FROM = "best_model_1901.pth"
```

**Parancs:**
```powershell
# GPU memória törlés
Get-Process python | Stop-Process -Force
Start-Sleep -Seconds 3

# Training indítás
python scripts/train_combined_phase3.py
```

**Várt eredmény:**
- ~500-800 lépés után
- Mel CE: 2.971 → ~3.0-3.2 (kis romlás)
- Hangsúlyozás: Jelentős javulás

---

## 📊 Sikerkritériumok Phase 3-hoz

### Objektív Metrikák

| Metrika | Jelenlegi | Phase 3 Cél | Elfogadható |
|---------|-----------|-------------|-------------|
| Mel CE  | 2.971     | < 3.2       | < 3.5       |
| Text CE | 0.0282    | < 0.030     | < 0.035     |
| Prozódia | ?       | Fejlődés    | Fejlődés    |

### Szubjektív Értékelés

**Tesztelendő:**
- [ ] Kérdések hanglejtése természetes?
- [ ] Felkiáltások hangsúlyosak?
- [ ] Magyar első szótag hangsúly helyes?
- [ ] Mondatvégi intonáció jó?
- [ ] Ritmus változatos, nem monoton?

**Tesztmondatok:**
```python
test_sentences = [
    # Kérdések
    "Mennyi ideje készül erre a kérdésre?",
    "Biztos benne, hogy ez a helyes válasz?",
    "Szeretne segítséget kérni?",
    
    # Felkiáltások  
    "Helyes válasz! Gratulálok!",
    "Óriási! Megvan a millió!",
    "Bravó! Fantasztikus!",
    
    # Feszültség
    "Ez az utolsó kérdés. Minden múlik ezen.",
    "Harminc másodperc van hátra.",
    
    # Semleges
    "A következő kérdés ezer forintért.",
    "Válasszon a négy lehetőség közül.",
]
```

---

## 🎯 Döntési Fa

```
Kezdés
  │
  ├─ Temperature tesztek (30 perc)
  │   ├─ Jó hangsúlyok? → ✅ KÉSZ
  │   └─ Még mindig fura? → Tovább
  │
  ├─ Reference audio váltogatás (1 óra)
  │   ├─ Javult? → ✅ Használd ezt
  │   └─ Még mindig nem elég? → Tovább
  │
  └─ Phase 3 Training - GPT Focus (4-6 óra)
      ├─ Mel CE < 3.5 ÉS jobb prozódia? → ✅ SIKER
      └─ Mel CE > 3.5 VAGY rosszabb? → ❌ Maradj Phase 2-nél
```

---

## 🔧 Phase 3 Script Elkészítése

### 1. Temperature Tesztelő Script

```python
# scripts/test_temperatures.py

import torch
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torchaudio

MODEL_DIR = Path("run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd")

test_sentences = [
    "Biztos benne, hogy ez a helyes válasz?",
    "Helyes válasz! Gratulálok!",
    "Ez az utolsó kérdés. Minden múlik ezen.",
]

temperatures = [0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

def generate_with_temperature(text, temp, output_file):
    config = XttsConfig()
    config.load_json(MODEL_DIR / "config.json")
    
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=str(MODEL_DIR),
        checkpoint_path=str(MODEL_DIR / "best_model_1901.pth"),
        vocab_path=str(MODEL_DIR / "vocab.json"),
        eval=True,
        use_deepspeed=False
    )
    model.cuda()
    
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=["processed_clips/vago_vagott_01.wav"]
    )
    
    outputs = model.inference(
        text=text,
        language="hu",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=temp,
    )
    
    torchaudio.save(
        output_file,
        outputs["wav"].squeeze().unsqueeze(0).cpu(),
        24000,
    )

# Generálás
for i, text in enumerate(test_sentences):
    for temp in temperatures:
        output = f"temp_test/sentence{i+1}_temp{temp}.wav"
        generate_with_temperature(text, temp, output)
        print(f"Generated: {output}")
```

### 2. Phase 3 Training Script

```python
# scripts/train_combined_phase3.py
# (Másold le train_combined_phase2.py-t és módosítsd)

# PHASE 3 KONFIGURÁCIÓ
LEARNING_RATE = 3e-6          # Magasabb mint Phase 2
NUM_EPOCHS = 10
BATCH_SIZE = 3

# Loss súlyok módosítása
def compute_loss_with_weights(mel_loss, text_loss, gpt_loss):
    weighted_loss = (
        mel_loss * 0.7 +      # Csökkentett súly
        text_loss * 1.0 +     # Változatlan
        gpt_loss * 1.5        # Növelt súly (prozódia)
    )
    return weighted_loss

# Training indítás best_model_1901.pth-ból
RESUME_CHECKPOINT = "best_model_1901.pth"
```

---

## 📝 Következő Lépések

### Azonnal Megtehető (Training nélkül)

1. ✅ **Temperature tesztek** - Próbálj 0.75-0.85 között
2. ✅ **Reference audio váltogatás** - Prozódia szerint
3. ✅ **Generálj több mintát** - Értékeld a hangsúlyokat

### Training Szükséges

4. ⏳ **Phase 3 Training** - GPT loss súlyozással
5. ⏳ **Prozódia-filtered dataset** - Csak expressív minták
6. ⏳ **Gradual LR increase** - Fokozatosan növeld 1e-6 → 3e-6

---

## 💡 Várható Eredmények

### Optimista Eset (90% esély)

- Temperature 0.80-0.85 javítja a hangsúlyokat
- Referencia audio váltogatás is segít
- **Nincs Phase 3 training szükséges!**

### Pesszimista Eset (10% esély)

- Temperature nem elég
- Phase 3 training szükséges
- Mel CE: 2.971 → ~3.1 (kis romlás)
- De prozódia javul

---

## 🎯 Ajánlás

### 🥇 LEGJOBB MEGKÖZELÍTÉS

1. **Temperature tesztek** (30 perc, nincs training)
   - Próbáld ki 0.80 és 0.85-öt
   - Ha jó → kész vagy!

2. **Ha nem elég:**
   - Reference audio váltogatás
   - Kérdéseknél: question_003.wav
   - Lelkes részeknél: excitement_001.wav

3. **Ha még mindig nem elég:**
   - Phase 3 training GPT fókusszal
   - Várható: kis Mel CE romlás, nagy prozódia javulás

---

**Következtetés:** A legtöbb esetben az **inference-time paraméter tuning** (temperature, reference audio) megoldja a problémát training nélkül!

---

*Készítette: GitHub Copilot*  
*Dátum: 2025-10-04*
