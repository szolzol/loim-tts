"""
Convert Phase 4 Training Checkpoint to Inference Format
========================================================
Converts training checkpoint with gpt.gpt_inference.* keys to 
inference format with gpt.gpt.* keys

Usage:
  python convert_phase4_checkpoint.py
"""

import torch
from pathlib import Path
import sys

# Configuration
PROJECT_ROOT = Path("i:/CODE/tts-2")
TRAINING_DIR = PROJECT_ROOT / "run" / "training_phase4_continuation" / "XTTS_Phase4_Continuation-October-09-2025_07+54PM-f634425"
INPUT_CHECKPOINT = TRAINING_DIR / "best_model_2735.pth"
OUTPUT_CHECKPOINT = TRAINING_DIR / "best_model_2735_inference.pth"

def convert_checkpoint(input_path, output_path):
    """
    Convert training checkpoint to inference format by renaming keys
    
    Training format: gpt.gpt_inference.transformer.* 
    Inference format: gpt.gpt.*
    """
    
    print("=" * 80)
    print("PHASE 4 CHECKPOINT CONVERSION")
    print("=" * 80)
    print()
    print(f"Input:  {input_path.name}")
    print(f"Output: {output_path.name}")
    print()
    
    # Check input file
    if not input_path.exists():
        print(f"❌ Error: Input checkpoint not found: {input_path}")
        return False
    
    file_size_gb = input_path.stat().st_size / (1024**3)
    print(f"📁 Input file size: {file_size_gb:.2f} GB")
    print()
    
    # Load checkpoint
    print("⏳ Loading training checkpoint...")
    try:
        checkpoint = torch.load(input_path, map_location="cpu")
    except Exception as e:
        print(f"❌ Error loading checkpoint: {e}")
        return False
    
    print("✅ Checkpoint loaded")
    print()
    
    # Analyze structure
    print("📊 Checkpoint structure:")
    if isinstance(checkpoint, dict):
        print(f"  Keys: {list(checkpoint.keys())}")
        if "model" in checkpoint:
            state_dict = checkpoint["model"]
            print(f"  Model keys count: {len(state_dict)}")
        else:
            state_dict = checkpoint
            print(f"  State dict keys count: {len(state_dict)}")
    else:
        print("  ⚠️ Unexpected checkpoint format (not a dict)")
        return False
    
    print()
    
    # Sample original keys
    sample_keys = list(state_dict.keys())[:5]
    print("🔍 Sample original keys:")
    for key in sample_keys:
        print(f"  {key}")
    print()
    
    # Convert keys
    print("🔄 Converting keys...")
    converted_state_dict = {}
    conversion_count = 0
    unchanged_count = 0
    
    for key, value in state_dict.items():
        # Check if key needs conversion
        if "gpt.gpt_inference." in key:
            # Convert: gpt.gpt_inference.transformer.* -> gpt.gpt.*
            new_key = key.replace("gpt.gpt_inference.transformer.", "gpt.gpt.")
            converted_state_dict[new_key] = value
            conversion_count += 1
        else:
            # Keep unchanged
            converted_state_dict[key] = value
            unchanged_count += 1
    
    print(f"  ✅ Converted: {conversion_count} keys")
    print(f"  ✅ Unchanged: {unchanged_count} keys")
    print(f"  ✅ Total: {len(converted_state_dict)} keys")
    print()
    
    # Sample converted keys
    print("🔍 Sample converted keys:")
    converted_sample = [k for k in converted_state_dict.keys() if k.startswith("gpt.gpt.")][:5]
    for key in converted_sample:
        print(f"  {key}")
    print()
    
    # Prepare output checkpoint
    if isinstance(checkpoint, dict) and "model" in checkpoint:
        # Preserve checkpoint structure with metadata
        output_checkpoint = checkpoint.copy()
        output_checkpoint["model"] = converted_state_dict
        print("📦 Preserving checkpoint metadata (optimizer, config, etc.)")
    else:
        # Just the state dict
        output_checkpoint = converted_state_dict
        print("📦 Saving as state dict only")
    
    print()
    
    # Save converted checkpoint
    print("💾 Saving converted checkpoint...")
    try:
        torch.save(output_checkpoint, output_path)
    except Exception as e:
        print(f"❌ Error saving checkpoint: {e}")
        return False
    
    print("✅ Checkpoint saved")
    print()
    
    # Verify output
    output_size_gb = output_path.stat().st_size / (1024**3)
    print(f"📁 Output file size: {output_size_gb:.2f} GB")
    print()
    
    # Size check
    size_diff = abs(output_size_gb - file_size_gb)
    if size_diff > 0.1:  # Allow 100MB difference
        print(f"⚠️ Warning: Size difference is {size_diff:.2f} GB")
    else:
        print(f"✅ Size check passed (diff: {size_diff:.3f} GB)")
    
    print()
    print("=" * 80)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Update generate_questions_and_answers.py to use:")
    print(f"   MODEL_PATH = MODEL_DIR / \"{output_path.name}\"")
    print("2. Test inference with the converted checkpoint")
    print("3. Compare quality with Phase 2 baseline")
    print()
    
    return True

def verify_conversion(checkpoint_path):
    """
    Verify the converted checkpoint has correct key format
    """
    print("🔍 Verifying converted checkpoint...")
    
    try:
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        if isinstance(checkpoint, dict) and "model" in checkpoint:
            state_dict = checkpoint["model"]
        else:
            state_dict = checkpoint
        
        # Check for inference format keys
        gpt_keys = [k for k in state_dict.keys() if k.startswith("gpt.gpt.")]
        inference_keys = [k for k in state_dict.keys() if "gpt_inference" in k]
        
        print(f"  Found {len(gpt_keys)} keys with 'gpt.gpt.' prefix ✅")
        print(f"  Found {len(inference_keys)} keys with 'gpt_inference' ⚠️")
        
        if len(gpt_keys) > 0 and len(inference_keys) == 0:
            print("  ✅ Conversion successful - checkpoint is in inference format")
            return True
        else:
            print("  ❌ Conversion may have issues")
            return False
            
    except Exception as e:
        print(f"  ❌ Error verifying: {e}")
        return False

def main():
    print()
    
    # Check if output already exists
    if OUTPUT_CHECKPOINT.exists():
        print(f"⚠️ Output file already exists: {OUTPUT_CHECKPOINT.name}")
        response = input("Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Conversion cancelled")
            return
        print()
    
    # Convert
    success = convert_checkpoint(INPUT_CHECKPOINT, OUTPUT_CHECKPOINT)
    
    if not success:
        print("❌ Conversion failed")
        sys.exit(1)
    
    # Verify
    verify_conversion(OUTPUT_CHECKPOINT)
    
    print()
    print("🎉 All done! Ready to test Phase 4 model.")
    print()

if __name__ == "__main__":
    main()
