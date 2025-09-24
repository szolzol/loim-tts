#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VagoFinetune Fast Smooth - Gyors smooth konfiguráció
Spec: Smooth minőség gyorsabb beszédtempóval
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from premium_xtts_hungarian import PremiumXTTSHungarian

class VagoFinetuneFastSmooth:
    def __init__(self):
        """Fast Smooth VagoFinetune inicializálás"""
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "vago_fast_smooth_output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Reference audio
        self.reference_audio = self.project_root / "vago_finetune.mp3"
        
        print(f"🚀 VagoFinetune Fast Smooth initialized")
        print(f"🎤 Reference: {self.reference_audio}")
        print(f"📁 Output: {self.output_dir}")
    
    def create_fast_smooth_configs(self):
        """Gyors smooth konfigurációk létrehozása"""
        
        fast_smooth_configs = [
            {
                "name": "fast_smooth_v1",
                "description": "Smooth quality with moderate speed boost",
                "temperature": 0.6,  # Smooth tartomány, de kicsit alacsonyabb
                "repetition_penalty": 1.15,  # Kevésbé agresszív mint balanced
                "speed_factor": 1.3,  # Gyorsabb
                "length_penalty": 0.85  # Rövidebb, gyorsabb mondatok
            },
            {
                "name": "fast_smooth_v2", 
                "description": "Smooth quality with higher speed",
                "temperature": 0.65,
                "repetition_penalty": 1.2,
                "speed_factor": 1.4,  # Még gyorsabb
                "length_penalty": 0.8
            },
            {
                "name": "fast_smooth_v3",
                "description": "Maximum speed while keeping smoothness",
                "temperature": 0.5,  # Stabilabb a gyorsaságért
                "repetition_penalty": 1.3,
                "speed_factor": 1.5,  # Maximum sebesség
                "length_penalty": 0.75
            }
        ]
        
        return fast_smooth_configs
    
    def generate_fast_smooth_samples(self):
        """Gyors smooth minták generálása"""
        print(f"\n🎵 Generating fast smooth samples...")
        
        # Teszt szövegek
        test_texts = [
            "Jó estét! Itt vagyok, Vágó István!",
            "Fantasztikus! Ez volt a helyes válasz!",
            "Na most figyeljen! Mi a végső válasza?",
            "A helyes válasz most következik... figyeljen!",
            "Gratulálok! Ön lett a mai főnyertes!"
        ]
        
        configs = self.create_fast_smooth_configs()
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                print(f"❌ Failed to load TTS model")
                return False
            
            print(f"✅ TTS model loaded")
            
            # Minden konfiguráció tesztelése
            for config in configs:
                print(f"\n🧪 Testing {config['name']}...")
                print(f"📋 {config['description']}")
                
                # Konfiguráció alkalmazása
                tts.config.update(config)
                
                # Minden teszt szöveghez
                for i, text in enumerate(test_texts, 1):
                    timestamp = datetime.now().strftime("%H%M")
                    output_filename = f"{config['name']}_test{i}_{timestamp}.wav"
                    output_path = self.output_dir / output_filename
                    
                    try:
                        result = tts.synthesize_premium(
                            text=text,
                            ref_clips=[str(self.reference_audio)],
                            output_path=str(output_path)
                        )
                        
                        if result:
                            print(f"✅ Generated: {output_filename}")
                        else:
                            print(f"❌ Failed: {output_filename}")
                            
                    except Exception as e:
                        print(f"❌ Error generating {output_filename}: {e}")
            
            print(f"\n🎉 Fast smooth samples completed!")
            return True
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return False
    
    def create_speed_comparison(self):
        """Sebesség összehasonlítás"""
        print(f"\n📊 Creating speed comparison...")
        
        comparison_text = "Ez egy sebesség teszt! Smooth minőség, de gyors tempó!"
        
        # Konfigurációk összehasonlításhoz
        speed_configs = [
            {
                "name": "original_smooth",
                "temperature": 0.7,
                "repetition_penalty": 1.1,
                "speed_factor": 0.9
            },
            {
                "name": "fast_smooth_optimal",
                "temperature": 0.6,
                "repetition_penalty": 1.15,
                "speed_factor": 1.3,
                "length_penalty": 0.85
            },
            {
                "name": "ultra_fast_smooth",
                "temperature": 0.5,
                "repetition_penalty": 1.3,
                "speed_factor": 1.5,
                "length_penalty": 0.75
            }
        ]
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                return False
            
            for config in speed_configs:
                print(f"🎵 Generating {config['name']}...")
                
                tts.config.update(config)
                
                timestamp = datetime.now().strftime("%H%M")
                output_filename = f"speed_comparison_{config['name']}_{timestamp}.wav"
                output_path = self.output_dir / output_filename
                
                result = tts.synthesize_premium(
                    text=comparison_text,
                    ref_clips=[str(self.reference_audio)],
                    output_path=str(output_path)
                )
                
                if result:
                    print(f"✅ Speed comparison: {output_filename}")
            
            print(f"✅ Speed comparison completed!")
            return True
            
        except Exception as e:
            print(f"❌ Comparison error: {e}")
            return False
    
    def generate_recommended_config(self):
        """Ajánlott gyors smooth konfiguráció"""
        print(f"\n🎯 Generating recommended fast smooth config...")
        
        # Optimális gyors smooth beállítások
        optimal_config = {
            "name": "recommended_fast_smooth",
            "temperature": 0.6,
            "repetition_penalty": 1.15,
            "speed_factor": 1.3,
            "length_penalty": 0.85,
            "top_k": 50,
            "top_p": 0.85
        }
        
        # Hosszabb teszt szöveg
        test_text = """Jó estét! Üdvözlöm a Legyen Ön Is Milliomos műsorában! 
        Itt vagyok, Vágó István, és ma este ismét van lehetőségük arra, 
        hogy akár ötven millió forinttal gazdagabban távozzanak innen. 
        Fantasztikus! Ez volt a helyes válasz! Gratulálok!"""
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                return False
            
            # Optimális konfiguráció alkalmazása
            tts.config.update(optimal_config)
            
            timestamp = datetime.now().strftime("%y%m%d_%H%M")
            output_filename = f"vago_fast_smooth_recommended_{timestamp}.wav"
            output_path = self.output_dir / output_filename
            
            print(f"🎵 Generating recommended version...")
            
            result = tts.synthesize_premium(
                text=test_text,
                ref_clips=[str(self.reference_audio)],
                output_path=str(output_path)
            )
            
            if result:
                print(f"✅ Recommended fast smooth: {output_filename}")
                
                # Konfiguráció mentése
                import json
                config_path = self.output_dir / f"fast_smooth_optimal_config_{timestamp}.json"
                with open(config_path, 'w') as f:
                    json.dump(optimal_config, f, indent=2)
                
                print(f"💾 Config saved: {config_path.name}")
                return True
            else:
                print(f"❌ Failed to generate recommended version")
                return False
                
        except Exception as e:
            print(f"❌ Recommended generation error: {e}")
            return False

def main():
    print("🚀 === VAGO FINETUNE FAST SMOOTH ===")
    print("🎯 Smooth quality with faster speech tempo")
    
    fast_smooth = VagoFinetuneFastSmooth()
    
    # Gyors smooth minták generálása
    if fast_smooth.generate_fast_smooth_samples():
        # Sebesség összehasonlítás
        fast_smooth.create_speed_comparison()
        
        # Ajánlott konfiguráció
        fast_smooth.generate_recommended_config()
        
        print(f"\n🎉 === FAST SMOOTH COMPLETED ===")
        print(f"🎯 Smooth quality with faster tempo ready!")
        print(f"📁 Results: {fast_smooth.output_dir}")
        print(f"\n💡 Try the 'recommended_fast_smooth' version!")
    else:
        print(f"\n❌ Fast smooth generation failed!")

if __name__ == "__main__":
    main()