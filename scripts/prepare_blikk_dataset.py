"""
Prepare Blikk Interview Dataset for Training
Converts metadata.json format to metadata.csv format
Combines with existing Milliomos dataset
"""

import json
import csv
import shutil
from pathlib import Path

PROJECT_ROOT = Path("f:/CODE/tts-2")
BLIKK_DIR = PROJECT_ROOT / "dataset_blikk"
MILLIOMOS_DIR = PROJECT_ROOT / "dataset_milliomos"
COMBINED_DIR = PROJECT_ROOT / "dataset_combined"

def prepare_blikk_dataset():
    """Convert Blikk dataset to training format"""
    
    print("="*70)
    print("PREPARE BLIKK INTERVIEW DATASET")
    print("István Vágó - Interview Clips")
    print("="*70)
    
    # Load metadata.json
    metadata_file = BLIKK_DIR / "metadata.json"
    
    if not metadata_file.exists():
        print(f"\n❌ metadata.json not found: {metadata_file}")
        return False
    
    print(f"\n📖 Loading metadata...")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        blikk_data = json.load(f)
    
    print(f"✓ Found {len(blikk_data)} samples")
    
    # Analyze dataset
    categories = {}
    total_duration = 0
    issues = []
    
    for item in blikk_data:
        category = item.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
        total_duration += item.get('duration', 0)
        
        # Check text length
        text = item.get('text', '')
        if len(text) > 224:
            issues.append({
                'file': Path(item['filename']).name,
                'length': len(text),
                'text': text[:100] + '...'
            })
    
    print(f"\n📊 Dataset statistics:")
    print(f"   Total samples: {len(blikk_data)}")
    print(f"   Total duration: {total_duration/60:.2f} minutes")
    print(f"\n   Category breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"      {cat:10s}: {count:3d} samples")
    
    # Check for text length issues
    if issues:
        print(f"\n⚠️  WARNING: {len(issues)} texts exceed 224 character limit!")
        print(f"   These will need truncation:")
        for issue in issues[:5]:
            print(f"      {issue['file']}: {issue['length']} chars")
            print(f"         Text: {issue['text']}")
        
        if len(issues) > 5:
            print(f"      ... and {len(issues) - 5} more")
    
    # Create combined dataset directory
    print(f"\n📁 Creating combined dataset...")
    COMBINED_DIR.mkdir(exist_ok=True)
    
    # Copy Milliomos dataset
    print(f"\n📂 Copying Milliomos dataset...")
    milliomos_csv = MILLIOMOS_DIR / "metadata.csv"
    
    if not milliomos_csv.exists():
        print(f"   ⚠️  Milliomos metadata not found: {milliomos_csv}")
        print(f"   Will create new dataset with only Blikk data")
        milliomos_rows = []
    else:
        with open(milliomos_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            milliomos_rows = list(reader)
        print(f"   ✓ Loaded {len(milliomos_rows)} Milliomos samples")
        
        # Copy Milliomos audio files
        for row in milliomos_rows:
            src_file = MILLIOMOS_DIR / row['audio_file']
            if src_file.exists():
                # Preserve directory structure
                category = row['audio_file'].split('/')[0]
                cat_dir = COMBINED_DIR / category
                cat_dir.mkdir(exist_ok=True)
                
                dst_file = COMBINED_DIR / row['audio_file']
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
    
    # Process Blikk data
    print(f"\n📂 Processing Blikk dataset...")
    blikk_rows = []
    copied_count = 0
    skipped_count = 0
    
    for item in blikk_data:
        src_path = Path(item['filename'])
        
        if not src_path.exists():
            skipped_count += 1
            continue
        
        # Get category and create directory
        category = item.get('category', 'neutral')
        cat_dir = COMBINED_DIR / category
        cat_dir.mkdir(exist_ok=True)
        
        # Copy audio file with simplified name
        filename = src_path.name
        dst_file = cat_dir / filename
        
        if not dst_file.exists():
            shutil.copy2(src_path, dst_file)
            copied_count += 1
        
        # Prepare row
        text = item.get('text', '').strip()
        
        # Truncate if needed (Hungarian limit is 224 chars)
        if len(text) > 224:
            # Smart truncation at sentence boundary
            text = text[:221] + '...'
        
        blikk_rows.append({
            'audio_file': f"{category}/{filename}",
            'text': text,
            'speaker_name': 'vago'
        })
    
    print(f"   ✓ Copied {copied_count} audio files")
    if skipped_count > 0:
        print(f"   ⚠️  Skipped {skipped_count} missing files")
    
    # Combine datasets
    print(f"\n🔗 Combining datasets...")
    combined_rows = milliomos_rows + blikk_rows
    
    print(f"   Milliomos: {len(milliomos_rows)} samples")
    print(f"   Blikk:     {len(blikk_rows)} samples")
    print(f"   Combined:  {len(combined_rows)} samples")
    
    # Calculate total duration
    milliomos_duration = 14.8  # Known from previous analysis
    blikk_duration = total_duration / 60
    total = milliomos_duration + blikk_duration
    
    print(f"\n⏱️  Total duration:")
    print(f"   Milliomos: {milliomos_duration:.1f} minutes")
    print(f"   Blikk:     {blikk_duration:.1f} minutes")
    print(f"   Combined:  {total:.1f} minutes")
    
    # Write combined metadata.csv
    metadata_out = COMBINED_DIR / "metadata.csv"
    
    print(f"\n💾 Writing metadata.csv...")
    with open(metadata_out, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['audio_file', 'text', 'speaker_name'], delimiter='|')
        writer.writeheader()
        writer.writerows(combined_rows)
    
    print(f"   ✓ Written: {metadata_out}")
    
    # Summary
    print(f"\n" + "="*70)
    print("✅ DATASET PREPARATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Combined dataset location:")
    print(f"   {COMBINED_DIR}")
    print(f"\n📊 Final statistics:")
    print(f"   Total samples: {len(combined_rows)}")
    print(f"   Total duration: {total:.1f} minutes")
    print(f"   Quality: {'🟢 EXCELLENT' if total >= 30 else '🟡 GOOD' if total >= 20 else '🔴 MODERATE'}")
    
    print(f"\n🎯 Next step:")
    print(f"   Run training with combined dataset:")
    print(f"   python scripts\\train_combined.py")
    
    return True


if __name__ == "__main__":
    success = prepare_blikk_dataset()
    
    if not success:
        print("\n❌ Dataset preparation failed!")
        exit(1)
