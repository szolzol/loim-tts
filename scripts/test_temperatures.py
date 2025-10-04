"""
Temperature Testing Script
Test different temperature values to find the best prosody/stress
"""

import torch
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torchaudio
import os

# Model configuration
MODEL_DIR = Path("run/training_combined_phase2/XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd")
OUTPUT_DIR = Path("temperature_tests")
OUTPUT_DIR.mkdir(exist_ok=True)

# Test sentences focusing on prosody issues
TEST_SENTENCES = [
    # Questions (should have rising intonation)
    ("question_1", "Biztos benne, hogy ez a helyes válasz?"),
    ("question_2", "Szeretne segítséget kérni?"),
    ("question_3", "Mennyi ideje készül erre a kérdésre?"),
    
    # Exclamations (should have strong stress)
    ("excited_1", "Helyes válasz! Gratulálok!"),
    ("excited_2", "Óriási! Megvan a millió forint!"),
    ("excited_3", "Bravó! Fantasztikus teljesítmény!"),
    
    # Tension/Drama (should have varied rhythm)
    ("tension_1", "Ez az utolsó kérdés. Minden múlik ezen."),
    ("tension_2", "Harminc másodperc van hátra. Döntsön!"),
    ("tension_3", "Ez most a milliós kérdés. Nagyon figyeljen!"),
    
    # Neutral (baseline)
    ("neutral_1", "A következő kérdés tízezer forintért szól."),
    ("neutral_2", "Válasszon a négy lehetőség közül."),
]

# Temperature values to test
TEMPERATURES = [0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

def load_model():
    """Load the Phase 2 best model"""
    print("🔄 Loading model...")
    
    config = XttsConfig()
    config.load_json(str(MODEL_DIR / "config.json"))
    
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=str(MODEL_DIR),
        checkpoint_path=str(MODEL_DIR / "best_model_1901.pth"),
        vocab_path=str(MODEL_DIR / "vocab.json"),
        eval=True,
        use_deepspeed=False
    )
    
    model.cuda()
    print("✅ Model loaded successfully!")
    
    return model, config

def generate_sample(model, text, temperature, output_path, reference_audio="processed_clips/vago_vagott_01.wav"):
    """Generate a single sample with specified temperature"""
    
    # Get conditioning latents
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=[reference_audio]
    )
    
    # Generate
    outputs = model.inference(
        text=text,
        language="hu",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=temperature,
        length_penalty=1.0,
        repetition_penalty=2.0,
    )
    
    # Save
    torchaudio.save(
        str(output_path),
        outputs["wav"].squeeze().unsqueeze(0).cpu(),
        24000,
    )

def main():
    print("=" * 60)
    print("🎯 Temperature Testing for Prosody Improvement")
    print("=" * 60)
    print()
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🎤 Test sentences: {len(TEST_SENTENCES)}")
    print(f"🌡️  Temperature values: {TEMPERATURES}")
    print(f"📊 Total samples: {len(TEST_SENTENCES) * len(TEMPERATURES)}")
    print()
    
    # Load model
    model, config = load_model()
    print()
    
    # Generate samples
    total = len(TEST_SENTENCES) * len(TEMPERATURES)
    current = 0
    
    for name, text in TEST_SENTENCES:
        print(f"\n📝 Sentence: {name}")
        print(f"   Text: {text}")
        
        for temp in TEMPERATURES:
            current += 1
            output_file = OUTPUT_DIR / f"{name}_temp{temp:.2f}.wav"
            
            print(f"   🌡️  Temperature {temp:.2f} ({current}/{total})... ", end="")
            
            try:
                generate_sample(model, text, temp, output_file)
                size_kb = output_file.stat().st_size / 1024
                print(f"✅ ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("✅ ALL SAMPLES GENERATED!")
    print("=" * 60)
    print()
    print("📊 Evaluation Guide:")
    print("   Listen to each sentence with different temperatures")
    print("   Rate the prosody/stress naturalness (1-10)")
    print("   Find the best temperature for each sentence type")
    print()
    print("🎯 Expected Results:")
    print("   • 0.65-0.70: Safe, but may be monotone")
    print("   • 0.75-0.80: Balanced, recommended")
    print("   • 0.85-0.90: Expressive, but may be unstable")
    print()
    print(f"📁 All samples saved to: {OUTPUT_DIR.absolute()}")
    print()
    
    # Create a summary CSV
    summary_path = OUTPUT_DIR / "EVALUATION_TEMPLATE.csv"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Sentence,Text,Temperature,Naturalness(1-10),Stress_Quality,Notes\n")
        for name, text in TEST_SENTENCES:
            for temp in TEMPERATURES:
                f.write(f'{name},"{text}",{temp:.2f},,,\n')
    
    print(f"📋 Evaluation template created: {summary_path}")
    print("   Fill in the ratings after listening!")
    print()

if __name__ == "__main__":
    main()
