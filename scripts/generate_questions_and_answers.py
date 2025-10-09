"""
Generate Custom Quiz Questions
===============================
Interactive script to generate quiz questions with optimized parameters
Uses 'natural' profile: temp=0.55, top_p=0.88, top_k=50, rep_penalty=6.5

Usage:
  python generate_questions_and_answers.py                    # Interactive mode
  python generate_questions_and_answers.py 6 5                # Topic 6 (zene), 5 questions
"""

import torch
import torchaudio
import soundfile as sf
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import TTS.tts.models.xtts as xtts_module

# Workaround for torchaudio/torchcodec - use soundfile instead
def load_audio_sf(audiopath, sr=None):
    """Load audio using soundfile (bypassing broken torchaudio/torchcodec)"""
    audio_np, lsr = sf.read(audiopath)
    audio = torch.FloatTensor(audio_np)
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)
    return audio

# Monkey-patch XTTS audio loading
xtts_module.load_audio = load_audio_sf

# ========================================
# CONFIGURATION
# ========================================

PROJECT_ROOT = Path("i:/CODE/tts-2")
MODEL_DIR = PROJECT_ROOT / "run" / "training_combined_phase2" / "XTTS_Combined_Phase2-October-04-2025_03+00PM-fb239cd"
MODEL_PATH = MODEL_DIR / "best_model_1901.pth"
OUTPUT_DIR = PROJECT_ROOT / "test_samples"
OUTPUT_DIR.mkdir(exist_ok=True)

# CONTROLLED NATURAL PROFILE
# Moderate temperature (0.45) - balanced between consistency and naturalness
# Moderate repetition_penalty (5.0) - prevents repetition without overemphasis
# Moderate top_k (40) - more controlled token selection
# Higher top_p (0.88) for smooth transitions
# LOWER length_penalty (0.85) to prevent end-of-sequence stress/overemphasis
PARAMS = {
    "temperature": 0.45,
    "top_p": 0.88,
    "top_k": 40,
    "repetition_penalty": 5.0,
    "length_penalty": 0.85,
}

# Multi-reference inference - 3 STRONG Vágó-characteristic references
# Using question + excitement + neutral to preserve Vágó's voice timbre
# Fewer references = stronger voice identity preservation
REFERENCES = [
    PROJECT_ROOT / "prepared_sources/vago_samples_first_source/question/question_025.wav",      # Primary - quiz tone
    PROJECT_ROOT / "prepared_sources/vago_samples_first_source/excitement/excitement_001.wav",  # Energy variation
    PROJECT_ROOT / "prepared_sources/vago_samples_first_source/neutral/neutral_021.wav",        # Stable baseline
]

# ========================================
# QUESTION TEMPLATES BY TOPIC
# ========================================

QUESTION_TEMPLATES = {
    "földrajz": [
        "Melyik ország fővárosa Budapest? Lengyelország; Ausztria; Magyarország; Csehország.",
        "Melyik kontinensen található Egyiptom? Ázsia; Afrika; Európa; Dél-Amerika.",
        "Melyik a világ leghosszabb folyója? Amazonas; Nílus; Misszipi; Jangce.",
        "Melyik ország területe a legnagyobb? Kanada; Kína; Oroszország; Amerikai Egyesült Államok.",
        "Melyik óceán a legnagyobb? Atlanti-óceán; Csendes-óceán; Indiai-óceán; Jeges-tenger.",
    ],
    "történelem": [
        "Melyik évben fedezte fel Kolumbusz Kristóf Amerikát? Ezernégyszázkilencvenkettő; Ezerötszáz; Ezernégyszáznyolcvannyolc; Ezerötszáztíz.",
        "Melyik évben tört ki az első világháború? Ezerkilencszáztíz; Ezerkilencszáztizennégy; Ezerkilencszáztizennyolc; Ezerkilencszázhúsz.",
        "Ki volt Magyarország első királya? Géza fejedelem; Szent István; Szent László; Árpád fejedelem.",
        "Melyik évben értek véget a második világháború? Ezerkilencszáznegyvennégy; Ezerkilencszáznegyvenöt; Ezerkilencszáznegyvenhát; Ezerkilencszáznegyvennyolc.",
        "Ki volt az Egyesült Államok első elnöke? Támász Dzsefferszon; Dzsórdzsz Vósingtön; Bendzsámin Frenklin; Dzsón Ádámsz.",
    ],
    "tudomány": [
        "Mi a fény sebessége vákuumban? Kétszáznyolcvanezer kilométer per szekundum; Háromszázezer kilométer per szekundum; Háromszázötven kilométer per szekundum; Négyszázezer kilométer per szekundum.",
        "Melyik elem vegyjele az Au? Ezüst; Arany; Alumínium; Arzén.",
        "Hány bolygó van a Naprendszerünkben? Hat bolygó; Hét bolygó; Nyolc bolygó; Kilenc bolygó.",
        "Mi a víz kémiai képlete? H kettő O; C O kettő; N H három; O kettő.",
        "Ki fedezte fel a gravitációt? Albert Einstein; Isaac Newton; Galileo Galilei; Stephen Hawking.",
    ],
    "irodalom": [
        "Ki írta a Rómeó és Júlia című drámát? Csárlz Dikensz; Vilyem Sékszpír; Márk Tvén; Oszkár Vajld.",
        "Ki írta a Toldi című eposztrílógiát? Petőfi Sándor; Arany János; Vörösmarty Mihály; Jókai Mór.",
        "Melyik magyar író kapta meg először a Nobel-díjat? Márai Sándor; Kosztolányi Dezső; Kertész Imre; Krúdy Gyula.",
        "Ki írta az Egri csillagok című regényt? Gárdonyi Géza; Mikszáth Kálmán; Móricz Zsigmond; Herczeg Ferenc.",
        "Melyik Sékszpír darab főszereplője Hámlet? A velencei kalmár; Othelló; Hámlet dán királyfi; Lír király.",
    ],
    "sport": [
        "Hány játékos van egy kosárlabda csapatban a pályán egyszerre? Négy játékos; Öt játékos; Hat játékos; Hét játékos.",
        "Hány pont ér egy touchdown az amerikai futballban? Négy pont; Öt pont; Hat pont; Hét pont.",
        "Hány játékrész van egy tenisz mérkőzésben? Kettő vagy három szett; Három vagy négy szett; Három vagy öt szett; Négy vagy öt szett.",
        "Melyik évben rendezték az első modern olimpiát? Ezernyolcszázkilencvenkettő; Ezernyolcszázkilencvenhat; Ezerkilencszáz; Ezerkilencszáznégy.",
        "Hány méter hosszú az olimpiai úszómedence? Huszonöt méter; Ötven méter; Száz méter; Kétszáz méter.",
    ],
    "zene": [
        "Melyik híres zeneszerző komponálta A négy évszak című művet? Volfgáng Amádéusz Móczárt; Lúdvig ván Bétóven; Antónyó Viváldi; Jóhan Sebástián Bakh.",
        "Ki írta a Kilencedik szimfóniát? Volfgáng Amádéusz Móczárt; Lúdvig ván Bétóven; Johánnesz Brámz; Fránc Súbert.",
        "Melyik hangszeren játszott Liszt Ferenc? Hegedű; Zongora; Orgona; Cselló.",
        "Ki komponálta a Varázsfuvola című operát? Móczárt; Verdi; Vágner; Pucsíni.",
        "Hány húrja van egy hegedűnek? Három húr; Négy húr; Öt húr; Hat húr.",
    ],
    "film": [
        "Jöjjön a következő kérdés ötvenmillióforintért. Melyik napon született a világhírű gyermek-gitáros, Vince Zsombor? Áá: Szeptember tizenötödikén; Béé: November ötödikén; Céé: Február huszonötödikén; vagy: Déé: Október kilencedikén; Nehéz kérdés, mert a többi válaszlehetőség is egy-egy híresség születési dátumát jelöli.; Kérdezzük meg a közönséget?",
        "Ki rendezte a Keresztapa című filmet? Mártin Szkorszézi; Frenszisz Ford Kopolá; Sztíven Szpílberg; Szténli Kjúbrik.",
        "Jöjjön a következő kérdés ötvenmillióforintért. Melyik napon találkozzunk a világhírű vovjátékossal, Lovász Líviusszal? Áá: Vasárnap hattól; Béé: Pénteken nyolctól; Céé: Mindkét napon; vagy: Déé: Rohadjon meg!; Nehéz kérdés. Kérdezzük meg a közönséget?",
        "Ki játszotta Indiána Dzsónszt? Tom Henksz; Heriszon Ford; Brúsz Vilisz; Mel Gibszon.",
        "Melyik évben készült az első Sztár Vorsz film? Ezerkilencszázhetvennégy; Ezerkilencszázhetvenhét; Ezerkilencszáznyolcvan; Ezerkilencszáznyolcvanhárnom.",
    ],
    "természet": [
        "Mi a legnagyobb élő állat a Földön? Az afrikai elefánt; A fehér cápa; A kék bálna; A zsiráf.",
        "Melyik állat a leggyorsabb szárazföldön? Az oroszlán; A gepárd; Az antilop; A strucc.",
        "Hány szárnya van egy pillangónak? Kettő; Négy; Hat; Nyolc.",
        "Melyik az egyetlen emlős, amely tud repülni? A repülő mókus; A denevér; A sugar glider; A repülő hal.",
        "Melyik madár tud hátrafelé repülni? A kolibri; A papagáj; A sólyom; A veréb.",
    ],
    "technológia": [
        "Ki alapította a Májkroszoft céget Bill Géjtsz-szel együtt? Sztív Dzsóbsz; Léri Pédzs; Pol Álen; Márk Zákerberg.",
        "Melyik évben alapították a Féjszbukkot? Kétezer-kettő; Kétezer-négy; Kétezer-hat; Kétezer-nyolc.",
        "Ki találta fel a villanykörtet? Nikolá Teszlá; Támász Ediszon; Alekszánder Gréjám Bell; Bendzsámin Frenklin.",
        "Melyik cég gyártja az Áj-Fónt? Szemszung; Ápl; Gúgl; Májkroszoft.",
        "Mi volt az első keresőmotor az interneten? Jáhú; Gúgl; Árki; ÁltáVisztá.",
    ],
}


# ========================================
# USER INPUT FUNCTIONS
# ========================================

def get_user_inputs():
    """Get number of questions and topic from user"""
    
    print()
    print("=" * 80)
    print("🎤 KVÍZ KÉRDÉS GENERÁTOR - INTERAKTÍV MÓD")
    print("=" * 80)
    print()
    
    # Show available topics
    print("📚 Elérhető témák:")
    topics = list(QUESTION_TEMPLATES.keys())
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic.capitalize()}")
    print(f"  10. Vegyes (random minden témából)")
    print()
    
    # Get topic
    while True:
        try:
            topic_choice = input("Válassz témát (1-10): ").strip()
            topic_idx = int(topic_choice)
            if topic_idx == 10:
                selected_topic = "vegyes"
                break
            elif 1 <= topic_idx <= len(topics):
                selected_topic = topics[topic_idx - 1]
                break
            else:
                print("❌ Érvénytelen választás! Válassz 1 és 10 között.")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Megszakítva.")
            return None, None
    
    print(f"✅ Választott téma: {selected_topic.capitalize()}")
    print()
    
    # Get number of questions
    if selected_topic == "vegyes":
        # For mixed, allow any number
        available = sum(len(q) for q in QUESTION_TEMPLATES.values())
        while True:
            try:
                num_str = input(f"Hány kérdést generáljak? (1-{available}, ajánlott: 20+): ").strip()
                num_questions = int(num_str)
                if 1 <= num_questions <= available:
                    break
                else:
                    print(f"❌ Érvénytelen szám! Válassz 1 és {available} között.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Megszakítva.")
                return None, None
    else:
        available = len(QUESTION_TEMPLATES[selected_topic])
        while True:
            try:
                num_str = input(f"Hány kérdést generáljak? (1-{available}): ").strip()
                num_questions = int(num_str)
                if 1 <= num_questions <= available:
                    break
                else:
                    print(f"❌ Érvénytelen szám! Válassz 1 és {available} között.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Megszakítva.")
                return None, None
    
    print(f"✅ Generálok {num_questions} kérdést a(z) {selected_topic} témában.")
    print()
    
    return selected_topic, num_questions

# ========================================
# MAIN GENERATION
# ========================================

def main():
    # Check for command-line arguments
    if len(sys.argv) == 3:
        # Command-line mode: topic_num questions_num
        try:
            topics = list(QUESTION_TEMPLATES.keys())
            choice = int(sys.argv[1])
            num_questions = int(sys.argv[2])
            
            # Handle "vegyes" (mixed) option
            if choice == 10:
                selected_topic = "vegyes"
                total_available = sum(len(q) for q in QUESTION_TEMPLATES.values())
                if num_questions < 1 or num_questions > total_available:
                    print(f"❌ Érvénytelen kérdésszám! Válassz 1-{total_available} között.")
                    return
            elif choice < 1 or choice > len(topics):
                print(f"❌ Érvénytelen téma! Válassz 1-10 között (10=vegyes).")
                return
            else:
                selected_topic = topics[choice - 1]
                available = len(QUESTION_TEMPLATES[selected_topic])
                if num_questions < 1 or num_questions > available:
                    print(f"❌ Érvénytelen kérdésszám! Válassz 1-{available} között.")
                    return
            
            print(f"🎯 Téma: {selected_topic.capitalize()}, Kérdések: {num_questions}")
            print()
            
        except ValueError:
            print("❌ Használat: python generate_questions_and_answers.py <téma 1-10> <kérdések>")
            print("   Téma 10 = vegyes (random minden témából)")
            return
    else:
        # Interactive mode
        selected_topic, num_questions = get_user_inputs()
        
        if selected_topic is None:
            return
    
    # Get questions for the selected topic
    if selected_topic == "vegyes":
        # Mixed mode: randomly select from all topics
        import random
        all_questions_pool = []
        for topic, questions in QUESTION_TEMPLATES.items():
            for q in questions:
                all_questions_pool.append((topic, q))
        
        # Shuffle and take requested number
        random.shuffle(all_questions_pool)
        questions_to_generate = all_questions_pool[:num_questions]
    else:
        all_questions = QUESTION_TEMPLATES[selected_topic]
        questions_to_generate = [(selected_topic, q) for q in all_questions[:num_questions]]
    
    print("=" * 80)
    print(f"🎯 GENERÁLÁS: {num_questions} KÉRDÉS - {selected_topic.upper()}")
    print("=" * 80)
    print()
    print(f"Model: {MODEL_PATH.name}")
    print(f"Parameters: temp={PARAMS['temperature']}, top_p={PARAMS['top_p']}, "
          f"top_k={PARAMS['top_k']}, rep_penalty={PARAMS['repetition_penalty']}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Check files
    print("📁 Checking files...")
    if not MODEL_PATH.exists():
        print(f"❌ Model not found: {MODEL_PATH}")
        return
    
    for ref in REFERENCES:
        if not ref.exists():
            print(f"❌ Reference not found: {ref}")
            return
    
    print("✅ All files found")
    print()
    
    # Load model
    print("⏳ Loading model...")
    config_path = MODEL_DIR / "config.json"
    config = XttsConfig()
    config.load_json(str(config_path))
    
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=str(MODEL_DIR),
        checkpoint_path=str(MODEL_PATH),
        vocab_path=str(MODEL_DIR / "vocab.json"),
        eval=True,
        use_deepspeed=False
    )
    
    # Use GPU if available (RTX 5070 Ti sm_120 now supported with PyTorch 2.10.0+cu128!)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"✅ Model loaded on {device.upper()}")
    print()
    
    # Compute speaker latents
    print("🎙️ Computing speaker latents from references...")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=[str(ref) for ref in REFERENCES],
        gpt_cond_len=30,
        gpt_cond_chunk_len=4,
        max_ref_length=60
    )
    print("✅ Speaker latents computed")
    print()
    
    # Generate samples
    print("=" * 80)
    print("GENERATING SAMPLES")
    print("=" * 80)
    print()
    
    for i, question_data in enumerate(questions_to_generate, 1):
        # Unpack topic and text
        if isinstance(question_data, tuple):
            topic, text = question_data
        else:
            topic = selected_topic
            text = question_data
        
        # Create filename
        filename = f"q{i:03d}_{topic}"
        
        print(f"[{i}/{num_questions}] {filename}")
        print(f"Text: {text[:80]}...")
        
        # Split text into question and answer segments
        # New pattern: "Question? Ans1; Ans2; Ans3; Ans4."
        import re
        
        # Split by question mark to separate question from answers
        if '?' in text:
            question_text = text.split('?')[0].strip() + '?'
            answers_text = text.split('?')[1].strip()
            
            # Split answers by semicolon
            answer_parts = [a.strip() for a in answers_text.rstrip('.').split(';')]
            
            # Generate each part separately with explicit pauses
            audio_segments = []
            
            # 1. Generate question
            out = model.inference(
                text=question_text,
                language="hu",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=PARAMS["temperature"],
                top_p=PARAMS["top_p"],
                top_k=PARAMS["top_k"],
                repetition_penalty=PARAMS["repetition_penalty"],
                length_penalty=PARAMS["length_penalty"],
                enable_text_splitting=False
            )
            audio_segments.append(out["wav"] if isinstance(out["wav"], np.ndarray) else out["wav"].cpu().numpy())
            # Add 0.7 sec silence after question (16800 samples at 24kHz)
            audio_segments.append(np.zeros(16800, dtype=np.float32))
            
            # 2. Generate each answer with pauses between them
            for answer_idx, answer in enumerate(answer_parts):
                out = model.inference(
                    text=answer + ".",
                    language="hu",
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=PARAMS["temperature"],
                    top_p=PARAMS["top_p"],
                    top_k=PARAMS["top_k"],
                    repetition_penalty=PARAMS["repetition_penalty"],
                    length_penalty=PARAMS["length_penalty"],
                    enable_text_splitting=False
                )
                audio_segments.append(out["wav"] if isinstance(out["wav"], np.ndarray) else out["wav"].cpu().numpy())
                # Add 0.9 sec silence between answers (21600 samples at 24kHz)
                if answer_idx < len(answer_parts) - 1:
                    audio_segments.append(np.zeros(16800, dtype=np.float32))
            
            # Concatenate all segments
            audio_numpy = np.concatenate(audio_segments)
        else:
            # Fallback: generate as single text
            out = model.inference(
                text=text,
                language="hu",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=PARAMS["temperature"],
                top_p=PARAMS["top_p"],
                top_k=PARAMS["top_k"],
                repetition_penalty=PARAMS["repetition_penalty"],
                length_penalty=PARAMS["length_penalty"],
                enable_text_splitting=True
            )
            audio_numpy = out["wav"]
            if isinstance(audio_numpy, torch.Tensor):
                audio_numpy = audio_numpy.cpu().numpy()
        
        # Save (using soundfile to avoid torchcodec issues)
        output_path = OUTPUT_DIR / f"{filename}.wav"
        sf.write(str(output_path), audio_numpy, 24000)
        
        print(f"✅ Saved: {output_path.name}")
        print()
    
    print("=" * 80)
    print(f"✅ MIND A(Z) {num_questions} MINTA ELKÉSZÜLT!")
    print("=" * 80)
    print()
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print()

if __name__ == "__main__":
    main()
