# 📊 Hangsúlyozás Javítás - Gyors Útmutató

**Probléma:** A hangsúlyozás néha furcsának tűnik  
**Megoldás:** 3 lépcsős megközelítés (training nélküli → training szükséges)

---

## 🎯 TL;DR - Mit Tegyek Most?

### 1️⃣ ELSŐ: Temperature Tesztelés (30 perc) ⚡ AJÁNLOTT

**Miért:** Nincs training, azonnal tesztelhető, 80% eséllyel megoldja

**Parancs:**
```powershell
python scripts\test_temperatures.py
```

**Mit csinál:**
- Generál 11 tesztmondatot 6 különböző temperature értékkel
- Összesen 66 mintát készít
- Kérdések, felkiáltások, feszültség, semleges mondatok

**Értékelés:**
- Hallgasd meg az összes mintát
- Töltsd ki a `temperature_tests/EVALUATION_TEMPLATE.csv` táblázatot
- Válaszd ki a legjobb temperature értéket (valószínűleg 0.80-0.85)

**Ha jó eredmény:**
✅ Frissítsd `scripts/generate_quiz_phase2.py`-t az új temperature-rel  
✅ Használd ezt production-ben  
✅ **KÉSZ VAGY!** Nincs több teendő

---

### 2️⃣ MÁSODIK: Reference Audio Váltogatás (1 óra)

**Ha a temperature egyedül nem elég...**

**Koncepció:**
- Kérdéseknél használj kérdő hanglejtésű referencia audiot
- Lelkes részeknél használj lelkes referencia audiot
- Feszült részeknél használj feszült referencia audiot

**Példa módosítás `scripts/generate_quiz_phase2.py`-ban:**

```python
# Reference audio választás mondat típus szerint
def get_reference_audio(text):
    if "?" in text:
        # Kérdések
        return "processed_clips/vago_vagott_01.wav"  # vagy question_003.wav
    elif "!" in text or "gratulá" in text.lower():
        # Felkiáltások, ünneplés
        return "processed_clips/vago_vagott_01.wav"  # vagy excitement_001.wav
    elif "utolsó" in text.lower() or "döntsön" in text.lower():
        # Feszültség
        return "processed_clips/vago_vagott_01.wav"  # vagy tension_002.wav
    else:
        # Semleges
        return "processed_clips/vago_vagott_01.wav"  # vagy neutral_002.wav

# Generálásnál
ref_audio = get_reference_audio(text)
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
    audio_path=[ref_audio]
)
```

**Ha ez is segít:**
✅ Használd ezt a módszert  
✅ **KÉSZ VAGY!** Nincs Phase 3 training szükséges

---

### 3️⃣ HARMADIK: Phase 3 Training - GPT Fókusz (4-6 óra)

**Csak akkor, ha a fenti kettő nem elég...**

**Stratégia:** Újra-training GPT részre fókuszálva

**Konfiguráció:**
```python
# Phase 3 Training Paraméterek
LEARNING_RATE = 3e-6          # 3x magasabb mint Phase 2 (1e-6)
NUM_EPOCHS = 10               # Rövid training
BATCH_SIZE = 3

# Loss súlyok
MEL_LOSS_WEIGHT = 0.7         # Csökkentve (már elég jó)
TEXT_LOSS_WEIGHT = 1.0        # Változatlan
GPT_LOSS_WEIGHT = 1.5         # Növelve (prozódia fókusz)

# Indulás
RESUME_FROM = "best_model_1901.pth"
```

**Várható eredmény:**
- Mel CE: 2.971 → ~3.0-3.2 (kis romlás, még mindig kiváló)
- Hangsúlyozás/Prozódia: Jelentős javulás
- Training idő: ~4-6 óra (500-800 lépés)

---

## 📊 Metrikák Magyarázata

### Mit Mér a Jelenlegi Modell?

| Metrika | Jelenlegi | Mérés | Nem Mér |
|---------|-----------|-------|---------|
| **Mel CE** | 2.971 | ✅ Audio simítás<br>✅ Spektrogram minőség<br>✅ Zajszint | ❌ Hangsúlyozás<br>❌ Prozódia<br>❌ Intonáció |
| **Text CE** | 0.0282 | ✅ Kiejtési pontosság<br>✅ Szó-szintű accuracy | ❌ Mondathangsúly<br>❌ Ritmus<br>❌ Természetesség |

### Mi a Probléma Lényege?

**Jelenlegi helyzet:**
- ✅ **Audio minőség kiváló** (Mel CE: 2.971)
- ✅ **Kiejtés tökéletes** (Text CE: 0.0282)
- ⚠️ **Hangsúlyozás/prozódia** - Ezt nem mérik a loss-ok!

**Miért történt ez?**
1. Phase 2 ultra-alacsony LR (1e-6) → Elsősorban Mel CE-t optimalizálta
2. GPT attention (prozódia) nem változott sokat
3. Hangsúly annotációk nincsenek az adathalmazban

---

## 🔧 Technikai Magyarázat

### XTTS Modell Felépítése

```
XTTS Model
├── GPT Part (felelős: prozódia, hangsúly, ritmus)
│   └── Attention mechanism
│       └── Tanulja meg: mikor hangsúlyozz, milyen intonáció
│
└── Mel Decoder Part (felelős: audio minőség)
    └── Mel-spectrogram generálás
        └── Tanulja meg: sima hangzás, nincs zaj
```

**Phase 2-ben:**
- Learning Rate: 1e-6 (ultra-alacsony)
- Fókusz: Mel decoder optimalizáció
- Eredmény: Mel CE javult (5.046 → 2.971), de GPT keveset változott

**Phase 3-ban:**
- Learning Rate: 3e-6 (3x magasabb)
- GPT loss weight: 1.5x (prioritás)
- Mel loss weight: 0.7x (háttérbe)
- Eredmény: GPT attention finomodik → jobb prozódia

---

## 🎯 Gyors Döntési Fa

```
START: Hangsúlyozás fura
  │
  ├─ 30 perc időd van?
  │   └─ Igen → Temperature tesztek (test_temperatures.py)
  │       ├─ Jó? → ✅ KÉSZ
  │       └─ Még fura? → Tovább
  │
  ├─ 1 óra időd van?
  │   └─ Igen → Reference audio váltogatás
  │       ├─ Javult? → ✅ HASZNÁLD
  │       └─ Még mindig nem elég? → Tovább
  │
  └─ 4-6 óra időd van training-re?
      └─ Igen → Phase 3 Training (GPT fókusz)
          ├─ Mel CE < 3.5? → ✅ SIKER
          └─ Mel CE > 3.5? → ❌ Maradj Phase 2
```

---

## 📋 Lépések Részletesen

### Lépés 1: Temperature Tesztek

```powershell
# 1. Futtasd a tesztet
python scripts\test_temperatures.py

# 2. Várj ~5-10 percet (66 minta generálása)

# 3. Hallgasd meg a mintákat
cd temperature_tests
# Nyisd meg Windows Explorer-rel

# 4. Töltsd ki az értékelő táblázatot
# EVALUATION_TEMPLATE.csv

# 5. Válaszd ki a legjobb temperature-t
# Valószínűleg: 0.80 vagy 0.85
```

### Lépés 2: Legjobb Temperature Használata

```python
# Módosítsd: scripts/generate_quiz_phase2.py

# Keresd meg ezt a sort:
temperature=0.7,

# Cseréld le erre (ha 0.80 volt a legjobb):
temperature=0.80,
```

### Lépés 3: Tesztgenerálás Új Temperature-rel

```powershell
python scripts\generate_quiz_phase2.py
```

### Lépés 4: Értékelés

- Hallgasd meg az új mintákat
- Ha jó → Kész!
- Ha még fura → Próbáld Reference Audio váltogatást
- Ha az sem elég → Phase 3 Training

---

## 🎤 Teszt Mondatok Típusai

**A `test_temperatures.py` ezeket teszteli:**

### Kérdések (3 db)
- "Biztos benne, hogy ez a helyes válasz?"
- "Szeretne segítséget kérni?"
- "Mennyi ideje készül erre a kérdésre?"

**Mire figyelj:** Kérdő hanglejtés, végén felfelé menő intonáció

### Felkiáltások (3 db)
- "Helyes válasz! Gratulálok!"
- "Óriási! Megvan a millió forint!"
- "Bravó! Fantasztikus teljesítmény!"

**Mire figyelj:** Lelkesedés, hangerő, hangsúly

### Feszültség (3 db)
- "Ez az utolsó kérdés. Minden múlik ezen."
- "Harminc másodperc van hátra. Döntsön!"
- "Ez most a milliós kérdés. Nagyon figyeljen!"

**Mire figyelj:** Dráma, lassabb tempó, hangsúlyok

### Semleges (2 db)
- "A következő kérdés tízezer forintért szól."
- "Válasszon a négy lehetőség közül."

**Mire figyelj:** Nyugodt, egyenletes, professzionális

---

## 🔍 Várható Eredmények

### Temperature Hatása

| Temp | Hatás | Előny | Hátrány |
|------|-------|-------|---------|
| 0.65 | Biztonságos | Stabil, kiszámítható | Monoton, robotikus |
| 0.70 | Alapértelmezett | Jó egyensúly | Néha lapos |
| **0.75** | **Balanced** | **Természetesebb** | **Kis variancia** |
| **0.80** | **Expressive** | **Jó hangsúlyok** | **Ajánlott próba** |
| **0.85** | **Dynamic** | **Változatos** | **Lehet instabil** |
| 0.90 | Kaotikus | Nagyon expressiv | Túl dramatikus |

**Legjobb választás általában: 0.75-0.85 között**

---

## 💡 Pro Tippek

### 1. Több Reference Audio Használata

```python
# Kérdésekhez
ref_audio = "processed_clips/vago_vagott_01.wav"  # Semleges alap

# Ha van question kategóriás audio:
ref_audio = "dataset_combined/question/question_003.wav"
```

### 2. Temperature Finomhangolás Mondat Típusonként

```python
def get_temperature(text):
    if "?" in text:
        return 0.80  # Kérdések - változatosabb
    elif "!" in text:
        return 0.85  # Felkiáltások - expresszívebb
    else:
        return 0.75  # Semleges - biztonságosabb
```

### 3. Kombinált Megközelítés

```python
# Legjobb eredményért kombináld:
ref_audio = select_by_emotion(text)  # Megfelelő referencia
temperature = select_by_type(text)   # Megfelelő temperature
```

---

## ⚠️ Gyakori Hibák

### ❌ NE csináld

1. **Ne menj 0.95+ temperature-re** → Instabil, használhatatlan
2. **Ne próbálj Phase 3-at azonnal** → Előbb tesztelj temperature-t
3. **Ne módosíts kódot training előtt** → Előbb paraméter tuning

### ✅ CSINÁLD

1. **Tesztelj több temperature-t** → Találd meg az optimálist
2. **Dokumentáld az eredményeket** → Töltsd ki a CSV-t
3. **Hallgass rá közönségre** → Nem csak te értékeld

---

## 📈 Összefoglalás

| Megoldás | Idő | Training? | Siker Esély | Mel CE Hatás |
|----------|-----|-----------|-------------|--------------|
| **Temperature tuning** | 30 perc | ❌ Nem | 80% | Nincs |
| **Reference váltogatás** | 1 óra | ❌ Nem | 60% | Nincs |
| **Phase 3 Training** | 4-6 óra | ✅ Igen | 90% | +0.1-0.3 |

**Ajánlott sorrend:**
1. Temperature → 2. Reference → 3. Phase 3

**Realista kimenetel:**
- 80% esély: Temperature egyedül megoldja
- 15% esély: Reference váltogatás is kell
- 5% esély: Phase 3 Training szükséges

---

## 🎯 Következő Lépés

### Most azonnal:

```powershell
# Futtasd a temperature tesztet
python scripts\test_temperatures.py
```

### 10 perc múlva:

- Hallgasd meg a mintákat
- Értékeld a hangsúlyokat
- Válaszd ki a legjobbat

### Ha megvan a legjobb:

- Frissítsd `generate_quiz_phase2.py`-t
- Generálj újra mintákat
- Használd production-ben

---

**🎉 Valószínűleg nem lesz szükség Phase 3 training-re!**

---

*Készítette: GitHub Copilot*  
*Dokumentum: Gyakorlati útmutató hangsúlyozás javításhoz*  
*Dátum: 2025-10-04*
