# Phase 4 Model Deployment Issue - RESOLVED PLAN

## 🚨 Issue Discovered

**Problem:** Phase 4 checkpoint cannot be loaded by inference scripts  
**Date:** October 9, 2025  
**Status:** ⚠️ REQUIRES CONVERSION SCRIPT

### Error Details

```
RuntimeError: Error(s) in loading state_dict for Xtts:
        Missing key(s) in state_dict:
        "gpt.gpt.wte.weight",
        "gpt.gpt_inference.transformer.h.0.ln_1.weight",
        ...
```

### Root Cause

The training checkpoint (`best_model_2735.pth`) has a **different state_dict structure** than what the inference `Xtts` model expects:

**Training Checkpoint Keys:**

- `gpt.gpt_inference.transformer.h.0.ln_1.weight`
- `gpt.gpt_inference.transformer.h.0.attn.c_attn.weight`
- ... (all keys have `gpt_inference` prefix)

**Inference Expected Keys:**

- `gpt.gpt.wte.weight`
- `gpt.gpt.transformer.h.0.ln_1.weight`
- ... (keys have `gpt.gpt` prefix, NOT `gpt.gpt_inference`)

This happens because:

1. **Training** uses `GPTTrainer` which wraps the model in a `gpt_inference` container for training-specific functionality
2. **Inference** uses raw `Xtts` model which expects the base GPT structure

---

## ✅ Solution Options

### Option 1: Convert Checkpoint Format (Recommended) ⭐

Create a conversion script that:

1. Loads Phase 4 checkpoint
2. Renames all keys from `gpt.gpt_inference.*` → `gpt.gpt.*`
3. Saves as a new inference-compatible checkpoint

**Pros:**

- Clean separation of training/inference formats
- No modification to existing scripts
- Can be reused for future training

**Cons:**

- Requires additional conversion step

**Script to create:** `scripts/convert_training_to_inference_checkpoint.py`

### Option 2: Modify Inference Script

Update `generate_questions_and_answers.py` to:

1. Load raw checkpoint
2. Manually extract and rename keys
3. Load into model

**Pros:**

- One-time fix in inference script

**Cons:**

- Makes inference code more complex
- Every inference script needs modification

### Option 3: Export from Training Script

Modify `train_phase4_continuation.py` to:

1. Save an additional inference-compatible checkpoint
2. Strip training-specific wrappers before saving

**Pros:**

- Automatic inference-ready checkpoints

**Cons:**

- Requires re-training or loading/resaving
- Doubles storage requirements

---

## 🎯 Recommended Approach: Option 1 (Conversion Script)

### Implementation Plan

**Step 1: Create Conversion Script**

```python
# scripts/convert_training_to_inference_checkpoint.py

import torch
from pathlib import Path

def convert_checkpoint(training_checkpoint_path, output_path):
    """
    Convert training checkpoint to inference-compatible format

    Changes:
    - gpt.gpt_inference.* → gpt.gpt.*
    - Preserves all other keys (hifigan, dvae, etc.)
    """
    print(f"Loading training checkpoint: {training_checkpoint_path}")
    checkpoint = torch.load(training_checkpoint_path, map_location='cpu')

    # Create new state dict with renamed keys
    new_state_dict = {}

    for key, value in checkpoint.items():
        if key.startswith('gpt.gpt_inference.'):
            # Rename: gpt.gpt_inference.* → gpt.gpt.*
            new_key = key.replace('gpt.gpt_inference.', 'gpt.gpt.')
            new_state_dict[new_key] = value
            print(f"Renamed: {key} → {new_key}")
        else:
            # Keep other keys unchanged
            new_state_dict[key] = value

    # Save inference-compatible checkpoint
    print(f"\nSaving inference checkpoint: {output_path}")
    torch.save(new_state_dict, output_path)
    print("✅ Conversion complete!")

    return new_state_dict

if __name__ == "__main__":
    training_checkpoint = Path("run/training_phase4_continuation/XTTS_Phase4_Continuation-October-09-2025_07+54PM-f634425/best_model_2735.pth")
    output_checkpoint = Path("run/training_phase4_continuation/XTTS_Phase4_Continuation-October-09-2025_07+54PM-f634425/best_model_2735_inference.pth")

    convert_checkpoint(training_checkpoint, output_checkpoint)
```

**Step 2: Run Conversion**

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/convert_training_to_inference_checkpoint.py
```

**Step 3: Update Inference Script**

```python
# scripts/generate_questions_and_answers.py

MODEL_DIR = PROJECT_ROOT / "run" / "training_phase4_continuation" / "XTTS_Phase4_Continuation-October-09-2025_07+54PM-f634425"
MODEL_PATH = MODEL_DIR / "best_model_2735_inference.pth"  # ← Use converted model
```

**Step 4: Test Generation**

```powershell
I:/CODE/tts-2/.conda/python.exe scripts/generate_questions_and_answers.py 4 2
```

---

## 📋 Action Items

- [ ] Create `scripts/convert_training_to_inference_checkpoint.py`
- [ ] Run conversion on `best_model_2735.pth`
- [ ] Verify converted checkpoint size (~5.22 GB, same as original)
- [ ] Test inference with converted checkpoint
- [ ] Generate comparison samples (Phase 2 vs Phase 4)
- [ ] Document conversion process in README.md
- [ ] Add conversion step to training workflow

---

## 🔍 Why This Happened

This is a **known Coqui TTS behavior**:

1. **Training Mode:** The `GPTTrainer` class wraps the model in a training-specific structure for:

   - Gradient accumulation
   - Distributed training support
   - Evaluation mode switching
   - Loss calculation

2. **Inference Mode:** The raw `Xtts` model expects the base structure without training wrappers

3. **Solution:** Standard practice in deep learning to have separate checkpoint formats for training vs. inference (e.g., PyTorch `state_dict` vs TorchScript, ONNX export)

---

## 💡 Lessons Learned

1. **Always test inference immediately after training** to catch format issues early
2. **Export inference-ready checkpoints** during training (add to training script)
3. **Document checkpoint formats** for future reference
4. **Create conversion utilities** as part of training infrastructure

---

## 🎯 Current Status

**Phase 2 Model:** ✅ Working - Production ready  
**Phase 4 Model:** ⏸️ Trained successfully, pending conversion for inference use

**Temporary Solution:** Continue using Phase 2 (`best_model_1901.pth`) for inference  
**Permanent Solution:** Convert Phase 4 checkpoint and compare quality

---

_Issue documented: October 9, 2025_  
_Next action: Create conversion script_
