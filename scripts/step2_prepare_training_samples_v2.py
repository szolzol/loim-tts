"""
Step 2 (V2): Extract sentence samples with accurate word-level timing.
Uses original JSON with word timestamps to ensure perfect audio alignment.
"""

import json
import os
from pydub import AudioSegment
import re

# Configuration
SOURCE_AUDIO = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav"
SOURCE_JSON = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav.json"
OUTPUT_DIR = "new_source_2/vago_samples_final"

# Sample length thresholds (in seconds)
MIN_DURATION = 0.5   # Minimum sample length
SHORT_MAX = 5.0      # Short samples: 0.5-5 seconds
LONG_MIN = 5.0       # Long samples: 5-10 seconds
VERY_LONG_MIN = 10.0 # Very long: 10+ seconds

def load_json_data(json_path):
    """Load the original transcription JSON."""
    print(f"Loading JSON data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data['segments'])} segments")
    return data

def clean_text_for_filename(text):
    """Clean text for use in filename."""
    # Remove punctuation and special chars
    text = re.sub(r'[^\w\s\-áéíóöőúüűÁÉÍÓÖŐÚÜŰ]', '', text)
    # Replace spaces with underscores, limit length
    text = text.strip().replace(' ', '_')[:60]
    return text

def split_into_sentences(segment):
    """
    Split segment text into sentences using punctuation.
    Returns list of sentence info with word-level timing.
    """
    text = segment['text']
    words = segment['words']
    
    if not words:
        return []
    
    # Find sentence boundaries by punctuation
    sentences = []
    current_sentence_words = []
    current_sentence_text = ""
    
    for word in words:
        word_text = word['text']
        current_sentence_words.append(word)
        current_sentence_text += word_text
        
        # Check if this word ends a sentence
        if word_text.strip() and word_text.strip()[-1] in '.!?':
            # Complete sentence found
            if current_sentence_words:
                # Get actual timing from first and last word
                start_time = current_sentence_words[0]['start_time']
                end_time = current_sentence_words[-1]['end_time']
                duration = end_time - start_time
                
                # Clean up text
                sentence_text = current_sentence_text.strip()
                
                if duration >= MIN_DURATION and sentence_text:
                    sentences.append({
                        'text': sentence_text,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'words': current_sentence_words.copy()
                    })
                
                # Reset for next sentence
                current_sentence_words = []
                current_sentence_text = ""
    
    # Handle remaining words (sentence without ending punctuation)
    if current_sentence_words:
        start_time = current_sentence_words[0]['start_time']
        end_time = current_sentence_words[-1]['end_time']
        duration = end_time - start_time
        sentence_text = current_sentence_text.strip()
        
        if duration >= MIN_DURATION and sentence_text:
            sentences.append({
                'text': sentence_text,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'words': current_sentence_words.copy()
            })
    
    return sentences

def extract_vago_sentences(data):
    """Extract all sentences from Vágó (Speaker 0) segments."""
    print("\nExtracting Vágó sentences with word-level timing...")
    
    all_sentences = []
    speaker_0_segments = 0
    
    for segment in data['segments']:
        # Check if this is Speaker 0 (Vágó)
        if segment['speaker']['name'] != "Speaker 0":
            continue
        
        speaker_0_segments += 1
        
        # Skip stage directions
        text = segment['text'].strip()
        if text.startswith('[') and text.endswith(']'):
            continue
        
        # Split into sentences
        sentences = split_into_sentences(segment)
        all_sentences.extend(sentences)
    
    print(f"✓ Found {speaker_0_segments} Speaker 0 segments")
    print(f"✓ Extracted {len(all_sentences)} sentences")
    
    return all_sentences

def categorize_sentences(sentences):
    """Categorize sentences by duration."""
    print("\nCategorizing by length...")
    
    short_samples = []
    long_samples = []
    very_long_samples = []
    
    for sentence in sentences:
        duration = sentence['duration']
        
        if duration < SHORT_MAX:
            short_samples.append(sentence)
        elif duration < VERY_LONG_MIN:
            long_samples.append(sentence)
        else:
            very_long_samples.append(sentence)
    
    print(f"  Short ({MIN_DURATION}-{SHORT_MAX}s): {len(short_samples)}")
    print(f"  Long ({LONG_MIN}-{VERY_LONG_MIN}s): {len(long_samples)}")
    print(f"  Very Long ({VERY_LONG_MIN}s+): {len(very_long_samples)}")
    
    return {
        'short': short_samples,
        'long': long_samples,
        'very_long': very_long_samples
    }

def extract_audio_segment(audio, start_time, end_time):
    """Extract audio segment using precise millisecond timing."""
    start_ms = int(start_time * 1000)
    end_ms = int(end_time * 1000)
    segment = audio[start_ms:end_ms]
    
    # Ensure proper format for XTTS (22050 Hz, mono)
    segment = segment.set_frame_rate(22050).set_channels(1)
    
    return segment

def save_samples(audio, categorized, output_dir):
    """Save categorized samples with accurate audio extraction."""
    print("\nSaving audio samples with accurate timing...")
    
    # Create output directories
    for category in ['short', 'long', 'very_long']:
        cat_dir = os.path.join(output_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
    
    metadata_lines = []
    total_saved = 0
    
    for category, samples in categorized.items():
        print(f"\n{category.upper()} samples:")
        cat_dir = os.path.join(output_dir, category)
        
        for idx, sample in enumerate(samples, 1):
            # Create filename from actual text
            text_clean = clean_text_for_filename(sample['text'])
            filename = f"{category}_{idx:03d}_{text_clean}.wav"
            filepath = os.path.join(cat_dir, filename)
            
            try:
                # Extract audio with precise timing
                audio_segment = extract_audio_segment(
                    audio,
                    sample['start_time'],
                    sample['end_time']
                )
                
                # Export as WAV
                audio_segment.export(filepath, format='wav')
                
                # Add to metadata
                relative_path = os.path.join(category, filename)
                metadata_lines.append(f"{relative_path}|{sample['text']}|vago\n")
                
                total_saved += 1
                
                # Show progress
                if idx <= 3 or idx % 50 == 0:
                    print(f"  ✓ [{idx:3d}] {filename[:70]}... ({sample['duration']:.2f}s)")
            
            except Exception as e:
                print(f"  ✗ Error saving {filename}: {e}")
    
    # Save metadata file
    metadata_path = os.path.join(output_dir, 'metadata.csv')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write('audio_file|text|speaker_name\n')
        f.writelines(metadata_lines)
    
    print(f"\n✓ Metadata saved: {metadata_path}")
    print(f"✓ Total samples: {total_saved}")
    
    return total_saved

def generate_statistics(categorized):
    """Generate detailed statistics."""
    print("\n" + "="*60)
    print("EXTRACTION STATISTICS")
    print("="*60)
    
    total_samples = 0
    total_duration = 0
    
    for category, samples in categorized.items():
        if not samples:
            continue
        
        cat_duration = sum(s['duration'] for s in samples)
        total_samples += len(samples)
        total_duration += cat_duration
        
        avg_duration = cat_duration / len(samples)
        min_duration = min(s['duration'] for s in samples)
        max_duration = max(s['duration'] for s in samples)
        
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Count: {len(samples)}")
        print(f"  Total: {cat_duration:.1f}s ({cat_duration/60:.1f} min)")
        print(f"  Average: {avg_duration:.2f}s")
        print(f"  Range: {min_duration:.2f}s - {max_duration:.2f}s")
    
    print(f"\nOVERALL:")
    print(f"  Total samples: {total_samples}")
    print(f"  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Average duration: {total_duration/total_samples:.2f}s")
    print("="*60)

def main():
    print("="*60)
    print("STEP 2 V2: PREPARE TRAINING SAMPLES")
    print("Using word-level timing for perfect accuracy")
    print("="*60)
    
    # Check files exist
    if not os.path.exists(SOURCE_AUDIO):
        print(f"ERROR: Audio file not found: {SOURCE_AUDIO}")
        return
    
    if not os.path.exists(SOURCE_JSON):
        print(f"ERROR: JSON file not found: {SOURCE_JSON}")
        return
    
    # Load data
    data = load_json_data(SOURCE_JSON)
    
    # Extract sentences
    sentences = extract_vago_sentences(data)
    
    # Categorize by length
    categorized = categorize_sentences(sentences)
    
    # Load audio
    print(f"\nLoading audio: {SOURCE_AUDIO}")
    audio = AudioSegment.from_wav(SOURCE_AUDIO)
    print(f"✓ Audio loaded: {len(audio)/1000:.1f}s")
    
    # Save samples
    total_saved = save_samples(audio, categorized, OUTPUT_DIR)
    
    # Statistics
    generate_statistics(categorized)
    
    print(f"\n✅ SUCCESS!")
    print(f"✅ Extracted {total_saved} sentence samples")
    print(f"✅ Output directory: {OUTPUT_DIR}")
    print(f"✅ Ready for XTTS fine-tuning!")
    print("="*60)

if __name__ == "__main__":
    main()
