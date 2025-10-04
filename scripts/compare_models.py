"""
Compare Fine-tuned vs Zero-shot XTTS-v2 Model Quality
Analyzes quality, naturalness, and voice similarity
"""
import os
import sys
from pathlib import Path
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.api import TTS
import time

# Paths
FINETUNED_MODEL_DIR = Path("run/training_milliomos/XTTS_20251002_2323-October-02-2025_11+23PM-06571a9")
REFERENCE_AUDIO = Path("dataset_milliomos/greeting/greeting_001.wav")
OUTPUT_DIR = Path("comparison_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Test sentences covering different styles and phonetic patterns
TEST_SENTENCES = [
    {
        "category": "greeting",
        "text": "Jó estét kívánok, kedves nézők! Üdvözlöm Önöket a Legyen Ön is milliomos műsorában!",
        "description": "Greeting - warm, welcoming tone"
    },
    {
        "category": "question",
        "text": "Melyik magyar költő írta a Szeptember végén című verset?",
        "description": "Question - clear, neutral tone"
    },
    {
        "category": "tension",
        "text": "Ez most a tízmilliós kérdés! Biztos benne, hogy válaszolni szeretne?",
        "description": "High tension - dramatic, suspenseful"
    },
    {
        "category": "encouragement",
        "text": "Nagyon ügyes! Gratulálok, helyes a válasz! Folytatjuk tovább!",
        "description": "Encouragement - enthusiastic, positive"
    },
    {
        "category": "complex",
        "text": "A következő kérdésre három segítséget használhat: felezés, telefonos segítség, vagy közönség segítsége.",
        "description": "Complex sentence - informative, measured pace"
    }
]

print("🔬 Fine-tuned vs Zero-shot Model Comparison")
print("=" * 70)
print()

# Load fine-tuned model
print("📦 Loading fine-tuned model...")
print(f"   Path: {FINETUNED_MODEL_DIR}")
config = XttsConfig()
config.load_json(str(FINETUNED_MODEL_DIR / "config.json"))
finetuned_model = Xtts.init_from_config(config)
finetuned_model.load_checkpoint(
    config,
    checkpoint_dir=str(FINETUNED_MODEL_DIR),
    checkpoint_path=str(FINETUNED_MODEL_DIR / "best_model.pth"),
    eval=True,
    use_deepspeed=False
)

if torch.cuda.is_available():
    finetuned_model.cuda()
    print("   ✅ Fine-tuned model on GPU")
else:
    print("   ✅ Fine-tuned model on CPU")

print()

# Load zero-shot model
print("📦 Loading zero-shot XTTS-v2 model...")
try:
    zeroshot_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    if torch.cuda.is_available():
        zeroshot_tts = zeroshot_tts.to("cuda")
    print("   ✅ Zero-shot model loaded")
except Exception as e:
    print(f"   ❌ Failed to load zero-shot model: {e}")
    print("   Continuing with fine-tuned model only...")
    zeroshot_tts = None

print()
print("=" * 70)
print()

# Get conditioning latents for fine-tuned model
print(f"🎤 Reference audio: {REFERENCE_AUDIO.name}")
gpt_cond_latent, speaker_embedding = finetuned_model.get_conditioning_latents(
    audio_path=[str(REFERENCE_AUDIO)]
)

print()
print("🎬 Generating samples for comparison...")
print()

results = []

for i, test_case in enumerate(TEST_SENTENCES, 1):
    category = test_case["category"]
    text = test_case["text"]
    description = test_case["description"]
    
    print(f"[{i}/{len(TEST_SENTENCES)}] {category.upper()}")
    print(f"    {description}")
    print(f"    Text: {text[:60]}...")
    print()
    
    # Generate with fine-tuned model
    print("    🔧 Fine-tuned model...")
    start_time = time.time()
    
    outputs = finetuned_model.inference(
        text,
        language="hu",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.65,
        repetition_penalty=3.5,
    )
    
    if isinstance(outputs, dict):
        wav = outputs.get("wav", outputs)
    else:
        wav = outputs
    
    if not torch.is_tensor(wav):
        wav = torch.tensor(wav)
    
    wav = wav.squeeze().cpu()
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    
    finetuned_path = OUTPUT_DIR / f"{i:02d}_{category}_finetuned.wav"
    torchaudio.save(str(finetuned_path), wav, 24000)
    finetuned_time = time.time() - start_time
    finetuned_duration = wav.shape[1] / 24000
    
    print(f"       ✅ Generated in {finetuned_time:.2f}s (audio: {finetuned_duration:.2f}s)")
    
    # Generate with zero-shot model if available
    zeroshot_time = None
    zeroshot_duration = None
    
    if zeroshot_tts is not None:
        print("    🌐 Zero-shot model...")
        start_time = time.time()
        
        try:
            zeroshot_path = OUTPUT_DIR / f"{i:02d}_{category}_zeroshot.wav"
            zeroshot_tts.tts_to_file(
                text=text,
                speaker_wav=str(REFERENCE_AUDIO),
                language="hu",
                file_path=str(zeroshot_path)
            )
            
            zeroshot_time = time.time() - start_time
            # Load to get duration
            wav_zs, sr = torchaudio.load(str(zeroshot_path))
            zeroshot_duration = wav_zs.shape[1] / sr
            
            print(f"       ✅ Generated in {zeroshot_time:.2f}s (audio: {zeroshot_duration:.2f}s)")
        except Exception as e:
            print(f"       ❌ Failed: {e}")
    
    results.append({
        "category": category,
        "description": description,
        "text": text,
        "finetuned_time": finetuned_time,
        "finetuned_duration": finetuned_duration,
        "zeroshot_time": zeroshot_time,
        "zeroshot_duration": zeroshot_duration,
        "finetuned_path": finetuned_path,
        "zeroshot_path": OUTPUT_DIR / f"{i:02d}_{category}_zeroshot.wav" if zeroshot_tts else None
    })
    
    print()

print()
print("=" * 70)
print("📊 COMPARISON RESULTS")
print("=" * 70)
print()

# Summary statistics
total_finetuned_time = sum(r["finetuned_time"] for r in results)
total_finetuned_duration = sum(r["finetuned_duration"] for r in results)

print("🔧 FINE-TUNED MODEL:")
print(f"   Total generation time: {total_finetuned_time:.2f}s")
print(f"   Total audio duration: {total_finetuned_duration:.2f}s")
print(f"   Real-time factor: {total_finetuned_duration / total_finetuned_time:.2f}x")
print(f"   Average speed: {total_finetuned_time / len(results):.2f}s per sample")
print()

if zeroshot_tts is not None:
    total_zeroshot_time = sum(r["zeroshot_time"] for r in results if r["zeroshot_time"])
    total_zeroshot_duration = sum(r["zeroshot_duration"] for r in results if r["zeroshot_duration"])
    
    print("🌐 ZERO-SHOT MODEL:")
    print(f"   Total generation time: {total_zeroshot_time:.2f}s")
    print(f"   Total audio duration: {total_zeroshot_duration:.2f}s")
    print(f"   Real-time factor: {total_zeroshot_duration / total_zeroshot_time:.2f}x")
    print(f"   Average speed: {total_zeroshot_time / len(results):.2f}s per sample")
    print()
    
    print("⚡ SPEED COMPARISON:")
    speedup = total_zeroshot_time / total_finetuned_time
    if speedup > 1:
        print(f"   Fine-tuned is {speedup:.2f}x FASTER than zero-shot")
    else:
        print(f"   Zero-shot is {1/speedup:.2f}x FASTER than fine-tuned")
    print()

print("=" * 70)
print("📁 GENERATED FILES:")
print("=" * 70)
print()

for i, result in enumerate(results, 1):
    print(f"{i}. {result['category'].upper()} - {result['description']}")
    print(f"   Text: {result['text'][:60]}...")
    print(f"   Fine-tuned: {result['finetuned_path'].name}")
    if result['zeroshot_path'] and result['zeroshot_path'].exists():
        print(f"   Zero-shot:  {result['zeroshot_path'].name}")
    print()

print("=" * 70)
print("🎧 QUALITY ASSESSMENT GUIDE")
print("=" * 70)
print()
print("Listen to the generated samples and evaluate:")
print()
print("1. 🎯 VOICE SIMILARITY")
print("   - Does it sound like István Vágó?")
print("   - Voice timbre and characteristics")
print("   - Consistency across different styles")
print()
print("2. 🗣️  PRONUNCIATION")
print("   - Correct Hungarian pronunciation")
print("   - Natural word stress and intonation")
print("   - Clear articulation")
print()
print("3. 🎭 EMOTIONAL EXPRESSION")
print("   - Appropriate emotion for each category")
print("   - Greeting: warm and welcoming")
print("   - Question: neutral and clear")
print("   - Tension: dramatic and suspenseful")
print("   - Encouragement: enthusiastic and positive")
print()
print("4. 🎵 PROSODY & RHYTHM")
print("   - Natural speech rhythm")
print("   - Appropriate pauses")
print("   - Sentence melody (intonation)")
print()
print("5. 🔊 AUDIO QUALITY")
print("   - No artifacts or glitches")
print("   - Consistent volume")
print("   - Natural breathing patterns")
print()
print("=" * 70)
print("💡 EXPECTED RESULTS")
print("=" * 70)
print()
print("Fine-tuned model should show:")
print("  ✅ Better voice similarity to István Vágó")
print("  ✅ More consistent Hungarian pronunciation")
print("  ✅ Better emotional expression for quiz show context")
print("  ✅ More natural prosody and rhythm")
print("  ✅ Faster generation speed (model optimized for this voice)")
print()
print("Zero-shot model may show:")
print("  ⚠️  Less accurate voice replication")
print("  ⚠️  Generic emotional expression")
print("  ⚠️  Less consistent pronunciation")
print("  ⚠️  Slower generation (not optimized)")
print("  ✅ Still intelligible and clear")
print()
print("🎉 Comparison complete!")
print(f"📁 All files saved to: {OUTPUT_DIR}")
print()
