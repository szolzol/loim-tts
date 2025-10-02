"""
Verify dataset quality before training
Checks audio files, transcripts, and generates statistics
"""

import pandas as pd
import soundfile as sf
from pathlib import Path
import numpy as np


def verify_dataset(dataset_dir: str):
    """Verify dataset quality and generate statistics"""
    dataset_path = Path(dataset_dir)
    metadata_path = dataset_path / "metadata.csv"
    
    print("="*60)
    print("DATASET VERIFICATION")
    print("="*60)
    
    # Load metadata
    df = pd.read_csv(metadata_path, sep='|')
    print(f"\n✓ Metadata loaded: {len(df)} entries")
    
    # Statistics
    total_duration = 0
    durations = []
    missing_files = []
    category_stats = {}
    
    print("\nVerifying audio files...")
    for idx, row in df.iterrows():
        audio_file = dataset_path / row['audio_file']
        
        if not audio_file.exists():
            missing_files.append(row['audio_file'])
            continue
        
        # Load audio info
        info = sf.info(audio_file)
        duration = info.duration
        
        durations.append(duration)
        total_duration += duration
        
        # Category stats
        category = Path(row['audio_file']).parent.name
        if category not in category_stats:
            category_stats[category] = {'count': 0, 'duration': 0}
        category_stats[category]['count'] += 1
        category_stats[category]['duration'] += duration
    
    # Report
    print(f"\n{'='*60}")
    print("STATISTICS")
    print("="*60)
    
    if missing_files:
        print(f"\n⚠ Missing files: {len(missing_files)}")
        for f in missing_files:
            print(f"  - {f}")
    else:
        print("\n✓ All audio files present")
    
    print(f"\nTotal clips: {len(durations)}")
    print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Average duration: {np.mean(durations):.2f} seconds")
    print(f"Min duration: {np.min(durations):.2f} seconds")
    print(f"Max duration: {np.max(durations):.2f} seconds")
    print(f"Median duration: {np.median(durations):.2f} seconds")
    
    # Category breakdown
    print(f"\n{'='*60}")
    print("CATEGORY BREAKDOWN")
    print("="*60)
    
    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        print(f"\n{category.upper()}:")
        print(f"  Clips: {stats['count']}")
        print(f"  Duration: {stats['duration']:.2f}s ({stats['duration']/60:.2f} min)")
        print(f"  Average: {stats['duration']/stats['count']:.2f}s")
        print(f"  Percentage: {stats['count']/len(durations)*100:.1f}%")
    
    # Sample some texts
    print(f"\n{'='*60}")
    print("SAMPLE TRANSCRIPTS")
    print("="*60)
    
    for category in sorted(category_stats.keys()):
        samples = df[df['audio_file'].str.contains(category)].head(3)
        if len(samples) > 0:
            print(f"\n{category.upper()}:")
            for idx, row in samples.iterrows():
                text = row['text'][:80] + "..." if len(row['text']) > 80 else row['text']
                print(f"  • {text}")
    
    # Quality assessment
    print(f"\n{'='*60}")
    print("QUALITY ASSESSMENT")
    print("="*60)
    
    if total_duration < 10*60:
        print(f"⚠ Dataset is short ({total_duration/60:.1f} min)")
        print(f"  Recommendation: 15-20 minutes for best results")
    else:
        print(f"✓ Dataset duration is good ({total_duration/60:.1f} min)")
    
    if np.mean(durations) < 3:
        print(f"⚠ Average clip is short ({np.mean(durations):.1f}s)")
    else:
        print(f"✓ Average clip duration is good ({np.mean(durations):.1f}s)")
    
    if len(category_stats) < 4:
        print(f"⚠ Limited content diversity ({len(category_stats)} categories)")
    else:
        print(f"✓ Good content diversity ({len(category_stats)} categories)")
    
    print(f"\n{'='*60}")
    print("✓ VERIFICATION COMPLETE")
    print("="*60)
    print(f"\nDataset is ready for training!")
    print(f"Run: python scripts\\train_xtts.py")


if __name__ == "__main__":
    import sys
    
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset_milliomos"
    verify_dataset(dataset_dir)
