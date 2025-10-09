"""
Prepare Phase 4 Dataset - New Selected Vágó Samples
====================================================
Prepares the 40 new high-quality samples from vago_samples_selected
- 10 excitement samples
- 14 neutral samples  
- 16 question samples

Creates metadata.csv for training continuation from checkpoint 1901
"""

import os
import shutil
from pathlib import Path
import soundfile as sf
import csv

# Paths
PROJECT_ROOT = Path("i:/CODE/tts-2")
SOURCE_DIR = PROJECT_ROOT / "prepared_sources" / "vago_samples_selected"
OUTPUT_DIR = PROJECT_ROOT / "dataset_phase4"
OUTPUT_DIR.mkdir(exist_ok=True)

# Sample rate for XTTS-v2
TARGET_SAMPLE_RATE = 22050

print("=" * 80)
print("🎯 PHASE 4 DATASET PREPARATION")
print("=" * 80)
print()
print(f"📂 Source: {SOURCE_DIR}")
print(f"📂 Output: {OUTPUT_DIR}")
print(f"🎵 Target sample rate: {TARGET_SAMPLE_RATE} Hz")
print()

# Manual transcriptions for each sample
# These are placeholder transcriptions - YOU NEED TO UPDATE THESE!
TRANSCRIPTIONS = {
    # EXCITEMENT samples
    "excitement/excitement1.wav": "Fantasztikus! Gratulálok a helyes válaszhoz!",
    "excitement/excitement2.wav": "Hihetetlen teljesítmény! Nagyszerű!",
    "excitement/excitement3.wav": "Ez aztán a siker! Gratulálok!",
    "excitement/excitement4.wav": "Óriási! Csak így tovább!",
    "excitement/excitement5.wav": "Briliáns! Remek munka!",
    "excitement/excitement6.wav": "Csodálatos! Kitűnő válasz!",
    "excitement/excitement7.wav": "Nagyszerű! Tökéletes!",
    "excitement/excitement8.wav": "Fantasztikus teljesítmény! Gratulálok!",
    "excitement/excitement9.wav": "Remek! Csak így tovább!",
    "excitement/excitement10.wav": "Kiváló! Csodálatos munka!",
    
    # NEUTRAL samples
    "neutral/neutral1.wav": "Üdvözlöm önöket a mai kvízműsorban.",
    "neutral/neutral2.wav": "Kezdjük a következő kérdéssel.",
    "neutral/neutral3.wav": "Lássuk a helyes választ.",
    "neutral/neutral4.wav": "Itt az idő dönteni.",
    "neutral/neutral5.wav": "Figyeljünk most a következő feladatra.",
    "neutral/neutral6.wav": "Köszönöm a válaszukat.",
    "neutral/neutral7.wav": "Most következik egy újabb kérdés.",
    "neutral/neutral8.wav": "Gondolkodjanak csak nyugodtan.",
    "neutral/neutral9.wav": "Halljuk a lehetőségeket.",
    "neutral/neutral10.wav": "Köszönöm szépen a figyelmet.",
    "neutral/neutral11.wav": "Lássuk tovább a játékot.",
    "neutral/neutral12.wav": "Következik a döntő kérdés.",
    "neutral/neutral13.wav": "Figyeljünk most a részletekre.",
    "neutral/neutral14.wav": "Köszönöm a részvételt mindenkinek.",
    
    # QUESTION samples
    "question/question1.wav": "Melyik évben történt ez az esemény?",
    "question/question2.wav": "Ki volt az első ember a Holdon?",
    "question/question3.wav": "Hány kontinens van a Földön?",
    "question/question4.wav": "Melyik ország fővárosa London?",
    "question/question5.wav": "Mikor fedezte fel Kolumbusz Amerikát?",
    "question/question6.wav": "Hány bolygó van a Naprendszerben?",
    "question/question7.wav": "Ki írta a Toldi című művet?",
    "question/question8.wav": "Melyik a legnagyobb óceán?",
    "question/question9.wav": "Hány éves korában halt meg Mozart?",
    "question/question10.wav": "Melyik évben tört ki a második világháború?",
    "question/question11.wav": "Ki festette a Mona Lisát?",
    "question/question12.wav": "Hány húrja van egy hegedűnek?",
    "question/question13.wav": "Melyik elem vegyjele az Au?",
    "question/question14.wav": "Ki volt Magyarország első királya?",
    "question/question15.wav": "Hány perc van egy órában?",
    "question/question16.wav": "Melyik városban van az Eiffel-torony?",
}

print("⚠️  IMPORTANT: Update transcriptions in this script before running!")
print("   Current transcriptions are PLACEHOLDERS - listen to each file")
print("   and update the TRANSCRIPTIONS dictionary with exact text.")
print()
input("Press Enter to continue if transcriptions are correct, or Ctrl+C to cancel...")
print()

# Create category directories
for category in ["excitement", "neutral", "question"]:
    (OUTPUT_DIR / category).mkdir(exist_ok=True)

# Prepare metadata
metadata = []
total_duration = 0.0
processed_count = 0

print("🔄 Processing samples...")
print()

for rel_path, text in TRANSCRIPTIONS.items():
    source_file = SOURCE_DIR / rel_path
    
    if not source_file.exists():
        print(f"⚠️  WARNING: File not found: {rel_path}")
        continue
    
    # Read audio
    try:
        audio, sr = sf.read(str(source_file))
        duration = len(audio) / sr
        
        # Resample if needed
        if sr != TARGET_SAMPLE_RATE:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SAMPLE_RATE)
            sr = TARGET_SAMPLE_RATE
        
        # Create output filename
        category = rel_path.split('/')[0]
        filename = Path(rel_path).name
        output_path = OUTPUT_DIR / category / filename
        
        # Save resampled audio
        sf.write(str(output_path), audio, sr)
        
        # Add to metadata (format: audio_file|text|speaker_name)
        relative_path = f"{category}/{filename}"
        metadata.append([relative_path, text, "vago_istvan"])
        
        total_duration += duration
        processed_count += 1
        
        print(f"✅ {relative_path:<40} ({duration:.2f}s)")
        
    except Exception as e:
        print(f"❌ ERROR processing {rel_path}: {e}")
        continue

print()
print(f"✅ Processed {processed_count} samples")
print(f"⏱️  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
print()

# Write metadata.csv
metadata_file = OUTPUT_DIR / "metadata.csv"
with open(metadata_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='|')
    writer.writerows(metadata)

print(f"📝 Metadata saved: {metadata_file}")
print(f"   {len(metadata)} entries")
print()

# Summary
print("=" * 80)
print("✅ PHASE 4 DATASET PREPARATION COMPLETE")
print("=" * 80)
print()
print("📊 Dataset Statistics:")
print(f"   • Total samples: {processed_count}")
print(f"   • Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
print(f"   • Average duration: {total_duration/processed_count:.2f}s per sample")
print(f"   • Sample rate: {TARGET_SAMPLE_RATE} Hz")
print()
print("📂 Output structure:")
print(f"   {OUTPUT_DIR}/")
print(f"   ├── excitement/  ({len([k for k in TRANSCRIPTIONS if 'excitement' in k])} samples)")
print(f"   ├── neutral/     ({len([k for k in TRANSCRIPTIONS if 'neutral' in k])} samples)")
print(f"   ├── question/    ({len([k for k in TRANSCRIPTIONS if 'question' in k])} samples)")
print(f"   └── metadata.csv")
print()
print("🎯 Next Steps:")
print("   1. Verify metadata.csv transcriptions are accurate")
print("   2. Run training script: python scripts/train_phase4_continuation.py")
print("   3. Monitor Mel CE score improvement")
print()
print("⚠️  REMINDER: This will continue from checkpoint 1901 (Mel CE: 2.971)")
print()
