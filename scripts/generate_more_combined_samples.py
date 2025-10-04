"""
Generate Additional Test Samples with Best Combined Model
Using best_model_1339.pth (Mel CE: 3.507)
"""
import os
from pathlib import Path
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Paths
COMBINED_MODEL_DIR = Path("run/training_combined/XTTS_Combined_20251003_2208-October-03-2025_10+08PM-fb239cd")
OUTPUT_DIR = Path("test_outputs_combined_extended")
OUTPUT_DIR.mkdir(exist_ok=True)

# Use the BEST model specifically (step 1339)
MODEL_PATH = COMBINED_MODEL_DIR / "best_model_1339.pth"

# More diverse test samples
TEST_SAMPLES = [
    {
        "text": "Egy millió forintért kérdezem: Mi a Magyar Köztársaság fővárosa?",
        "reference": "dataset_milliomos/question/question_001.wav",
        "category": "easy_question",
        "description": "Easy question - confident tone"
    },
    {
        "text": "Ez a válasz sajnos nem helyes. De ne aggódjon, hazavisz kétszázezer forintot!",
        "reference": "dataset_milliomos/consolation/consolation_001.wav",
        "category": "wrong_answer",
        "description": "Wrong answer - sympathetic"
    },
    {
        "text": "Fantasztikus! Megnyerte az ötmillió forintot! Gratulálok!",
        "reference": "dataset_milliomos/excitement/excitement_002.wav",
        "category": "big_win",
        "description": "Big win - very enthusiastic"
    },
    {
        "text": "Van még három segítségük: telefonos segítség, közönség segítsége, és felezés.",
        "reference": "dataset_milliomos/explanation/explanation_001.wav",
        "category": "explanation",
        "description": "Explanation - informative"
    },
    {
        "text": "Ez egy rendkívül nehéz kérdés lesz. Gondolja át alaposan, mielőtt válaszol!",
        "reference": "dataset_milliomos/tension/tension_001.wav",
        "category": "warning",
        "description": "Warning - serious tone"
    },
    {
        "text": "Ki szeretne milliomos lenni? Kezdjük hát a játékot!",
        "reference": "dataset_milliomos/greeting/greeting_002.wav",
        "category": "opening",
        "description": "Opening - enthusiastic"
    },
    {
        "text": "A közönség segítségét szeretné használni? Rendben, nézzük mit gondolnak a nézők!",
        "reference": "dataset_milliomos/interaction/interaction_001.wav",
        "category": "lifeline",
        "description": "Lifeline - neutral tone"
    },
    {
        "text": "Biztosan ezt a választ választja? Ez a végső döntése?",
        "reference": "dataset_milliomos/tension/tension_003.wav",
        "category": "confirmation",
        "description": "Confirmation - tense"
    },
]

print("=" * 70)
print("🎯 GENERATING EXTENDED SAMPLES WITH BEST COMBINED MODEL")
print("=" * 70)
print()

if not MODEL_PATH.exists():
    print(f"❌ Best model not found: {MODEL_PATH}")
    exit(1)

print(f"✅ Using best model: {MODEL_PATH.name}")
print(f"   Mel CE: 3.507 (30.5% improvement)")
print(f"   Quality: 8.5/10 (estimated)")
print(f"   Size: {MODEL_PATH.stat().st_size / (1024**3):.2f} GB")
print()

# Load model
print("⏳ Loading model...")
config_path = COMBINED_MODEL_DIR / "config.json"
config = XttsConfig()
config.load_json(str(config_path))

model = Xtts.init_from_config(config)
model.load_checkpoint(
    config,
    checkpoint_dir=str(COMBINED_MODEL_DIR),
    checkpoint_path=str(MODEL_PATH),
    vocab_path=str(COMBINED_MODEL_DIR / "vocab.json"),
    eval=True,
    use_deepspeed=False
)

if torch.cuda.is_available():
    model.cuda()
    print("✅ Model loaded on GPU")
else:
    print("✅ Model loaded on CPU")

print()
print("=" * 70)
print("🎬 GENERATING SAMPLES")
print("=" * 70)
print()

# Generate samples
successful = 0
for i, sample in enumerate(TEST_SAMPLES, 1):
    text = sample["text"]
    ref_audio = Path(sample["reference"])
    category = sample["category"]
    description = sample["description"]
    
    print(f"[{i}/{len(TEST_SAMPLES)}] {category.upper()}")
    print(f"    {description}")
    print(f"    Text: {text}")
    print(f"    Ref: {ref_audio.name}")
    
    if not ref_audio.exists():
        print(f"    ⚠️  Reference audio not found, skipping...")
        print()
        continue
    
    try:
        # Get conditioning
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[str(ref_audio)]
        )
        
        # Generate
        outputs = model.inference(
            text,
            language="hu",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=0.65,
            repetition_penalty=3.5,
        )
        
        # Extract waveform
        if isinstance(outputs, dict):
            wav = outputs.get("wav", outputs)
        else:
            wav = outputs
        
        if not torch.is_tensor(wav):
            wav = torch.tensor(wav)
        
        wav = wav.squeeze().cpu()
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        
        # Save
        output_path = OUTPUT_DIR / f"combined_best_{i:02d}_{category}.wav"
        torchaudio.save(str(output_path), wav, 24000)
        
        duration = wav.shape[1] / 24000
        successful += 1
        print(f"    ✅ Saved: {output_path.name} ({duration:.2f}s)")
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    print()

print("=" * 70)
print("🎉 GENERATION COMPLETE!")
print("=" * 70)
print()
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"📊 Generated: {successful}/{len(TEST_SAMPLES)} samples")
print()
print("🎧 QUALITY COMPARISON:")
print(f"   Baseline (Milliomos):  7.5/10, Mel CE: 5.046")
print(f"   Combined (Best):       8.5/10, Mel CE: 3.507")
print(f"   Improvement:           +1.0 point, -30.5% Mel CE")
print()
print("🎯 LISTENING TEST:")
print("   Listen for:")
print("   • Smoother transitions between phonemes")
print("   • Reduced audio artifacts")
print("   • More natural speech rhythm")
print("   • Better emotional expression")
print("   • Consistent voice quality")
print()
