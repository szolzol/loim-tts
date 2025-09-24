#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VagoFinetune V3 Stable - V3 konfiguráció fokozott hangstabilitással
Spec: Maximum sebesség stabilabb hanggal
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from premium_xtts_hungarian import PremiumXTTSHungarian

class VagoFinetuneV3Stable:
    def __init__(self):
        """V3 Stable VagoFinetune inicializálás"""
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "vago_v3_stable_output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Reference audio
        self.reference_audio = self.project_root / "vago_finetune.mp3"
        
        print(f"🎯 VagoFinetune V3 Stable initialized")
        print(f"🎤 Reference: {self.reference_audio}")
        print(f"📁 Output: {self.output_dir}")
    
    def create_v3_stable_configs(self):
        """V3 stable konfigurációk létrehozása"""
        
        v3_stable_configs = [
            {
                "name": "v3_stable_conservative",
                "description": "V3 speed with maximum voice stability",
                "temperature": 0.4,  # Alacsonyabb = stabilabb
                "repetition_penalty": 1.4,  # Magasabb = kevésbé ismétlődő
                "speed_factor": 1.5,  # V3 sebesség
                "length_penalty": 0.75,
                "top_k": 30,  # Alacsonyabb = stabilabb választások
                "top_p": 0.8,  # Fókuszáltabb
                "use_deterministic_sampling": True,
                "voice_stability": 0.9  # Maximum stabilitás
            },
            {
                "name": "v3_stable_balanced",
                "description": "V3 speed with good stability balance",
                "temperature": 0.45,
                "repetition_penalty": 1.35,
                "speed_factor": 1.5,
                "length_penalty": 0.75,
                "top_k": 40,
                "top_p": 0.85,
                "use_deterministic_sampling": True,
                "voice_stability": 0.85
            },
            {
                "name": "v3_stable_optimal",
                "description": "V3 speed with optimized stability",
                "temperature": 0.3,  # Nagyon alacsony = ultra stabil
                "repetition_penalty": 1.5,  # Magas = dinamikus
                "speed_factor": 1.5,  # V3 sebesség
                "length_penalty": 0.7,  # Gyors
                "top_k": 25,  # Nagyon stabil
                "top_p": 0.75,  # Fókuszált
                "use_deterministic_sampling": True,
                "voice_stability": 0.95,  # Ultra stabil
                "consistency_boost": True
            }
        ]
        
        return v3_stable_configs
    
    def generate_v3_stable_samples(self):
        """V3 stable minták generálása"""
        print(f"\n🎵 Generating V3 stable samples...")
        
        # Teszt szövegek stabilitás teszteléshez
        stability_test_texts = [
            "Jó estét! Itt vagyok, Vágó István!",
            "Fantasztikus! Ez volt a helyes válasz! Gratulálok!",
            "Na most figyeljen! Ez már komoly pénz! Mi a végső válasza?",
            "A helyes válasz... és most... figyeljen ide... mindjárt elmondom...",
            "Hihetetlen! Fantasztikus teljesítmény! Ön lett a mai főnyertes!",
            "Ennyi volt a ma esti adás! Remélem, élvezték! Viszlát!"
        ]
        
        configs = self.create_v3_stable_configs()
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                print(f"❌ Failed to load TTS model")
                return False
            
            print(f"✅ TTS model loaded")
            
            # Minden konfiguráció tesztelése
            for config in configs:
                print(f"\n🎯 Testing {config['name']}...")
                print(f"📋 {config['description']}")
                print(f"🔧 Stability settings: temp={config['temperature']}, top_k={config['top_k']}")
                
                # Konfiguráció alkalmazása
                tts.config.update(config)
                
                # Minden teszt szöveghez
                for i, text in enumerate(stability_test_texts, 1):
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
            
            print(f"\n🎉 V3 stable samples completed!")
            return True
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return False
    
    def create_stability_comparison(self):
        """Stabilitás összehasonlítás"""
        print(f"\n📊 Creating stability comparison...")
        
        # Hosszabb szöveg a stabilitás tesztelésére
        stability_test_text = """Jó estét! Üdvözlöm a Legyen Ön Is Milliomos műsorában! 
        Itt vagyok, Vágó István, és ma este ismét van lehetőségük arra, 
        hogy akár ötven millió forinttal gazdagabban távozzanak innen. 
        De vigyázat! Egy rossz válasz, és minden odavan. 
        Na most figyeljen! Ez már komoly pénz! Mi a végső válasza? 
        Fantasztikus! Ez volt a helyes válasz! Gratulálok!"""
        
        # Stabilitás konfigurációk
        stability_configs = [
            {
                "name": "original_v3",
                "temperature": 0.5,
                "repetition_penalty": 1.3,
                "speed_factor": 1.5,
                "length_penalty": 0.75
            },
            {
                "name": "v3_more_stable",
                "temperature": 0.4,
                "repetition_penalty": 1.4,
                "speed_factor": 1.5,
                "length_penalty": 0.75,
                "top_k": 30,
                "top_p": 0.8
            },
            {
                "name": "v3_ultra_stable",
                "temperature": 0.3,
                "repetition_penalty": 1.5,
                "speed_factor": 1.5,
                "length_penalty": 0.7,
                "top_k": 25,
                "top_p": 0.75,
                "use_deterministic_sampling": True
            }
        ]
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                return False
            
            for config in stability_configs:
                print(f"🎵 Generating {config['name']}...")
                
                tts.config.update(config)
                
                timestamp = datetime.now().strftime("%H%M")
                output_filename = f"stability_test_{config['name']}_{timestamp}.wav"
                output_path = self.output_dir / output_filename
                
                result = tts.synthesize_premium(
                    text=stability_test_text,
                    ref_clips=[str(self.reference_audio)],
                    output_path=str(output_path)
                )
                
                if result:
                    print(f"✅ Stability test: {output_filename}")
            
            print(f"✅ Stability comparison completed!")
            return True
            
        except Exception as e:
            print(f"❌ Stability comparison error: {e}")
            return False
    
    def generate_final_v3_stable(self):
        """Végleges V3 stable verzió"""
        print(f"\n🏆 Generating final V3 stable version...")
        
        # Ultra stabil V3 konfiguráció
        final_config = {
            "name": "v3_stable_final",
            "description": "Final V3 with maximum stability",
            "temperature": 0.25,  # Ultra alacsony = nagyon stabil
            "repetition_penalty": 1.6,  # Magas = nagyon dinamikus
            "speed_factor": 1.5,  # V3 sebesség megtartva
            "length_penalty": 0.7,  # Gyors tempó
            "top_k": 20,  # Nagyon stabil választások
            "top_p": 0.7,  # Nagyon fókuszált
            "use_deterministic_sampling": True,
            "voice_stability": 0.98,
            "consistency_boost": True,
            "quality_enhancement": True
        }
        
        # Komplex teszt szöveg
        final_test_text = """Jó estét! Üdvözlöm a Legyen Ön Is Milliomos műsorában! 
        Itt vagyok, Vágó István, és ma este ismét van lehetőségük arra, 
        hogy akár ötven millió forinttal gazdagabban távozzanak innen. 
        De vigyázat! Egy rossz válasz, és minden odavan.
        
        Na most figyeljen! Itt az egymillió forintos kérdés! 
        Ez már komoly pénz! Mi a végső válasza?
        
        Fantasztikus! Lenyűgöző! Ez volt a helyes válasz! 
        Gratulálok! Ön lett a mai főnyertes!
        
        Hihetetlen! Fantasztikus teljesítmény! 
        Ennyi volt a ma esti adás! Remélem, élvezték! Viszlát!"""
        
        try:
            tts = PremiumXTTSHungarian()
            if not tts.load_model():
                return False
            
            # Végleges konfiguráció alkalmazása
            tts.config.update(final_config)
            
            timestamp = datetime.now().strftime("%y%m%d_%H%M")
            output_filename = f"vago_v3_stable_final_{timestamp}.wav"
            output_path = self.output_dir / output_filename
            
            print(f"🎵 Generating final V3 stable version...")
            print(f"🔧 Ultra stable settings applied")
            
            result = tts.synthesize_premium(
                text=final_test_text,
                ref_clips=[str(self.reference_audio)],
                output_path=str(output_path)
            )
            
            if result:
                print(f"🏆 Final V3 stable: {output_filename}")
                
                # Konfiguráció mentése
                import json
                config_path = self.output_dir / f"v3_stable_final_config_{timestamp}.json"
                with open(config_path, 'w') as f:
                    json.dump(final_config, f, indent=2)
                
                print(f"💾 Final config saved: {config_path.name}")
                print(f"\n🎯 V3 Stable Features:")
                print(f"   • Maximum speed (1.5x)")
                print(f"   • Ultra stable voice (temp: 0.25)")
                print(f"   • Consistent quality")
                print(f"   • Deterministic sampling")
                
                return True
            else:
                print(f"❌ Failed to generate final V3 stable")
                return False
                
        except Exception as e:
            print(f"❌ Final generation error: {e}")
            return False

def main():
    print("🎯 === VAGO FINETUNE V3 STABLE ===")
    print("🏆 Maximum speed with enhanced voice stability")
    
    v3_stable = VagoFinetuneV3Stable()
    
    # V3 stable minták generálása
    if v3_stable.generate_v3_stable_samples():
        # Stabilitás összehasonlítás
        v3_stable.create_stability_comparison()
        
        # Végleges V3 stable
        v3_stable.generate_final_v3_stable()
        
        print(f"\n🎉 === V3 STABLE COMPLETED ===")
        print(f"🎯 V3 speed with maximum voice stability!")
        print(f"📁 Results: {v3_stable.output_dir}")
        print(f"\n💡 Try the 'v3_stable_final' version for best results!")
    else:
        print(f"\n❌ V3 stable generation failed!")

if __name__ == "__main__":
    main()