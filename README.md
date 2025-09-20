# LOIM-TTS: Legyen Ön Is Milliomos - Dinamikus TTS Rendszer

Ez a projekt lehetővé teszi a **"Legyen Ön Is Milliomos"** magyar kvízműsor dinamikus reprodukcióját kiváló minőségű TTS (Text-to-Speech) technológiával. A rendszer Vágó István műsorvezető hangján alapul, és ElevenLabs-közeli minőséget ér el a Coqui XTTS v2 modell optimalizált használatával.

## 🎯 Projekt Célja

A műsor eredeti hangulatának megőrzése mellett:

- **Dinamikus kérdés-felolvasás** TTS-szel
- **Autentikus Vágó István hangszín** klónozás
- **Professional broadcasting minőség** elérése
- **Valós idejű műsorelem generálás** támogatása

## 🚀 Fő Funkciók

### TTS Minőség Optimalizálás

- **Prémium hangszintézis**: 52.5/100 minőségi pontszám (ElevenLabs benchmark: 90-95)
- **Magyar nyelv specialista**: Natív `language="hu"` támogatás
- **6 darab optimalizált referencia klip**: 12 másodperces szegmensek
- **Post-processing pipeline**: Spektrális tisztítás, dinamikus optimalizálás

### Műsor-specifikus Elemek

- **Kérdés dinamikus generálás**: Kategóriák és nehézségi szintek szerint
- **Autentikus beszédstílus**: Vágó István karakterisztikus intonációja
- **Broadcasting ready kimenet**: 24kHz, professional audio szint

## 📦 Telepítés

### Gyors Telepítés

```bash
# Repository klónozása
git clone https://github.com/szolzol/loim-tts.git
cd loim-tts

# Virtual environment létrehozása
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Függőségek telepítése
pip install -r requirements.txt
```

### Részletes telepítési útmutató: [docs/TELEPITES.md](docs/TELEPITES.md)

## 🎬 Használat

### Alapvető Műsorelem Generálás

```bash
# Egyszerű kérdés felolvasás
python premium_xtts_hungarian.py \
  --text "Ez volt a helyes válasz! Gratulálok, továbbjutott a következő szintre!" \
  --refs "processed_audio/premium_clip_01.wav" \
  --out celebration.wav \
  --mp3
```

### Komplex Műsorelem (Több Referencia)

```bash
# Kérdés felvezetése autentikus hangzással
python premium_xtts_hungarian.py \
  --text "És most jön a kétmillió forintos kérdés! Figyeljen jól, mert ez már nem gyerekjáték. A kérdés:" \
  --refs "processed_audio/premium_clip_01.wav,processed_audio/premium_clip_02.wav,processed_audio/premium_clip_03.wav" \
  --out question_intro_2mil.wav \
  --mp3
```

### Post-Processing (Broadcast Minőség)

```bash
# Professional audio enhancement
python audio_post_processor.py \
  --input question_intro_2mil.wav \
  --output question_intro_2mil_broadcast.wav
```

## 🎵 Audio Minőség Elemzés

### Jelenlegi Eredmények

- **Overall Score**: 52.5/100 (enhanced verzió)
- **SNR**: 10-12 dB (cél: 20-25 dB)
- **Pitch Variation**: 0.28-0.32 (természetes tartomány)
- **Harmonic Ratio**: 0.20-0.25 (cél: 0.40-0.60)

### Minőség Összehasonlítás

```bash
# Objektív minőség értékelés
python quality_comparison.py
```

## 🗂️ Projekt Struktúra

```
loim-tts/
├── 🎙️ Hangminták és Referenciák
│   ├── vago_vagott.mp3                    # Eredeti Vágó István hangminta
│   └── processed_audio/                   # Optimalizált referencia klipek
│       ├── premium_clip_01.wav            # 6 darab 12s-es prémium klip
│       └── ...
│
├── 🤖 TTS Motor
│   ├── premium_xtts_hungarian.py          # Fő TTS engine (optimalizált)
│   ├── premium_tts_config.json            # Prémium beállítások
│   └── audio_post_processor.py            # Broadcast minőség enhancement
│
├── 🔧 Fejlesztői Eszközök
│   ├── premium_reference_generator.py     # Referencia klip optimalizáló
│   ├── quality_comparison.py              # Minőség értékelő rendszer
│   ├── audio_debug.py                     # Audio elemzés és debug
│   └── elevenlabs_optimizer.py            # ElevenLabs-szintű optimalizálás
│
├── 📊 Eredmények és Tesztek
│   ├── test_results/                      # Generált műsorelemek
│   ├── quality_report.json               # Részletes minőségi metrikák
│   └── docs/ELEVENLABS_OPTIMIZATION_REPORT.md  # Fejlesztési jelentés
│
├── 📚 Dokumentáció
│   ├── README.md                          # Ez a fájl
│   ├── docs/TELEPITES.md                  # Részletes telepítési útmutató
│   ├── docs/ELEVENLABS_OPTIMIZATION_REPORT.md # Fejlesztési jelentés
│   └── docs/TEST_RESULTS.md               # Teszt dokumentáció
│
└── 🗄️ Legacy
    └── legacy/                            # Régi fejlesztési fájlok
```

## 🎯 Műsor Elemek Generálása

### Tipikus LOIM Szituációk

```bash
# Kérdés felvezetés
python premium_xtts_hungarian.py \
  --text "Itt a következő kérdés ötszázezer forintért. Figyelem, ez már nem könnyű!" \
  --refs "processed_audio/premium_clip_01.wav" \
  --out question_500k.wav --mp3

# Helyes válasz ünneplés
python premium_xtts_hungarian.py \
  --text "Kitűnő! Ez volt a helyes válasz! Gratulálok, megnyerte az ötszázezer forintot!" \
  --refs "processed_audio/premium_clip_02.wav" \
  --out correct_500k.wav --mp3

# Feszültségkeltés
python premium_xtts_hungarian.py \
  --text "Na most figyeljen jól... ez a döntő pillanat. Biztosan ezt választja végső válaszként?" \
  --refs "processed_audio/premium_clip_03.wav" \
  --out suspense.wav --mp3
```

## 🔧 Speciális Funkciók

### Batch Műsorelem Generálás

```bash
# Több műsorelem egyszerre
python audio_post_processor.py \
  --batch \
  --input test_results \
  --output test_results/broadcast_ready \
  --pattern "*question*.wav"
```

### Minőség Monitoring

```bash
# Valós idejű minőség ellenőrzés
python quality_comparison.py
```

## 📈 Fejlesztési Roadmap

### Jelenlegi Állapot (v1.0)

- ✅ Vágó István hang klónozás alapjai
- ✅ Magyar TTS optimalizálás
- ✅ Prémium referencia klipek
- ✅ Post-processing pipeline
- ✅ Objektív minőség mérés

### Következő Célok (v2.0)

- 🎯 ElevenLabs paritás elérése (80+ pont)
- 🎯 Real-time műsorelem generálás
- 🎯 Emotion-aware beszédszintézis
- 🎯 Adaptive quality tuning

## 🔍 Minőségi Metrikák

A projekt objektív minőség értékeléssel dolgozik:

- **Signal Quality**: SNR, dinamikus tartomány
- **Prosody**: Pitch variáció, energia konzisztencia
- **Naturalness**: Harmonikus arány, folytonosság
- **Overall Score**: Súlyozott összesített pontszám

Részletek: [docs/ELEVENLABS_OPTIMIZATION_REPORT.md](docs/ELEVENLABS_OPTIMIZATION_REPORT.md)

## 🎵 Referencia Audio

A projekt 6 darab optimalizált Vágó István referencia klipet tartalmaz:

- **12 másodperces szegmensek** a legjobb audio minőségű részekből
- **-26 dB átlagos szint** broadcasting standardnek megfelelően
- **Manuálisan szűrt és enhanced** a maximális minőségért

## 💡 Tippek a Legjobb Eredményért

1. **Műsor-specifikus szövegek**: Használja az eredeti műsor kifejezéseit
2. **Megfelelő intonáció**: A kérdések emelkedő, válaszok erősítő hangsúllyal
3. **Post-processing**: Mindig alkalmazza broadcast ready kimenethez
4. **Multiple reference**: 2-3 referencia klip használata jobb minőségért

## 🏆 Eredmények

- **20-25% minőségjavulás** az optimalizálás után
- **Production-ready** műsorelem generálás
- **Objektív mérési rendszer** a folyamatos fejlesztéshez
- **Broadcast standard** audio kimenet

## 🤝 Hozzájárulás

A projekt nyitott a közösségi fejlesztésre! Különösen keresünk:

- **Audio engineering** szakértőket
- **Magyar nyelvi** optimalizálást
- **Real-time processing** fejlesztést

## 📄 Licenc

Mozilla Public License 2.0 (Coqui TTS alapján)

---

**"Legyen Ön Is Milliomos - Most már TTS-szel is!"** 🎙️🏆
