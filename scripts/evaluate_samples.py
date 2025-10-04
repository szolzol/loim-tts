"""
Sample Evaluation Helper
Helps you systematically evaluate generated voice samples
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("f:/CODE/tts-2")
OUTPUTS = [
    PROJECT_ROOT / "test_outputs",
    PROJECT_ROOT / "test_outputs_v2",
]

def evaluate_samples():
    """Interactive sample evaluation"""
    
    print("="*70)
    print("VOICE SAMPLE EVALUATION")
    print("István Vágó Milliomos Voice Clone")
    print("="*70)
    
    print("\n📋 Evaluation Criteria:")
    print("\n1. Voice Similarity (1-10)")
    print("   How close does it sound to István Vágó?")
    print("   1 = Completely different, 10 = Perfect match")
    
    print("\n2. Pronunciation (1-10)")
    print("   How natural is the Hungarian pronunciation?")
    print("   1 = Robotic/wrong, 10 = Perfect native speaker")
    
    print("\n3. Emotional Accuracy (1-10)")
    print("   Does the emotion match the category?")
    print("   (Excitement sounds excited, tension sounds tense, etc.)")
    print("   1 = Wrong emotion, 10 = Perfect match")
    
    print("\n4. Smoothness (1-10)")
    print("   How natural and smooth is the speech flow?")
    print("   1 = Very choppy, 10 = Completely smooth")
    
    print("\n5. Quiz Show Energy (1-10)")
    print("   Does it sound like a TV quiz show host?")
    print("   1 = No energy, 10 = Perfect TV presenter")
    
    print("\n" + "="*70)
    print("SAMPLE LOCATIONS")
    print("="*70)
    
    for output_dir in OUTPUTS:
        if output_dir.exists():
            samples = list(output_dir.glob("*.wav"))
            print(f"\n📁 {output_dir.name}:")
            print(f"   Location: {output_dir}")
            print(f"   Samples: {len(samples)} files")
        else:
            print(f"\n📁 {output_dir.name}: Not found")
    
    print("\n" + "="*70)
    print("EVALUATION INSTRUCTIONS")
    print("="*70)
    
    print("\n📝 How to evaluate:")
    print("\n1. Open the sample folders in File Explorer:")
    print("   test_outputs/     - Original generation")
    print("   test_outputs_v2/  - Improved parameters")
    
    print("\n2. Listen to each sample carefully")
    
    print("\n3. For each sample, rate 1-10 on all 5 criteria")
    
    print("\n4. Calculate averages:")
    print("   • Average score across all samples")
    print("   • Identify weakest category")
    print("   • Note best and worst samples")
    
    print("\n" + "="*70)
    print("DECISION GUIDE")
    print("="*70)
    
    print("\n📊 Average Score Interpretation:")
    print("\n   9-10: EXCELLENT - Ready for production")
    print("         → Deploy immediately (Option 5)")
    
    print("\n   7-8:  GOOD - Minor improvements needed")
    print("         → Continue training 20 epochs (Option 1)")
    print("         → Or adjust generation parameters")
    
    print("\n   5-6:  MODERATE - Significant work needed")
    print("         → Retrain with new classification (Option 2)")
    print("         → Or expand dataset (Option 4)")
    
    print("\n   3-4:  POOR - Major issues")
    print("         → Expand dataset significantly (Option 4)")
    print("         → Check if reference audio is good quality")
    
    print("\n   1-2:  VERY POOR - Fundamental problems")
    print("         → Review dataset quality")
    print("         → Check text transcriptions")
    print("         → Verify audio preprocessing")
    
    print("\n" + "="*70)
    print("SPECIFIC ISSUES & SOLUTIONS")
    print("="*70)
    
    print("\n❌ Problem: Choppy/robotic speech")
    print("   ✅ Solution:")
    print("      • Continue training (smooths out)")
    print("      • Lower temperature (0.65 → 0.55)")
    print("      • More training data")
    
    print("\n❌ Problem: Wrong pronunciation")
    print("   ✅ Solution:")
    print("      • Check text transcriptions in metadata.csv")
    print("      • Verify Hungarian language setting")
    print("      • More training epochs")
    
    print("\n❌ Problem: Doesn't sound like István Vágó")
    print("   ✅ Solution:")
    print("      • Use better reference audios")
    print("      • More training data (need 30+ min)")
    print("      • Longer training (50-100 epochs)")
    
    print("\n❌ Problem: Wrong emotional tone")
    print("   ✅ Solution:")
    print("      • Dataset reclassification worked!")
    print("      • Retrain from scratch with new classification")
    print("      • Match reference audio to target emotion")
    
    print("\n❌ Problem: Inconsistent quality")
    print("   ✅ Solution:")
    print("      • More training epochs (reduces variance)")
    print("      • More training data")
    print("      • Check eval vs training loss gap")
    
    print("\n" + "="*70)
    print("COMPARISON CHECKLIST")
    print("="*70)
    
    print("\n✓ Compare v1 vs v2:")
    print("   • Same text, different parameters")
    print("   • v2 has lower temperature (more conservative)")
    print("   • v2 uses varied reference audios")
    print("   → Which sounds better?")
    
    print("\n✓ Compare to original dataset:")
    print("   • dataset_milliomos/[category]/")
    print("   • Does generated match original style?")
    print("   • Is emotional tone preserved?")
    
    print("\n✓ Compare categories:")
    print("   • Which category sounds best?")
    print("   • Which needs most work?")
    print("   • Are weak categories under-represented?")
    
    print("\n" + "="*70)
    print("NEXT STEPS AFTER EVALUATION")
    print("="*70)
    
    print("\n1️⃣  Record your scores")
    print("2️⃣  Identify main issues")
    print("3️⃣  Choose appropriate option from NEXT_STEPS.md")
    print("4️⃣  Run the selected action")
    print("5️⃣  Generate new samples")
    print("6️⃣  Re-evaluate and compare")
    print("7️⃣  Repeat until satisfied")
    
    print("\n" + "="*70)
    
    input("\nPress Enter to open sample folders in Explorer...")
    
    # Open folders in File Explorer
    for output_dir in OUTPUTS:
        if output_dir.exists():
            os.startfile(str(output_dir))
            print(f"✓ Opened: {output_dir.name}")
    
    print("\n✅ Ready to evaluate!")
    print("Listen carefully and take notes. Good luck! 🎧")

if __name__ == "__main__":
    evaluate_samples()
