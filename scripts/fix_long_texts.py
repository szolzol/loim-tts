"""
Fix texts that exceed 224 character limit for Hungarian
"""

import re

def smart_truncate(text, max_length=224):
    """Truncate text at sentence boundary"""
    if len(text) <= max_length:
        return text
    
    # Try to cut at sentence end
    truncated = text[:max_length]
    
    # Look for sentence endings
    sentence_ends = ['.', '!', '?']
    last_end = -1
    for end_char in sentence_ends:
        pos = truncated.rfind(end_char)
        if pos > last_end:
            last_end = pos
    
    if last_end > max_length * 0.6:  # At least 60% of target length
        return text[:last_end + 1].strip()
    
    # Otherwise, cut at last space
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.7:
        return text[:last_space].strip()
    
    # Last resort: hard cut
    return text[:max_length].strip()


def fix_metadata():
    """Fix all long texts in metadata.csv"""
    input_file = 'dataset_milliomos/metadata.csv'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = lines[0]
    data_lines = lines[1:]
    
    fixed_count = 0
    fixed_lines = [header]
    
    for i, line in enumerate(data_lines, 1):
        parts = line.strip().split('|')
        if len(parts) != 3:
            fixed_lines.append(line)
            continue
        
        audio_file, text, speaker = parts
        
        if len(text) > 224:
            original_len = len(text)
            text = smart_truncate(text, 224)
            new_len = len(text)
            print(f"Line {i}: {audio_file}")
            print(f"  {original_len} → {new_len} chars")
            print(f"  Text: {text[:80]}...")
            print()
            fixed_count += 1
        
        fixed_lines.append(f"{audio_file}|{text}|{speaker}\n")
    
    # Write back
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"\n✅ Fixed {fixed_count} texts")
    print(f"✅ All texts now ≤ 224 characters")
    
    # Verify
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]
    
    max_len = max(len(line.split('|')[1]) for line in lines)
    over_limit = sum(1 for line in lines if len(line.split('|')[1]) > 224)
    
    print(f"\nVerification:")
    print(f"  Max length: {max_len}")
    print(f"  Over 224 chars: {over_limit}")
    

if __name__ == "__main__":
    fix_metadata()
