#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOIM Episode Tester - Teljes műsor tesztelése
Spec: Hosszú, komplex Legyen Ön Is Milliomos epizód hangszintézise
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from premium_xtts_hungarian import PremiumXTTSHungarian

class LOIMEpisodeTester:
    def __init__(self):
        self.output_dir = Path("episode_test_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # A teljes epizód szövege
        self.full_episode_text = """Jó estét! Üdvözlöm a Legyen Ön Is Milliomos műsorában! Itt vagyok, Vágó István, és ma este ismét van lehetőségük arra, hogy akár ötven millió forinttal gazdagabban távozzanak innen. De vigyázat! Egy rossz válasz, és minden odavan.

Ma este játékosunk Kovács József úr Debrecenből, aki tanár, két gyermek édesapja, és nagy álma, hogy a családjával eljuthasson Ausztráliába. Na, József úr, készen áll a nagy kalandra?

Akkor kezdjük! Itt az első kérdés ötvenezer forintért. Figyelem, még nem nagy pénz, de már kezd izgalmas lenni! A kérdés:

Melyik állat neve szerepel ebben a közismert mondásban: "A jó barát maga a fél..."?
A: egészség
B: ló  
C: kutya
D: macska

Na, ez még könnyű volt, ugye? Látom a szemén, hogy tudja! Mi a válasza?

Igen! A helyes válasz a B, a ló! Kitűnő! Ez volt a helyes válasz! Gratulálok, megnyerte az ötvenezer forintot!

És most jön a következő kérdés százezer forintért. Lassan melegítünk, de még mindig biztos talaj alatt vagyunk. A kérdés:

Ki festette a Sixtus-kápolna mennyezetfreskóját?
A: Leonardo da Vinci
B: Rafael
C: Michelangelo
D: Donatello

Hmm, látom, hogy gondolkodik! Ez már kicsit komolyabb műveltségi kérdés. Mi a véleménye?

Brávó! A helyes válasz valóban a C, Michelangelo! Nagyszerű! Ez volt a jó válasz! Gratulálok, továbbjutott a következő szintre!

Most jön a kétszázezer forintos kérdés! Na, ez már kezd komoly lenni. Figyeljünk oda! A kérdés:

Melyik magyar író írta a Pál utcai fiúk című regényt?
A: Mikszáth Kálmán
B: Jókai Mór  
C: Molnár Ferenc
D: Gárdonyi Géza

Ez már igazi magyar irodalom! Mit gondol, tudja?

Fantasztikus! A helyes válasz a C, Molnár Ferenc! Ezt remekül megoldotta! Ez volt a helyes válasz!

És íme az ötszázezer forintos kérdés! Itt már nem játszunk, uraim. Ez már komoly pénz! A kérdés:

Hány csillagos az Európai Unió zászlaja?
A: tizenkettő
B: tizenöt
C: huszonhét  
D: huszonnyolc

Na most figyeljen! Ezt tudni kell! Mi a válasza?

Kiváló! A helyes válasz a A, tizenkettő! Láttam a szemén, hogy tudta! Gratulálok, ez tökéletes válasz volt!

Na most figyeljen! Itt az egymillió forintos kérdés! Itt már nincs viccelődés, ez már igazi pénz! A kérdés:

Melyik bolygó a legnagyobb a Naprendszerben?
A: Szaturnusz
B: Jupiter
C: Neptunusz
D: Uránusz

Hmm, látom, hogy biztos magában! És joggal! Szuper! A helyes válasz a B, Jupiter! Ezt bravúrosan oldotta meg! A helyes válasz valóban ez volt!

És most jön a kétmillió forintos kérdés! Figyeljen jól, mert ez már nem gyerekjáték. Itt már komolyabb tudás kell! A kérdés:

Ki komponálta A kis éjszakai zenét?
A: Johann Sebastian Bach
B: Ludwig van Beethoven  
C: Wolfgang Amadeus Mozart
D: Franz Schubert

Na, ez már komolyabb zenei műveltség! Mit gondol?

Csodálatos! A helyes válasz a C, Wolfgang Amadeus Mozart! Ön tényleg érti ezt! Gratulálok!

Ötmillió forint! Tisztelt játékos, ez már olyan összeg, amiből házat lehet venni! Biztos, hogy folytatja? Látom az izzadtságot a homlokán, ez teljesen természetes!

Oké, folytatjuk! A kérdés ötmillió forintért:

Melyik város Olaszország fővárosa?
A: Milánó
B: Nápoly
C: Firenze  
D: Róma

Na, ez viszont egyszerűbb volt! Látom, hogy megkönnyebbült!

Fantasztikus! Lenyűgöző! A helyes válasz a D, Róma! Tökéletes válasz! Ötmillió forint az öné!

Tízmillió forint! Na, ennél a pénznél már én is elgondolkodnék. Ez már olyan összeg, amiből egy életre kijön! De ha biztos magában, akkor folytatjuk! Mit szól, használ segítséget? Rendelkezésére áll a telefonos segítség, a közönség szavazás, és az ötven-ötven!

Igen? Akkor halljuk a kérdést tízmillió forintért:

Hány kontinens van a Földön?
A: öt
B: hat  
C: hét
D: nyolc

Ez egy trükkös kérdés lehet! Mit gondol? Biztos a válaszában?

Na most figyeljen jól... ez a döntő pillanat. Biztosan ezt választja végső válaszként?

Igen, a helyes válasz... és most... figyeljen ide... mindjárt elmondom...

A helyes válasz a C, hét! Hét kontinens van: Ázsia, Afrika, Észak-Amerika, Dél-Amerika, Antarktisz, Európa és Ausztrália! Gratulálok, tízmillió forint!

Huszonötmillió forint! Uram, ez már olyan pénz, amiből egy életre kijön! Tényleg folytatni akarja? Látom a bizonytalanságot a szemében, ez természetes! Senki sem szégyen, ha segítséget kér!

Mit szól, felhívjuk azt a barátját, aki biztos tud segíteni? Vagy inkább a közönséghez fordulunk?

Jó, akkor telefonáljunk! Ki az a barát, akit fel szeretne hívni?

Rendben, hívjuk fel Péter urat! ... Sajnos nem veszi fel a telefont. Ez előfordul! Mit csinálunk? Van még két segítsége!

Akkor közönség szavazás! Kedves közönség, segítsenek József úrnak! A kérdés huszonötmillió forintért:

Ki volt az első ember a Holdon?
A: Jurij Gagarin
B: John Glenn  
C: Neil Armstrong
D: Buzz Aldrin

A közönség szavazása: A: 5%, B: 10%, C: 78%, D: 7%

Na, a közönség egyértelmű! Mit szól, elfogadja a közönség tanácsát?

Most tartsa magát... mindjárt kiderül... helyes volt-e a válasza... és a válasz...

Fantasztikus! A közönség jól tudta! A helyes válasz valóban a C, Neil Armstrong! Huszonötmillió forint!

És most... itt az ötven millió forintos kérdés! A főnyeremény! Itt a csúcs, itt a teteje mindennek! Ha erre jól válaszol, akkor ötven millió forinttal lesz gazdagabb! 

Egy pillanat! Mielőtt felteszem a kérdést... gondolja át még egyszer! Ez az utolsó kérdés! Ha rosszul válaszol, minden pénzét elveszíti! Biztos folytatni akarja?

Rendben! A kérdés ötven millió forintért - figyelem, ez a nagy kérdés:

Melyik évben kezdődött a második világháború?
A: 1938
B: 1939
C: 1940  
D: 1941

Na most... ez a pillanat! Minden ezen múlik! Mit szól, használja az utolsó segítségét, az ötven-ötvenet?

Igen? Akkor eltávolítom két rossz választ... Marad a B és a C! 1939 vagy 1940?

Most nagyon vigyázzon! Itt sok minden múlik ezen az egy választáson! Mi a végső válasza?

B? 1939? Biztosan?

Most koncentráljon... minden a következő pillanaton múlik... lélegezzen... és most...

A helyes válasz... 

1939! A B válasz! FANTASZTIKUS! ÖTVEN MILLIÓ FORINT! ÖN LETT A MAI FŐNYERTES! GRATULÁLOK!

Hihetetlen! Fantasztikus teljesítmény! József úr, Ön ma este ötven millió forinttal lesz gazdagabb! Most már tényleg elmehet a családjával Ausztráliába!

Ennyi volt a ma esti adás! Remélem, élvezték! Legközelebb ismét itt leszek, és újabb játékosaink próbálhatnak szerencsét a nagy pénzért! Viszlát, és jó éjszakát!"""
    
    def test_episode_synthesis(self):
        """Teljes epizód hangszintézis tesztelése"""
        try:
            print("🎬 === LOIM EPISODE TESTER ===")
            print(f"📝 Episode length: {len(self.full_episode_text)} characters")
            print(f"📊 Estimated duration: ~{len(self.full_episode_text) // 150} minutes")
            print(f"🎯 Testing with: Vágó István voice")
            
            # TTS inicializálás
            tts = PremiumXTTSHungarian()
            
            if not tts.load_model():
                print(f"❌ Failed to load TTS model")
                return False
            
            # Fájlnév generálása
            timestamp = datetime.now().strftime("%y%m%d_%H%M")
            filename = f"loim_full_episode_{timestamp}.wav"
            output_path = self.output_dir / filename
            
            print(f"\n🎵 Starting synthesis...")
            print(f"⏰ This may take several minutes due to text length...")
            
            # Ellenőrizzük, hogy van-e reference fájl
            ref_files = []
            if os.path.exists("vago_vagott.mp3"):
                ref_files.append("vago_vagott.mp3")
                print(f"🎤 Using reference: vago_vagott.mp3")
            
            # Hangszintézis
            result = tts.synthesize_premium(
                text=self.full_episode_text,
                ref_clips=ref_files if ref_files else [],
                output_path=str(output_path)
            )
            
            if result:
                print(f"\n✅ Episode synthesis completed!")
                print(f"📁 Output: {filename}")
                print(f"📍 Location: {output_path}")
                print(f"🎉 Full LOIM episode generated successfully!")
                return True
            else:
                print(f"❌ Failed to synthesize episode")
                return False
                
        except Exception as e:
            print(f"❌ Error in episode synthesis: {e}")
            return False
    
    def test_short_sample(self):
        """Rövid minta tesztelése először"""
        try:
            print(f"\n🔬 Testing short sample first...")
            
            sample_text = """Jó estét! Üdvözlöm a Legyen Ön Is Milliomos műsorában! Itt vagyok, Vágó István, és ma este ismét van lehetőségük arra, hogy akár ötven millió forinttal gazdagabban távozzanak innen."""
            
            tts = PremiumXTTSHungarian()
            
            if not tts.load_model():
                print(f"❌ Failed to load TTS model")
                return False
            
            timestamp = datetime.now().strftime("%y%m%d_%H%M")
            filename = f"loim_sample_{timestamp}.wav"
            output_path = self.output_dir / filename
            
            print(f"🎵 Synthesizing sample...")
            
            ref_files = []
            if os.path.exists("vago_vagott.mp3"):
                ref_files.append("vago_vagott.mp3")
            
            result = tts.synthesize_premium(
                text=sample_text,
                ref_clips=ref_files if ref_files else [],
                output_path=str(output_path)
            )
            
            if result:
                print(f"✅ Sample synthesis successful: {filename}")
                return True
            else:
                print(f"❌ Sample synthesis failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in sample synthesis: {e}")
            return False

def main():
    tester = LOIMEpisodeTester()
    
    print("🎬 LOIM Episode Synthesis Test")
    print("=" * 50)
    
    # Először mintát tesztelünk
    if tester.test_short_sample():
        print(f"\n🎯 Sample successful! Proceeding with full episode...")
        tester.test_episode_synthesis()
    else:
        print(f"\n❌ Sample failed! Check TTS setup before full episode.")

if __name__ == "__main__":
    main()