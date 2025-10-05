"""
Step 1: Create a clean audio file containing ONLY István Vágó's voice.
Removes all silences, other speakers, and stage directions.
Output: Single continuous audio file with just Vágó speaking.
"""

import json
import os
from pydub import AudioSegment

# Configuration
SOURCE_AUDIO = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav"
SOURCE_JSON = "new_source_2/1_Legyen Ön Is Milliomos! (21) - egy újabb rész 2001-ből_(Vocals).wav.json"
OUTPUT_AUDIO = "new_source_2/vago_only.wav"
OUTPUT_SEGMENTS_JSON = "new_source_2/vago_only_segments.json"

def load_json_data(json_path):
    """Load the transcription JSON."""
    print(f"Loading JSON data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_vago_segments(data, speaker_name="Speaker 0"):
    """Extract all Speaker 0 segments with timestamps."""
    print(f"\nExtracting {speaker_name} segments...")
    
    segments = []
    
    for segment in data.get('segments', []):
        if segment.get('speaker', {}).get('name') != speaker_name:
            continue
        
        text = segment.get('text', '').strip()
        start_time = segment.get('start_time', 0)
        end_time = segment.get('end_time', 0)
        duration = end_time - start_time
        
        # Skip very short segments (< 0.5 second) - likely noise
        if duration < 0.5:
            print(f"  ⊗ Skipped (too short): {duration:.1f}s")
            continue
        
        # Skip non-speech segments (stage directions, etc.)
        if text.startswith('[') and text.endswith(']'):
            print(f"  ⊗ Skipped (stage direction): {text[:50]}...")
            continue
        
        segments.append({
            'text': text,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration
        })
    
    print(f"\n✓ Found {len(segments)} valid Vágó segments")
    print(f"✓ Total duration: {sum(s['duration'] for s in segments):.1f}s ({sum(s['duration'] for s in segments)/60:.1f} min)")
    
    return segments

def concatenate_audio_segments(audio, segments):
    """
    Concatenate all Vágó segments into one continuous audio file.
    Removes silences between segments.
    """
    print("\nConcatenating audio segments...")
    
    combined = AudioSegment.empty()
    
    for idx, segment in enumerate(segments, 1):
        # Extract segment from source audio
        start_ms = int(segment['start_time'] * 1000)
        end_ms = int(segment['end_time'] * 1000)
        
        audio_segment = audio[start_ms:end_ms]
        
        # Add to combined audio
        combined += audio_segment
        
        if idx % 20 == 0:
            print(f"  Processed {idx}/{len(segments)} segments...")
    
    print(f"\n✓ Combined audio length: {len(combined)/1000:.1f}s ({len(combined)/60000:.1f} min)")
    
    return combined

def create_segment_map(segments):
    """
    Create a mapping of new timestamps to original text.
    Useful for later sentence extraction.
    """
    print("\nCreating segment map...")
    
    segment_map = []
    current_time = 0.0
    
    for segment in segments:
        new_segment = {
            'text': segment['text'],
            'original_start': segment['start_time'],
            'original_end': segment['end_time'],
            'new_start': current_time,
            'new_end': current_time + segment['duration'],
            'duration': segment['duration']
        }
        
        segment_map.append(new_segment)
        current_time += segment['duration']
    
    return segment_map

def save_segment_map(segment_map, output_path):
    """Save the segment map to JSON for reference."""
    print(f"\nSaving segment map to {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_segments': len(segment_map),
            'total_duration': segment_map[-1]['new_end'] if segment_map else 0,
            'segments': segment_map
        }, f, ensure_ascii=False, indent=2)
    
    print("✓ Segment map saved")

def main():
    print("="*60)
    print("STEP 1: EXTRACT CLEAN VÁGÓ-ONLY AUDIO")
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
    
    # Extract Vágó's segments
    segments = extract_vago_segments(data, "Speaker 0")
    
    if not segments:
        print("ERROR: No Vágó segments found!")
        return
    
    # Load audio file
    print(f"\nLoading audio file: {SOURCE_AUDIO}")
    audio = AudioSegment.from_wav(SOURCE_AUDIO)
    print(f"✓ Source audio loaded: {len(audio)/1000:.1f}s duration")
    
    # Concatenate all Vágó segments
    combined_audio = concatenate_audio_segments(audio, segments)
    
    # Create segment map for reference
    segment_map = create_segment_map(segments)
    
    # Export combined audio (22050 Hz mono for XTTS)
    print(f"\nExporting clean audio to {OUTPUT_AUDIO}...")
    combined_audio = combined_audio.set_frame_rate(22050).set_channels(1)
    combined_audio.export(OUTPUT_AUDIO, format='wav')
    print("✓ Audio exported successfully")
    
    # Save segment map
    save_segment_map(segment_map, OUTPUT_SEGMENTS_JSON)
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"\n📁 Output Files:")
    print(f"  Audio:    {OUTPUT_AUDIO}")
    print(f"  Segments: {OUTPUT_SEGMENTS_JSON}")
    
    print(f"\n📊 Statistics:")
    print(f"  Original audio:   {len(audio)/1000:.1f}s ({len(audio)/60000:.1f} min)")
    print(f"  Vágó segments:    {len(segments)}")
    print(f"  Clean audio:      {len(combined_audio)/1000:.1f}s ({len(combined_audio)/60000:.1f} min)")
    print(f"  Removed:          {(len(audio)-len(combined_audio))/1000:.1f}s ({(len(audio)-len(combined_audio))/60000:.1f} min)")
    print(f"  Compression:      {len(combined_audio)/len(audio)*100:.1f}% of original")
    
    print("\n✅ Ready for Step 2: Sentence extraction from clean audio")
    print("="*60)

if __name__ == "__main__":
    main()
