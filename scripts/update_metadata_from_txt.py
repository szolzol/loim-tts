"""
Extract transcriptions from .txt files and update metadata.csv
"""

import re
from pathlib import Path
import csv

SOURCE_DIR = Path("i:/CODE/tts-2/prepared_sources/vago_samples_selected")
OUTPUT_DIR = Path("i:/CODE/tts-2/dataset_phase4")
METADATA_FILE = OUTPUT_DIR / "metadata.csv"

def extract_text_from_transcript(txt_file):
    """Extract spoken text from timestamped transcript file"""
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract text after Speaker labels, ignoring timestamps and stage directions
    lines = []
    for line in content.split('\n'):
        # Skip timestamp lines
        if '-->' in line or '[Speaker' in line:
            continue
        # Skip stage directions like [közönség tapsol], [bevezető dallam]
        if line.strip().startswith('[') and line.strip().endswith(']'):
            continue
        # Skip empty lines
        if not line.strip():
            continue
        
        # Clean up any remaining stage directions within text
        cleaned = re.sub(r'\[.*?\]', '', line).strip()
        if cleaned:
            lines.append(cleaned)
    
    # Join all lines into single text
    return ' '.join(lines).strip()

print("=" * 80)
print("📝 EXTRACTING TRANSCRIPTIONS FROM .TXT FILES")
print("=" * 80)
print()

metadata = []
total_processed = 0

# Process excitement samples
print("Processing excitement samples...")
for i in range(1, 11):
    txt_file = SOURCE_DIR / f"excitement{i}.wav.txt"
    if txt_file.exists():
        text = extract_text_from_transcript(txt_file)
        metadata.append([f"excitement/excitement{i}.wav", text, "vago_istvan"])
        print(f"  ✅ excitement{i}: {text[:60]}...")
        total_processed += 1

print()

# Process neutral samples
print("Processing neutral samples...")
for i in range(1, 15):
    txt_file = SOURCE_DIR / f"neutral{i}.wav.txt"
    if txt_file.exists():
        text = extract_text_from_transcript(txt_file)
        metadata.append([f"neutral/neutral{i}.wav", text, "vago_istvan"])
        print(f"  ✅ neutral{i}: {text[:60]}...")
        total_processed += 1

print()

# Process question samples
print("Processing question samples...")
for i in range(1, 17):
    txt_file = SOURCE_DIR / f"question{i}.wav.txt"
    if txt_file.exists():
        text = extract_text_from_transcript(txt_file)
        metadata.append([f"question/question{i}.wav", text, "vago_istvan"])
        print(f"  ✅ question{i}: {text[:60]}...")
        total_processed += 1

print()
print(f"✅ Processed {total_processed} transcriptions")
print()

# Write metadata.csv
print(f"📝 Writing metadata to: {METADATA_FILE}")
with open(METADATA_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='|')
    writer.writerows(metadata)

print(f"✅ Metadata file updated with {len(metadata)} entries")
print()

# Show sample
print("📄 Sample entries:")
for i, entry in enumerate(metadata[:3], 1):
    print(f"  {i}. {entry[0]}")
    print(f"     Text: {entry[1][:80]}...")
    print()

print("=" * 80)
print("✅ METADATA UPDATE COMPLETE")
print("=" * 80)
print()
print(f"📁 File: {METADATA_FILE}")
print(f"📊 Total entries: {len(metadata)}")
print()
print("🎯 Next: Continue with training!")
print()
