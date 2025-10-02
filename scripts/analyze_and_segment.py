"""
Analyze timestamped transcript and segment audio into training samples
Categorizes by content type: greetings, questions, excitement, tension, neutral
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import librosa
import soundfile as sf
import numpy as np

# Content categories with Hungarian keyword patterns
CATEGORIES = {
    'greeting': [
        r'\bgratulálok\b', r'\bköszönöm\b', r'\bszeretettel\b', r'\bkedves\b',
        r'\bvissza\b', r'\büdvözlöm\b', r'\bjó estét\b', r'\bszia\b'
    ],
    'question': [
        r'\bkérdés\b', r'\bmilyen\b', r'\bmelyik\b', r'\bki\b', r'\bhol\b',
        r'\bmikor\b', r'\bhány\b', r'\bmi\b', r'\bmiért\b', r'\bhogyan\b',
        r'\bvajon\b', r'\btegyék\b', r'\bsorrendbe\b'
    ],
    'excitement': [
        r'\bnagyszerű\b', r'\bbriliáns\b', r'\bcsodálatos\b', r'\bfantasztikus\b',
        r'\bszuper\b', r'\bremek\b', r'\bpompás\b', r'\bkiváló\b', r'\bgratulálok\b',
        r'\bjól\b', r'\bhelyes\b', r'\bpersze\b', r'\bbiztos\b'
    ],
    'tension': [
        r'\bgondolkodik\b', r'\bbizonytalan\b', r'\bfigyelem\b', r'\bvigyázz\b',
        r'\bne felejtse\b', r'\bmég\b', r'\bvagy\b', r'\btehát\b', r'\bvégső\b',
        r'\butolsó\b', r'\bfontos\b', r'\belgondolkod\b'
    ],
    'confirmation': [
        r'\bigen\b', r'\bpersze\b', r'\bbiztos\b', r'\bhelyes\b', r'\bjó\b',
        r'\bpontosan\b', r'\btermészetesen\b', r'\bhát\b', r'\bna\b'
    ],
    'transition': [
        r'\bjöjjön\b', r'\bkövetkező\b', r'\btovább\b', r'\bmenjünk\b', r'\bhát\b',
        r'\békkor\b', r'\bmost\b', r'\btehát\b', r'\bés\b', r'\blássuk\b'
    ]
}

# Minimum and maximum duration for clips (seconds)
MIN_DURATION = 2.0
MAX_DURATION = 15.0

# Minimum silence to split segments (seconds)
MIN_SILENCE_GAP = 0.8


def load_transcript(json_path: str) -> List[Dict]:
    """Load timestamped transcript from JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['segments']


def categorize_text(text: str) -> str:
    """
    Categorize text based on keyword patterns.
    Returns single best-matching category (priority order).
    """
    text_lower = text.lower()
    
    # Priority order: more specific categories first
    priority_order = [
        'greeting', 'excitement', 'question', 
        'tension', 'transition', 'confirmation', 'neutral'
    ]
    
    for category in priority_order:
        if category not in CATEGORIES:
            continue
        patterns = CATEGORIES[category]
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return category
    
    return 'neutral'


def merge_segments(segments: List[Dict]) -> List[Dict]:
    """Merge consecutive segments into logical phrases"""
    merged = []
    current = None
    
    for seg in segments:
        if current is None:
            current = {
                'text': seg['text'],
                'start_time': seg['start_time'],
                'end_time': seg['end_time']
            }
        else:
            # Check if we should merge or start new segment
            gap = seg['start_time'] - current['end_time']
            duration = current['end_time'] - current['start_time']
            
            # Merge if: gap is small AND total duration won't exceed max
            if gap < MIN_SILENCE_GAP and duration < MAX_DURATION:
                current['text'] += ' ' + seg['text']
                current['end_time'] = seg['end_time']
            else:
                # Save current and start new
                if duration >= MIN_DURATION:
                    merged.append(current)
                current = {
                    'text': seg['text'],
                    'start_time': seg['start_time'],
                    'end_time': seg['end_time']
                }
    
    # Don't forget the last segment
    if current and (current['end_time'] - current['start_time']) >= MIN_DURATION:
        merged.append(current)
    
    return merged


def analyze_transcript(segments: List[Dict]) -> Dict[str, List[Dict]]:
    """Analyze transcript and categorize segments"""
    # Merge short segments into phrases
    merged_segments = merge_segments(segments)
    
    print(f"Merged {len(segments)} segments into {len(merged_segments)} phrases")
    
    # Categorize each phrase (single category per segment)
    categorized = {cat: [] for cat in CATEGORIES.keys()}
    categorized['neutral'] = []
    
    for seg in merged_segments:
        duration = seg['end_time'] - seg['start_time']
        
        # Add metadata
        seg['duration'] = duration
        
        # Categorize (returns single best match)
        category = categorize_text(seg['text'])
        categorized[category].append(seg)
    
    return categorized


def extract_audio_segment(audio: np.ndarray, sr: int, 
                         start: float, end: float,
                         padding: float = 0.1) -> np.ndarray:
    """Extract audio segment with padding"""
    # Add padding
    start_padded = max(0, start - padding)
    end_padded = end + padding
    
    # Convert to samples
    start_sample = int(start_padded * sr)
    end_sample = int(end_padded * sr)
    
    # Extract
    segment = audio[start_sample:end_sample]
    
    return segment


def create_training_samples(categorized: Dict[str, List[Dict]], 
                           audio_path: str,
                           output_dir: str) -> List[Tuple[str, str, str]]:
    """
    Extract audio clips and create metadata
    Returns: List of (filename, text, category) tuples
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load audio
    print(f"Loading audio from {audio_path}...")
    audio, sr = librosa.load(audio_path, sr=22050)  # Resample to 22050 Hz
    print(f"Audio loaded: {len(audio)/sr:.2f} seconds at {sr} Hz")
    
    metadata = []
    clip_count = 0
    
    # Process each category
    for category, segments in categorized.items():
        if not segments:
            continue
            
        print(f"\nProcessing {category}: {len(segments)} segments")
        
        category_dir = output_path / category
        category_dir.mkdir(exist_ok=True)
        
        for idx, seg in enumerate(segments):
            # Extract audio
            segment_audio = extract_audio_segment(
                audio, sr, 
                seg['start_time'], 
                seg['end_time']
            )
            
            # Generate filename
            filename = f"{category}_{idx+1:03d}.wav"
            filepath = category_dir / filename
            
            # Save audio
            sf.write(filepath, segment_audio, sr)
            
            # Add to metadata
            metadata.append((
                f"{category}/{filename}",
                seg['text'].strip(),
                category
            ))
            
            clip_count += 1
            
            # Print sample for verification
            if idx < 2:  # Show first 2 from each category
                print(f"  {filename}: {seg['text'][:60]}... ({seg['duration']:.2f}s)")
    
    print(f"\n✓ Created {clip_count} training clips")
    
    return metadata


def create_metadata_csv(metadata: List[Tuple[str, str, str]], output_path: str):
    """Create metadata.csv for training"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("audio_file|text|speaker_name\n")
        for filename, text, category in metadata:
            # Clean text: remove extra spaces, normalize
            text_clean = ' '.join(text.split())
            f.write(f"{filename}|{text_clean}|vago\n")
    
    print(f"\n✓ Created metadata: {output_path}")


def print_statistics(categorized: Dict[str, List[Dict]]):
    """Print category statistics"""
    print("\n" + "="*60)
    print("CATEGORY STATISTICS")
    print("="*60)
    
    total_duration = 0
    total_clips = 0
    
    for category in sorted(categorized.keys()):
        segments = categorized[category]
        if not segments:
            continue
            
        duration = sum(s['duration'] for s in segments)
        total_duration += duration
        total_clips += len(segments)
        
        avg_duration = duration / len(segments) if segments else 0
        
        print(f"\n{category.upper()}:")
        print(f"  Clips: {len(segments)}")
        print(f"  Duration: {duration:.2f} seconds ({duration/60:.2f} min)")
        print(f"  Average: {avg_duration:.2f} seconds")
        
        # Show sample texts
        print(f"  Samples:")
        for seg in segments[:3]:
            print(f"    • {seg['text'][:70]}...")
    
    print(f"\n" + "="*60)
    print(f"TOTAL: {total_clips} clips, {total_duration:.2f}s ({total_duration/60:.2f} min)")
    print("="*60)


def main():
    # Paths
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "new_source"
    
    json_path = source_dir / "full_milliomos_vago_source_v1_hun.json"
    audio_path = source_dir / "full_milliomos_vago_source_v1.wav"
    output_dir = project_root / "dataset_milliomos"
    
    print("="*60)
    print("ANALYZING MILLIOMOS TRANSCRIPT")
    print("="*60)
    
    # Load and analyze transcript
    segments = load_transcript(str(json_path))
    print(f"Loaded {len(segments)} transcript segments")
    
    # Categorize
    categorized = analyze_transcript(segments)
    
    # Print statistics
    print_statistics(categorized)
    
    # Ask user confirmation
    print("\n" + "="*60)
    response = input("Extract audio clips and create training dataset? (y/n): ")
    
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Extract audio samples
    print("\n" + "="*60)
    print("EXTRACTING AUDIO CLIPS")
    print("="*60)
    
    metadata = create_training_samples(
        categorized,
        str(audio_path),
        str(output_dir)
    )
    
    # Create metadata CSV
    metadata_path = output_dir / "metadata.csv"
    create_metadata_csv(metadata, str(metadata_path))
    
    print("\n" + "="*60)
    print("✓ DATASET READY FOR FINE-TUNING!")
    print("="*60)
    print(f"\nDataset location: {output_dir}")
    print(f"Total clips: {len(metadata)}")
    print(f"\nNext step: Run training with:")
    print(f"  python scripts\\train_xtts.py")


if __name__ == "__main__":
    main()
