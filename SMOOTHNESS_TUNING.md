# 🎵 Beszéd Simítási Útmutató (Speech Smoothness Tuning)

## 🎯 Probléma: Darabos/Szaggatott Beszéd (Choppy Speech)

### Mit jelent a "choppy" beszéd?
- 🔊 Szavak közötti hirtelen szünetek
- 📊 Egyenetlen ritmus és tempó
- 🎭 Robothangzású kiejtés
- ⚡ Túl gyors vagy egyenetlen sebességváltások
- 🎪 Természetellenes hanglejtés

### Miért van ez a zero-shot módszernél?
A zero-shot klónozás **rövid referencia hangfelvételekből** tanul, és a pre-trained modell általános prozódiáját használja. Ez néha:
- ❌ Túl agresszív mintavételezést okoz
- ❌ Inkonzisztens prozódiát generál  
- ❌ Túlzott variációt kényszerít ki

---

## 🛠️ Paraméter Optimalizálás Simább Beszédhez

### 1. **TEMPERATURE** (Hőmérséklet) 🌡️

**Mit csinál:** Kontrollálja a "kreativitást" és variabilitást

```python
# Értékek és hatásuk:
TEMPERATURE = 0.5   # Nagyon stabil, de monoton (túl merev)
TEMPERATURE = 0.65  # ✅ Simább, természetes (AJÁNLOTT choppy-nál)
TEMPERATURE = 0.75  # Egyensúly (alap)
TEMPERATURE = 0.85  # Expresszív, de kevésbé stabil
TEMPERATURE = 1.0   # Nagyon változatos, choppy lehet
```

**Choppy beszédnél:**
- ⬇️ **Csökkentsd 0.65-0.7-re** a simább flowhoz
- Ez csökkenti a hirtelen változásokat
- Stabilabb, következetesebb output

**Jelenleg:** 0.7 ✅ (optimalizálva)

---

### 2. **REPETITION_PENALTY** (Ismétlés Büntetés) 🔁

**Mit csinál:** Büntet ismétlődő mintákért

```python
# Értékek és hatásuk:
REPETITION_PENALTY = 2.0   # Túl kevés, ismétlések
REPETITION_PENALTY = 5.0   # ✅ Egyensúly (AJÁNLOTT)
REPETITION_PENALTY = 7.0   # Erős variáció
REPETITION_PENALTY = 10.0  # Túl erős, choppy output
```

**Choppy beszédnél:**
- ⬇️ **Csökkentsd 5.0-re** (volt 7.0)
- Túl magas érték → túlzott variáció → choppy
- Alacsonyabb → simább átmenetek

**Jelenleg:** 5.0 ✅ (optimalizálva)

---

### 3. **TOP_K & TOP_P** (Mintavételezés) 🎲

**Mit csinálnak:** Korlátozzák a szóválasztást stabilabb outputhoz

```python
# TOP_K - Hány legjobb szó közül választ
TOP_K = 50    # ✅ Stabil, következetes (AJÁNLOTT)
TOP_K = 100   # Több változatosság
TOP_K = None  # Korlátlan (instabil lehet)

# TOP_P - Nucleus sampling (valószínűségi küszöb)
TOP_P = 0.80  # Nagyon konzervatív
TOP_P = 0.85  # ✅ Jó egyensúly (AJÁNLOTT)
TOP_P = 0.95  # Több kreativitás, kevésbé stabil
```

**Choppy beszédnél:**
- ✅ **TOP_K = 50** → Limitálja a szóválasztást
- ✅ **TOP_P = 0.85** → Stabil, de nem túl merev
- Ezek együtt **simítják a beszédet**

**Jelenleg:** TOP_K=50, TOP_P=0.85 ✅ (hozzáadva)

---

### 4. **SPEED** (Sebesség) ⏱️

**Mit csinál:** Beszéd sebessége

```python
SPEED = 0.9   # 10% lassabb (nyugodtabb)
SPEED = 1.0   # ✅ Normál sebesség (AJÁNLOTT choppy-nál)
SPEED = 1.1   # 10% gyorsabb
SPEED = 1.2   # 20% gyorsabb (choppy lehet)
```

**Choppy beszédnél:**
- ✅ **SPEED = 1.0** → Természetes tempó
- Gyorsabb sebesség → roboțikusabb hangzás
- Lassabb sebesség → túl monoton lehet

**Jelenleg:** 1.0 ✅ (optimalizálva)

---

## 📊 Optimális Beállítások Típus Szerint

### Simább Beszéd (Jelenleg Aktív) ✅
```python
TEMPERATURE = 0.7           # Stabil, természetes
REPETITION_PENALTY = 5.0    # Kiegyensúlyozott
TOP_K = 50                  # Korlátozott szókészlet
TOP_P = 0.85                # Nucleus sampling
SPEED = 1.0                 # Normál sebesség
```

**Használat:** Choppy beszéd javítására  
**Eredmény:** Simább flow, természetesebb ritmus

---

### Expresszívebb Beszéd (Ha túl monoton)
```python
TEMPERATURE = 0.85          # Több variáció
REPETITION_PENALTY = 6.0    # Erősebb diverzitás
TOP_K = 75                  # Több választék
TOP_P = 0.9                 # Több kreativitás
SPEED = 1.05                # Kissé gyorsabb
```

**Használat:** Ha a simított verzió túl unalmas  
**Eredmény:** Több érzelem, de kicsit kevésbé stabil

---

### Kvíz Show Energia (Vágó István stílus)
```python
TEMPERATURE = 0.75          # Jó egyensúly
REPETITION_PENALTY = 5.5    # Közép
TOP_K = 60                  # Változatos, de stabil
TOP_P = 0.87                # Kicsit több szabadság
SPEED = 1.05                # Dinamikusabb
```

**Használat:** Kvíz műsor jelllegű tartalom  
**Eredmény:** Energikus, de nem choppy

---

## 🎤 Referencia Audió Optimalizálás

### Jelenlegi Beállítás:
```python
REFERENCE_AUDIO = [
    "vago_vagott_02.wav",  # Legenergetikusabb
    "vago_vagott_05.wav",  # Magas expresszió
    "vago_vagott_03.wav",  # Dinamikus
]
```

### Alternatívák Simább Beszédhez:

**Opció 1: Kevesebb referencia (stabilabb)**
```python
REFERENCE_AUDIO = [
    "vago_vagott_03.wav",  # Legsimább
]
```
- ✅ Egységesebb stílus
- ✅ Kevesebb konfliktus a minták között
- ⚠️ Kevesebb variáció

**Opció 2: Csak nyugodtabb klipek**
```python
REFERENCE_AUDIO = [
    "vago_vagott_01.wav",  # Nyugodtabb
    "vago_vagott_04.wav",  # Kiegyensúlyozott
]
```
- ✅ Simább alapstílus
- ⚠️ Lehet kevésbé expresszív

**Opció 3: Több referencia (jobb átlag)**
```python
REFERENCE_AUDIO = [
    "vago_vagott_01.wav",
    "vago_vagott_02.wav",
    "vago_vagott_03.wav",
    "vago_vagott_04.wav",
    "vago_vagott_05.wav",
]
```
- ✅ Több adatpont → simább átlag
- ⚠️ Lassabb generálás

---

## 🧪 Tesztelési Stratégia

### 1. Alapvonal Megállapítása
```powershell
# Generálj 3 mintát a jelenlegi beállításokkal
python scripts\zero_shot_inference.py
```

Hallgasd meg:
- [ ] Van-e choppy beszéd?
- [ ] Természetes-e a ritmus?
- [ ] Egyenletes-e a tempó?

### 2. Finomhangolás
Ha még mindig choppy:

**Lépés A: Csökkentsd a temperaturát**
```python
TEMPERATURE = 0.65  # volt 0.7
```

**Lépés B: Növeld a TOP_P-t**
```python
TOP_P = 0.9  # volt 0.85
```

**Lépés C: Csökkentsd a repetition penalty-t**
```python
REPETITION_PENALTY = 4.5  # volt 5.0
```

**Lépés D: Próbálj kevesebb referenciát**
```python
REFERENCE_AUDIO = [
    "vago_vagott_03.wav",  # Csak egy
]
```

### 3. A/B Tesztelés
Generálj ugyanazt a szöveget különböző beállításokkal:

```python
test_text = "Gratulálok a helyes válaszhoz! Fantasztikus teljesítmény volt."

# Konfiguráció A (simább)
TEMPERATURE = 0.65
generate_speech(...)

# Konfiguráció B (jelenlegi)
TEMPERATURE = 0.7
generate_speech(...)

# Konfiguráció C (expresszívebb)
TEMPERATURE = 0.75
generate_speech(...)
```

Hasonlítsd össze és válaszd a legjobbat!

---

## 🎯 Gyakorlati Tippek

### Quick Wins (Gyors Javítások)

**1. Lassítsd le kissé:**
```python
SPEED = 0.95  # 5% lassabb
```
- Több időt ad az átmeneteknek
- Természetesebb hangzás

**2. Használj hosszabb szöveget:**
```python
# ❌ Rossz - túl rövid
"Gratulálok!"

# ✅ Jó - teljes mondat
"Gratulálok a helyes válaszhoz! Fantasztikus teljesítmény volt."
```
- Több kontextus → simább prozódia
- Jobb átmenetek a szavak között

**3. Adj hozzá írásjeleket:**
```python
# ❌ Rossz
"Kérem a választ most döntsenek gyorsan"

# ✅ Jó
"Kérem a választ! Most döntsenek... gyorsan!"
```
- Írásjelek → természetes szünetek
- Segít a modellnek értelmezni

### Advanced Tricks

**1. Batch generálás stabil seedel:**
```python
import torch
torch.manual_seed(42)  # Reprodukálható output
```

**2. Pre-processing a szövegen:**
```python
# Normalizáld a szöveget
text = text.strip()
text = re.sub(r'\s+', ' ', text)  # Dupla space-ek eltávolítása
text = text + "."  # Biztosítsd a lezárást
```

**3. Post-processing az audión:**
```python
# Simítsd a waveform-ot
import scipy.signal
audio = scipy.signal.savgol_filter(audio, 51, 3)
```

---

## 📈 Amikor a Fine-Tuning Szükséges

Ha a paraméter-hangolás után is choppy marad:

### Jelek, hogy fine-tuning kell:
- ❌ Még TEMPERATURE=0.6-nál is instabil
- ❌ Szavak közötti szünetek túl nagyok
- ❌ Inkonzisztens hanglejtés mondatokon belül
- ❌ "Robothangú" output paraméterektől függetlenül

### Mit ad a fine-tuning:
- ✅ **Tanult prozódia** - megtanulja Vágó természetes ritmusát
- ✅ **Simább átmenetek** - folyamatos beszédmintákat tanul
- ✅ **Karakterisztikus stílus** - kvíz show energia beépül
- ✅ **Jobb timing** - szünetek és hangsúlyok helyesen

### Minimális követelmény:
- **10-15 perc** tiszta, energikus Vágó beszéd
- Különböző érzelmek (kérdések, gratulációk, feszültség)
- Professzionális minőség (TV felvételek)

---

## 🚀 Gyors Teszt Script

Készítettem egy gyors tesztelő scriptet különböző paraméterekkel:

```python
# test_parameters.py
from scripts.zero_shot_inference import *

configs = {
    "smooth": {
        "temperature": 0.65,
        "repetition_penalty": 4.5,
        "top_k": 50,
        "top_p": 0.9,
        "speed": 1.0,
    },
    "current": {
        "temperature": 0.7,
        "repetition_penalty": 5.0,
        "top_k": 50,
        "top_p": 0.85,
        "speed": 1.0,
    },
    "expressive": {
        "temperature": 0.75,
        "repetition_penalty": 5.5,
        "top_k": 60,
        "top_p": 0.87,
        "speed": 1.05,
    },
}

test_text = "Gratulálok a helyes válaszhoz! Ez egy remek teljesítmény volt."

for name, config in configs.items():
    print(f"\nTesting: {name}")
    # Generate with config...
```

---

## 💡 Összefoglalás

### Choppy beszéd javítása:

1. ⬇️ **Csökkentsd a TEMPERATURE-t** (0.7 → 0.65)
2. ⬇️ **Csökkentsd a REPETITION_PENALTY-t** (7.0 → 5.0)
3. ➕ **Add hozzá TOP_K=50 és TOP_P=0.85**
4. 🎵 **Használj SPEED=1.0** (ne gyorsíts)
5. 🎤 **Próbálj kevesebb/nyugodtabb referenciát**

### Jelenlegi optimalizált beállítások ✅:
```python
TEMPERATURE = 0.7
REPETITION_PENALTY = 5.0
TOP_K = 50
TOP_P = 0.85
SPEED = 1.0
```

**Teszteld újra:** `python scripts\zero_shot_inference.py`

Ha még mindig choppy → Tovább csökkentsd a temperaturát vagy kezdj fine-tuningot! 🎯
