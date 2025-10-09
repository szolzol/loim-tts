"""
Convert metadata.csv to proper Coqui format with headers
"""

import csv
from pathlib import Path

METADATA_FILE = Path("i:/CODE/tts-2/dataset_phase4/metadata.csv")

print("🔧 Converting metadata.csv to Coqui format...")

# Read existing data
rows = []
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        if len(row) >= 2:
            audio_file = row[0]
            text = row[1]
            rows.append({'audio_file': audio_file, 'text': text})

print(f"✅ Read {len(rows)} entries")

# Write with headers in Coqui format
with open(METADATA_FILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['audio_file', 'text'], delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Metadata updated with proper headers")
print(f"📁 File: {METADATA_FILE}")
print()

# Show first few entries
print("📄 First 3 entries:")
for i, row in enumerate(rows[:3], 1):
    print(f"  {i}. {row['audio_file']}")
    print(f"     {row['text'][:70]}...")
    print()

print("✅ Done!")
