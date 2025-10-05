"""
Step 2: Extract sentence samples from clean Vágó-only audio.
Creates individual WAV files for each sentence, categorized by length.
Ready for XTTS fine-tuning.
"""

import json
import os
from pydub import AudioSegment
import re

# Configuration
SOURCE_AUDIO = "new_source_2/vago_only.wav"
SOURCE_SEGMENTS = "new_source_2/vago_only_segments.json"
OUTPUT_DIR = "new_source_2/vago_samples_clean"

# Sample length thresholds (in seconds)
SHORT_MAX = 5.0      # Short samples: up to 5 seconds
LONG_MIN = 5.0       # Long samples: 5-10 seconds
VERY_LONG_MIN = 10.0 # Very long: 10+ seconds

def load_segments(json_path):
    """Load the segment map."""
    print(f"Loading segment map from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded {data['total_segments']} segments")
    return data['segments']

def clean_text(text):
    """Clean text for filename and metadata."""
    # Remove special characters, keep alphanumeric and Hungarian chars
    text = re.sub(r'[^\w\s\-áéíóöőúüűÁÉÍÓÖŐÚÜŰ]', '', text)
    # Replace spaces with underscores, limit length
    text = text.strip().replace(' ', '_')[:80]
    return text

def split_segment_into_sentences(segment):
    """
    Split a segment into individual sentences.
    Returns list of sentences with estimated timings.
    """
    text = segment['text']
    duration = segment['duration']
    start_time = segment['new_start']
    
    # Split at sentence boundaries
    sentence_pattern = r'([^.!?]+[.!?]+)'
    sentences = re.findall(sentence_pattern, text)
    
    # If no sentences found (no punctuation), treat whole text as one sentence
    if not sentences:
        return [{
            'text': text.strip(),
            'start_time': start_time,
            'end_time': segment['new_end'],
            'duration': duration
        }]
    
    # Calculate approximate time per character
    time_per_char = duration / len(text) if len(text) > 0 else 0
    
    # Create sentence segments with timings
    sentence_segments = []
    char_offset = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Calculate timing based on character position
        sentence_duration = len(sentence) * time_per_char
        sentence_start = start_time + (char_offset * time_per_char)
        sentence_end = sentence_start + sentence_duration
        
        sentence_segments.append({
            'text': sentence,
            'start_time': sentence_start,
            'end_time': sentence_end,
            'duration': sentence_duration
        })
        
        char_offset += len(sentence)
    
    return sentence_segments

def extract_all_sentences(segments):
    """Extract all sentences from all segments."""
    print("\nExtracting sentences from segments...")
    
    all_sentences = []
    
    for segment in segments:
        # Split segment into sentences
        sentences = split_segment_into_sentences(segment)
        
        # Add valid sentences (>= 0.5 seconds)
        for sentence in sentences:
            if sentence['duration'] >= 0.5:
                all_sentences.append(sentence)
    
    print(f"✓ Extracted {len(all_sentences)} sentences")
    return all_sentences

def categorize_by_length(sentences):
    """Categorize sentences by duration."""
    print("\nCategorizing by sentence length...")
    
    short_samples = []
    long_samples = []
    very_long_samples = []
    
    for sentence in sentences:
        duration = sentence['duration']
        
        if duration <= SHORT_MAX:
            short_samples.append(sentence)
        elif duration < VERY_LONG_MIN:
            long_samples.append(sentence)
        else:
            very_long_samples.append(sentence)
    
    print(f"  Short (0.5-{SHORT_MAX}s): {len(short_samples)}")
    print(f"  Long ({LONG_MIN}-{VERY_LONG_MIN}s): {len(long_samples)}")
    print(f"  Very Long ({VERY_LONG_MIN}s+): {len(very_long_samples)}")
    
    return {
        'short': short_samples,
        'long': long_samples,
        'very_long': very_long_samples
    }

def extract_audio_segment(audio, start_time, end_time):
    """Extract audio segment in milliseconds."""
    start_ms = int(start_time * 1000)
    end_ms = int(end_time * 1000)
    return audio[start_ms:end_ms]

def save_samples(audio, categorized, output_dir):
    """Save categorized samples to disk with metadata."""
    print("\nSaving audio samples...")
    
    # Create output directories
    for category in ['short', 'long', 'very_long']:
        cat_dir = os.path.join(output_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
    
    # Save metadata file
    metadata_lines = []
    total_saved = 0
    
    for category, samples in categorized.items():
        print(f"\nProcessing {category} samples...")
        cat_dir = os.path.join(output_dir, category)
        
        for idx, sample in enumerate(samples, 1):
            # Create filename
            text_clean = clean_text(sample['text'])
            filename = f"{category}_{idx:03d}_{text_clean}.wav"
            filepath = os.path.join(cat_dir, filename)
            
            # Extract audio
            try:
                audio_segment = extract_audio_segment(
                    audio, 
                    sample['start_time'], 
                    sample['end_time']
                )
                
                # Export as WAV (already 22050 Hz mono from Step 1)
                audio_segment.export(filepath, format='wav')
                
                # Add to metadata
                relative_path = os.path.join(category, filename)
                metadata_lines.append(f"{relative_path}|{sample['text']}|vago\n")
                
                total_saved += 1
                
                if idx <= 3 or idx % 50 == 0:  # Show first 3 and every 50th
                    print(f"  ✓ Saved: {filename} ({sample['duration']:.1f}s)")
            
            except Exception as e:
                print(f"  ✗ Error saving {filename}: {e}")
    
    # Save metadata file
    metadata_path = os.path.join(output_dir, 'metadata.csv')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write('audio_file|text|speaker_name\n')
        f.writelines(metadata_lines)
    
    print(f"\n✓ Metadata saved to: {metadata_path}")
    print(f"✓ Total samples saved: {total_saved}")
    
    return total_saved

def generate_statistics(categorized):
    """Generate statistics about the extracted samples."""
    print("\n" + "="*60)
    print("EXTRACTION STATISTICS")
    print("="*60)
    
    total_samples = 0
    total_duration = 0
    
    for category, samples in categorized.items():
        cat_duration = sum(s['duration'] for s in samples)
        total_samples += len(samples)
        total_duration += cat_duration
        
        avg_duration = cat_duration / len(samples) if samples else 0
        
        print(f"\n{category.upper().replace('_', ' ')} SAMPLES:")
        print(f"  Count: {len(samples)}")
        print(f"  Total duration: {cat_duration:.1f}s ({cat_duration/60:.1f} min)")
        print(f"  Average duration: {avg_duration:.1f}s")
        if samples:
            print(f"  Min duration: {min(s['duration'] for s in samples):.1f}s")
            print(f"  Max duration: {max(s['duration'] for s in samples):.1f}s")
    
    print(f"\nTOTAL:")
    print(f"  Samples: {total_samples}")
    print(f"  Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Average: {total_duration/total_samples:.1f}s per sample")
    print("="*60)

def main():
    print("="*60)
    print("STEP 2: EXTRACT SENTENCES FOR FINE-TUNING")
    print("="*60)
    
    # Check if source files exist
    if not os.path.exists(SOURCE_AUDIO):
        print(f"ERROR: Audio file not found: {SOURCE_AUDIO}")
        print("Please run Step 1 first!")
        return
    
    if not os.path.exists(SOURCE_SEGMENTS):
        print(f"ERROR: Segments file not found: {SOURCE_SEGMENTS}")
        print("Please run Step 1 first!")
        return
    
    # Load segments
    segments = load_segments(SOURCE_SEGMENTS)
    
    # Extract all sentences
    sentences = extract_all_sentences(segments)
    
    # Categorize by length
    categorized = categorize_by_length(sentences)
    
    # Load audio file
    print(f"\nLoading clean audio: {SOURCE_AUDIO}")
    audio = AudioSegment.from_wav(SOURCE_AUDIO)
    print(f"✓ Audio loaded: {len(audio)/1000:.1f}s duration")
    
    # Save samples
    total_saved = save_samples(audio, categorized, OUTPUT_DIR)
    
    # Generate statistics
    generate_statistics(categorized)
    
    print(f"\n✅ All samples extracted to: {OUTPUT_DIR}")
    print(f"✅ Total: {total_saved} sentence samples")
    print(f"✅ Ready for XTTS fine-tuning!")
    print("="*60)

if __name__ == "__main__":
    main()
