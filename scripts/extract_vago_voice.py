"""
Extract István Vágó's voice (Speaker 0) from quiz show audio.
Splits into three categories: short, long, and question samples.
Each sample is word-boundary aware to avoid cutting words in half.
"""

import json
import os
from pydub import AudioSegment
import re

# Configuration
SOURCE_AUDIO = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav"
SOURCE_JSON = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav.json"
OUTPUT_DIR = "new_source_2/vago_samples"

# Sample length thresholds (in seconds)
SHORT_MAX = 5.0      # Short samples: up to 5 seconds
LONG_MIN = 5.0       # Long samples: 5+ seconds

def load_json_data(json_path):
    """Load the transcription JSON."""
    print(f"Loading JSON data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def is_question(text):
    """Determine if text is likely a question - must end with question mark."""
    # Only check for question mark at the END of the text
    text_clean = text.strip()
    return text_clean.endswith('?')

def clean_text(text):
    """Clean text for filename and metadata."""
    # Remove special characters, keep alphanumeric and Hungarian chars
    text = re.sub(r'[^\w\s\-áéíóöőúüűÁÉÍÓÖŐÚÜŰ]', '', text)
    # Replace spaces with underscores, limit length
    text = text.strip().replace(' ', '_')[:80]
    return text

def extract_speaker_segments(data, speaker_name="Speaker 0"):
    """Extract all segments for a specific speaker."""
    print(f"\nExtracting segments for {speaker_name}...")
    
    segments = []
    for segment in data.get('segments', []):
        if segment.get('speaker', {}).get('name') == speaker_name:
            text = segment.get('text', '').strip()
            start_time = segment.get('start_time', 0)
            end_time = segment.get('end_time', 0)
            duration = end_time - start_time
            
            # Skip very short segments (< 1 second)
            if duration < 1.0:
                continue
            
            # Skip non-speech segments (stage directions, etc.)
            if text.startswith('[') and text.endswith(']'):
                continue
            
            segments.append({
                'text': text,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'is_question': is_question(text)
            })
    
    print(f"Found {len(segments)} valid segments for {speaker_name}")
    return segments

def split_long_segment(segment, max_duration=10.0):
    """
    Split a long segment into smaller chunks at sentence boundaries.
    Ensures we don't cut words in half.
    """
    text = segment['text']
    duration = segment['duration']
    
    # If segment is short enough, return as is
    if duration <= max_duration:
        return [segment]
    
    # Try to split at sentence boundaries
    sentences = re.split(r'([.!?]\s+)', text)
    
    # Reconstruct sentences with punctuation
    full_sentences = []
    for i in range(0, len(sentences)-1, 2):
        if i+1 < len(sentences):
            full_sentences.append(sentences[i] + sentences[i+1])
        else:
            full_sentences.append(sentences[i])
    
    # If we couldn't split, try splitting at commas or conjunctions
    if len(full_sentences) <= 1:
        parts = re.split(r'(,\s+|\s+és\s+|\s+vagy\s+|\s+de\s+)', text)
        full_sentences = []
        for i in range(0, len(parts)-1, 2):
            if i+1 < len(parts):
                full_sentences.append(parts[i] + parts[i+1])
            else:
                full_sentences.append(parts[i])
    
    # Calculate approximate time per character
    time_per_char = duration / len(text)
    
    # Create sub-segments
    sub_segments = []
    char_offset = 0
    
    for sentence in full_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_duration = len(sentence) * time_per_char
        sub_start = segment['start_time'] + (char_offset * time_per_char)
        sub_end = sub_start + sentence_duration
        
        sub_segments.append({
            'text': sentence,
            'start_time': sub_start,
            'end_time': sub_end,
            'duration': sentence_duration,
            'is_question': is_question(sentence)
        })
        
        char_offset += len(sentence)
    
    return sub_segments if sub_segments else [segment]

def categorize_segments(segments, max_long_duration=10.0):
    """
    Categorize segments into short, long, and question.
    Split very long segments at sentence boundaries.
    """
    print("\nCategorizing segments...")
    
    short_samples = []
    long_samples = []
    question_samples = []
    
    for segment in segments:
        # Split if too long
        if segment['duration'] > max_long_duration:
            sub_segments = split_long_segment(segment, max_long_duration)
        else:
            sub_segments = [segment]
        
        for sub_seg in sub_segments:
            # Categorize as question first (priority)
            if sub_seg['is_question']:
                question_samples.append(sub_seg)
            # Then by duration
            elif sub_seg['duration'] <= SHORT_MAX:
                short_samples.append(sub_seg)
            else:
                long_samples.append(sub_seg)
    
    print(f"  Short samples (≤{SHORT_MAX}s): {len(short_samples)}")
    print(f"  Long samples (>{LONG_MIN}s): {len(long_samples)}")
    print(f"  Question samples: {len(question_samples)}")
    
    return {
        'short': short_samples,
        'long': long_samples,
        'question': question_samples
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
    for category in ['short', 'long', 'question']:
        cat_dir = os.path.join(output_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
    
    # Save metadata file
    metadata_lines = []
    
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
                
                # Export as WAV (22050 Hz mono for XTTS)
                audio_segment = audio_segment.set_frame_rate(22050).set_channels(1)
                audio_segment.export(filepath, format='wav')
                
                # Add to metadata
                relative_path = os.path.join(category, filename)
                metadata_lines.append(f"{relative_path}|{sample['text']}|vago\n")
                
                print(f"  ✓ Saved: {filename} ({sample['duration']:.1f}s)")
            
            except Exception as e:
                print(f"  ✗ Error saving {filename}: {e}")
    
    # Save metadata file
    metadata_path = os.path.join(output_dir, 'metadata.csv')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write('audio_file|text|speaker_name\n')
        f.writelines(metadata_lines)
    
    print(f"\n✓ Metadata saved to: {metadata_path}")
    print(f"  Total samples: {len(metadata_lines)}")

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
        
        print(f"\n{category.upper()} SAMPLES:")
        print(f"  Count: {len(samples)}")
        print(f"  Total duration: {cat_duration:.1f}s ({cat_duration/60:.1f} min)")
        print(f"  Average duration: {avg_duration:.1f}s")
        print(f"  Min duration: {min(s['duration'] for s in samples):.1f}s" if samples else "  N/A")
        print(f"  Max duration: {max(s['duration'] for s in samples):.1f}s" if samples else "  N/A")
    
    print(f"\nTOTAL:")
    print(f"  Samples: {total_samples}")
    print(f"  Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Average: {total_duration/total_samples:.1f}s per sample")
    print("="*60)

def main():
    print("="*60)
    print("EXTRACTING ISTVÁN VÁGÓ'S VOICE (SPEAKER 0)")
    print("="*60)
    
    # Check if source files exist
    if not os.path.exists(SOURCE_AUDIO):
        print(f"ERROR: Audio file not found: {SOURCE_AUDIO}")
        return
    
    if not os.path.exists(SOURCE_JSON):
        print(f"ERROR: JSON file not found: {SOURCE_JSON}")
        return
    
    # Load JSON data
    data = load_json_data(SOURCE_JSON)
    
    # Extract Speaker 0 segments
    segments = extract_speaker_segments(data, "Speaker 0")
    
    if not segments:
        print("ERROR: No segments found for Speaker 0!")
        return
    
    # Categorize segments
    categorized = categorize_segments(segments, max_long_duration=10.0)
    
    # Load audio file
    print(f"\nLoading audio file: {SOURCE_AUDIO}")
    audio = AudioSegment.from_wav(SOURCE_AUDIO)
    print(f"✓ Audio loaded: {len(audio)/1000:.1f}s duration")
    
    # Save samples
    save_samples(audio, categorized, OUTPUT_DIR)
    
    # Generate statistics
    generate_statistics(categorized)
    
    print(f"\n✓ All samples extracted to: {OUTPUT_DIR}")
    print(f"✓ Ready for fine-tuning!")

if __name__ == "__main__":
    main()
