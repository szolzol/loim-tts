"""
Merge all quiz show segments into a single audio file
"""
import os
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
import datetime

# Paths
SEGMENTS_DIR = Path("output_quiz_show")
OUTPUT_FILE = Path("output_quiz_show/full_quiz_show_merged.wav")
ORIGINAL_FILE = Path("new_source/full_milliomos_vago_source_v1.wav")

print("🎬 Merging quiz show segments...")
print(f"Input: {SEGMENTS_DIR}")
print(f"Output: {OUTPUT_FILE}")
print()

# Get all segment files
segment_files = sorted(SEGMENTS_DIR.glob("quiz_show_*.wav"))
print(f"Found {len(segment_files)} segments")

# Start with empty audio
combined = AudioSegment.empty()

# Merge all segments
for i, segment_path in enumerate(segment_files, 1):
    if i % 50 == 0:
        print(f"Processing segment {i}/{len(segment_files)}...")
    
    segment = AudioSegment.from_wav(str(segment_path))
    combined += segment

# Export merged audio
print(f"\n💾 Saving merged audio...")
combined.export(str(OUTPUT_FILE), format="wav")

# Get statistics
merged_duration = len(combined) / 1000  # milliseconds to seconds
merged_size = OUTPUT_FILE.stat().st_size / (1024 * 1024)  # bytes to MB

print(f"✅ Merged audio saved!")
print(f"Duration: {merged_duration:.1f} seconds ({merged_duration/60:.1f} minutes)")
print(f"Size: {merged_size:.2f} MB")
print(f"Location: {OUTPUT_FILE}")
print()

# Compare with original if it exists
if ORIGINAL_FILE.exists():
    print("📊 Comparing with original recording...")
    print(f"Original: {ORIGINAL_FILE}")
    
    original = AudioSegment.from_wav(str(ORIGINAL_FILE))
    original_duration = len(original) / 1000
    original_size = ORIGINAL_FILE.stat().st_size / (1024 * 1024)
    
    print(f"\nOriginal Recording:")
    print(f"  Duration: {original_duration:.1f} seconds ({original_duration/60:.1f} minutes)")
    print(f"  Size: {original_size:.2f} MB")
    print(f"  Sample Rate: {original.frame_rate} Hz")
    print(f"  Channels: {original.channels}")
    
    print(f"\nGenerated Recording:")
    print(f"  Duration: {merged_duration:.1f} seconds ({merged_duration/60:.1f} minutes)")
    print(f"  Size: {merged_size:.2f} MB")
    print(f"  Sample Rate: {combined.frame_rate} Hz")
    print(f"  Channels: {combined.channels}")
    
    # Calculate differences
    duration_diff = merged_duration - original_duration
    duration_diff_pct = (duration_diff / original_duration) * 100
    
    print(f"\n📈 Comparison:")
    print(f"  Duration difference: {duration_diff:+.1f} seconds ({duration_diff_pct:+.1f}%)")
    
    if abs(duration_diff_pct) < 5:
        print(f"  ✅ Duration is very close to original!")
    elif abs(duration_diff_pct) < 15:
        print(f"  ⚠️  Duration is somewhat different from original")
    else:
        print(f"  ❌ Duration is significantly different from original")
    
    print(f"\n💡 To listen side-by-side:")
    print(f"   Original: {ORIGINAL_FILE}")
    print(f"   Generated: {OUTPUT_FILE}")
else:
    print(f"⚠️  Original file not found: {ORIGINAL_FILE}")
    print("Cannot compare with original recording.")

print("\n🎉 Done!")
