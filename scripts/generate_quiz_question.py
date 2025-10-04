"""
Generate a quiz question with A, B, C, D answers using the fine-tuned XTTS-v2 model
"""
import os
import sys
from pathlib import Path
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Paths
MODEL_DIR = Path("run/training_milliomos/XTTS_20251002_2323-October-02-2025_11+23PM-06571a9")
REFERENCE_AUDIO = Path("dataset_milliomos/question/question_003.wav")
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Quiz question content
QUIZ_DATA = {
    "question": "Melyik városban található a világhírű Eiffel-torony?",
    "answers": {
        "A": "London",
        "B": "Párizs",
        "C": "Berlin",
        "D": "Róma"
    },
    "answer_pronunciations": {
        "A": "Á: London",
        "B": "Bé: Párizs",
        "C": "Cé: Berlin",
        "D": "Dé: Róma"
    },
    "correct": "B"
}

print("🎯 Generating Quiz Question with Answers")
print("=" * 60)
print()

# Load model
print("Loading XTTS-v2 model...")
config = XttsConfig()
config.load_json(str(MODEL_DIR / "config.json"))
model = Xtts.init_from_config(config)
model.load_checkpoint(
    config,
    checkpoint_dir=str(MODEL_DIR),
    checkpoint_path=str(MODEL_DIR / "best_model.pth"),
    eval=True,
    use_deepspeed=False
)

if torch.cuda.is_available():
    model.cuda()
    print("Model loaded on GPU.")
else:
    print("Model loaded on CPU.")

print()

# Get conditioning latents
print(f"Using reference audio: {REFERENCE_AUDIO.name}")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
    audio_path=[str(REFERENCE_AUDIO)]
)

print()
print("📝 Quiz Question:")
print(f"   {QUIZ_DATA['question']}")
print()

# Generate question audio
print("🎙️  Generating question audio...")
question_text = QUIZ_DATA['question']
outputs = model.inference(
    question_text,
    language="hu",
    gpt_cond_latent=gpt_cond_latent,
    speaker_embedding=speaker_embedding,
    temperature=0.65,
    repetition_penalty=3.5,
)

# Extract and save question
if isinstance(outputs, dict):
    wav = outputs.get("wav", outputs)
else:
    wav = outputs

if not torch.is_tensor(wav):
    wav = torch.tensor(wav)

wav = wav.squeeze().cpu()
if wav.dim() == 1:
    wav = wav.unsqueeze(0)

question_path = OUTPUT_DIR / "quiz_question.wav"
torchaudio.save(str(question_path), wav, 24000)
print(f"✅ Saved: {question_path.name}")
print()

# Generate answer options
print("🎙️  Generating answer options...")
for letter, answer in QUIZ_DATA['answers'].items():
    print(f"   {letter}. {answer}")
    
    # Use Hungarian pronunciation for letters (e.g., "Á: London" instead of "A. London")
    answer_text = QUIZ_DATA['answer_pronunciations'][letter]
    
    outputs = model.inference(
        answer_text,
        language="hu",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.65,
        repetition_penalty=3.5,
    )
    
    # Extract and save answer
    if isinstance(outputs, dict):
        wav = outputs.get("wav", outputs)
    else:
        wav = outputs
    
    if not torch.is_tensor(wav):
        wav = torch.tensor(wav)
    
    wav = wav.squeeze().cpu()
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    
    answer_path = OUTPUT_DIR / f"quiz_answer_{letter}.wav"
    torchaudio.save(str(answer_path), wav, 24000)
    print(f"   ✅ Saved: {answer_path.name}")

print()
print("=" * 60)
print("🎉 Quiz generation complete!")
print()
print("📁 Output files:")
print(f"   Question: {OUTPUT_DIR}/quiz_question.wav")
print(f"   Answer A: {OUTPUT_DIR}/quiz_answer_A.wav")
print(f"   Answer B: {OUTPUT_DIR}/quiz_answer_B.wav")
print(f"   Answer C: {OUTPUT_DIR}/quiz_answer_C.wav")
print(f"   Answer D: {OUTPUT_DIR}/quiz_answer_D.wav")
print()
print(f"✅ Correct answer: {QUIZ_DATA['correct']}. {QUIZ_DATA['answers'][QUIZ_DATA['correct']]}")
print()
print("💡 To create your own quiz question, edit the QUIZ_DATA dictionary in this script!")
