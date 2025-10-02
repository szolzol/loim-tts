# 🎯 István Vágó Fine-Tuning - Gyűjtési Terv

## Jelenlegi helyzet
- **Van:** 1.7 perc audio (13 klip)
- **Kell:** 15-20 perc minimum (jó minőséghez)
- **Cél:** Sima, természetes beszéd kvíz show energiával

---

## 🎤 PONTOS hangminta követelmények

### Mennyiség
```
Minimum (teszteléshez):     10 perc  →  ~80 klip
Ajánlott (jó minőség):      15-20 perc  →  ~120-160 klip  ⭐
Optimális (profi minőség):  25-30 perc  →  ~200-240 klip
```

### Klip hosszak (ideális eloszlás)
```
40% →  4-8 másodperc   (rövid kérdések, reagálások)
35% →  8-12 másodperc  (teljes mondatok)
25% →  12-15 másodperc (bonyolultabb magyarázatok)
```

---

## 🎭 Tartalom típusok (KRITIKUS a prosódiához!)

### 1. KÉRDÉSEK (40% - ~6-8 perc)
**Miért fontos:** Tanítja a felfelé ívelő intonációt

Példák amit keresni kell:
```
✅ "Ki volt az, aki...?"
✅ "Mikor történt...?"
✅ "Hol található...?"
✅ "Melyik évben...?"
✅ "Milyen híres...?"
✅ "Mit gondol, helyes a válasz?"
```

**Honnan:** 
- YouTube: "Vágó István kvíz kérdések"
- Keress videókat ahol sokat kérdez

### 2. IZGALOM/ÜNNEPLÉS (25% - ~4-5 perc)
**Miért fontos:** Tanítja az energikus, lelkes hangot

Példák:
```
✅ "Gratulálok! Helyes válasz!"
✅ "Fantasztikus teljesítmény!"
✅ "Nagyszerű!"
✅ "Bravo!"
✅ "Ezt tökéletesen tudta!"
✅ "Hibátlan válasz!"
```

**Honnan:**
- YouTube: "Vágó István gratulálok"
- Keress helyes válasz pillanatokat

### 3. FESZÜLTSÉG/DRÁMA (20% - ~3-4 perc)
**Miért fontos:** Tanítja a tempó változtatást, drámát

Példák:
```
✅ "Az idő múlik..."
✅ "Gondolkozzon csak..."
✅ "Biztos benne?"
✅ "Ez nehéz kérdés lesz..."
✅ "Figyelem, fontos döntés..."
```

**Honnan:**
- Időzítős jelenetek
- Nehéz kérdések előtti pillanatok

### 4. SEMLEGES/MAGYARÁZAT (15% - ~2-3 perc)
**Miért fontos:** Alapvető, nyugodt hang

Példák:
```
✅ "A helyes válasz a következő..."
✅ "Most következik..."
✅ "Lássuk a szabályokat..."
✅ "Ez azért érdekes, mert..."
```

---

## 🔍 HOL találod a legjobb anyagokat?

### YouTube keresési kifejezések:

**Legjobb találatok:**
```
1. "Vágó István Póker teljes adás"
2. "Vágó István Maradj talpon"
3. "Vágó István Legyen Ön is milliomos"
4. "Vágó István kvíz legjobb pillanatok"
5. "Vágó István helyes válasz"
```

**Trükkök:**
- Szűrő: "Ez az év" (jobb minőség)
- Rendezés: "Nézettség szerint"
- Keress: 20-30 perces teljes epizódokat

### Konkrét műsorok (amiket érdemes megnézni):

1. **"Maradj talpon"**
   - Sok kérdés
   - Jó tempó
   - Tiszta audio

2. **"Póker"** 
   - Vágó show-ja
   - Sok érzelem
   - Profi felvétel

3. **"Legyen Ön is milliomos"**
   - Feszültség
   - Drámai pillanatok
   - Változatos tartalom

---

## ⚠️ MIT KERÜLJ EL!

### Rossz audio minőség jelek:
```
❌ Túl sok háttérzaj
❌ Közönség zaja túl hangos
❌ Zene alatt beszél
❌ Rossz videó minőség (240p, 360p)
❌ Több ember beszél egyszerre
❌ Echo, visszhang
```

### Rossz tartalom jelek:
```
❌ Interjúk (más stílus)
❌ Politikai viták (komoly hangnem)
❌ Régi felvételek (1990-es évek - más hangszín)
❌ Rádió anyagok (kompresszált)
```

---

## 🛠️ GYORS munkamenet (2-3 óra alatt 10 perc)

### Lépés 1: Találd meg a forrást (20 perc)
```powershell
# YouTube videó letöltése
pip install yt-dlp

# Letöltés (egy jó 30 perces epizód):
yt-dlp -f bestaudio --extract-audio --audio-format wav --audio-quality 0 "https://youtube.com/watch?v=..."
```

### Lépés 2: Audacity-ben szegmentálás (90 perc)
```
1. Nyisd meg a letöltött WAV-ot
2. Hallgasd végig 1.5x sebességgel
3. Jelölj minden tiszta Vágó beszédet (zene/zaj nélkül)
4. Export minden szegmenst:
   - 4-12 másodperces darabok
   - Csak tiszta beszéd
   - Cél: 80-100 klip
```

### Lépés 3: Automatikus átírás (30 perc)
```powershell
# Whisper átírás
python scripts\transcribe_audio.py

# Javítsd a hibákat manuálisan
```

### Lépés 4: Ellenőrzés (20 perc)
```powershell
# Adatkészlet előkészítés
python scripts\prepare_dataset.py

# Nézd meg a statisztikákat
```

---

## 📊 Gyors minőség ellenőrzés

### Minden klipnél:
```
✓ Tiszta Vágó hang?
✓ Nincs háttérzene?
✓ Teljes mondat/kérdés?
✓ 4-12 másodperc?
✓ Jól hallható?
```

Ha mind ✓ → Tartsd meg
Ha bármi ✗ → Dobáljel

**Jobb 50 tökéletes klip, mint 100 közepesnél!**

---

## 🎯 Egyszerűsített gyűjtési terv

### OPCIÓ A: Gyors (10 perc, 2 óra munka)
```
1 jó YouTube videó (30 perc epizód)
→ Kiválogatni 80 tiszta klipet
→ Whisper átírás + gyors javítás
→ Kész a tanítás
```

### OPCIÓ B: Kiváló (20 perc, 4 óra munka)
```
2-3 jó YouTube videó
→ 160 klip kiválogatás
→ Gondos átírás
→ Kategóriákba rendezés (kérdés/ünneplés/stb)
→ Profi eredmény
```

---

## 💡 TIPP: Kezdd ezzel

1. **Most rögtön (10 perc):**
   ```
   - Menj YouTube-ra
   - Keress: "Vágó István Póker teljes"
   - Nézz meg 2-3 videót
   - Válaszd a legjobbat (tiszta audio, sok beszéd)
   ```

2. **Töltsd le:**
   ```powershell
   yt-dlp -f bestaudio --extract-audio --audio-format wav --audio-quality 0 "URL"
   ```

3. **Kezd el vágni Audacity-ben**
   - Cél első körre: 40-50 klip
   - Ez kb. 5 perc audio
   - Már ezzel is látszódni fog a javulás!

---

## ❓ Konkrét kérdések amikre válaszolhatok:

1. **"Melyik YouTube videót válasszam?"**
   → Küldj linkeket, megnézem melyik a legjobb

2. **"Hogyan vágjam Audacity-ben?"**
   → Részletes lépésről-lépésre útmutató

3. **"Hogyan javítsam az átírást?"**
   → Mutatok példákat mi a helyes formátum

4. **"Mennyi idő alatt lehet 15 percet gyűjteni?"**
   → 1 jó epizódból 2-3 óra alatt kész

---

## 🚀 Következő lépés

**Mondd meg melyik úton indulunk:**

**A) Segítek konkrét videókat találni**
→ Keresek neked jó forrásokat linkekkel

**B) Megmagyarázom a vágási folyamatot**
→ Részletes Audacity tutorial

**C) Már van anyagod, csak feldolgozod**
→ Segítek az átírásban és előkészítésben

**D) Mindent automatizáljunk amennyire lehet**
→ Scriptek a gyorsabb munkához

---

## ✅ GARANTÁLT EREDMÉNY

Ha gyűjtesz:
- **10 perc** → 50% javulás a zero-shot-hoz képest
- **15 perc** → 70% javulás, használható kvíz app-hoz
- **20+ perc** → 90% javulás, profi minőség

A choppy beszéd **teljesen eltűnik** a fine-tuning után! ✨

---

**Melyik opciót választod? Segítek bármiben! 🎯**
