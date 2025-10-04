"""
Deep Semantic Reclassification of Audio Dataset
Analyzes speech content and emotional context to properly categorize audio samples
"""

import os
import shutil
import csv
from pathlib import Path
import re

PROJECT_ROOT = Path("f:/CODE/tts-2")
DATASET_PATH = PROJECT_ROOT / "dataset_milliomos"
METADATA_FILE = DATASET_PATH / "metadata.csv"
BACKUP_FILE = DATASET_PATH / "metadata_backup.csv"

# Comprehensive semantic classification rules
CLASSIFICATION_RULES = {
    'greeting': {
        'keywords': [
            'gratulálok', 'gratulál', 'köszönt', 'szeretettel', 'üdvözöl',
            'kedves', 'jó estét', 'hello', 'szia', 'üdv', 'várunk',
            'tessék', 'foglaljon helyet', 'jövök', 'érkezik', 'érkezett',
            'sok szeretet', 'legyen', 'várjon', 'kivel érkezett'
        ],
        'patterns': [
            r'gratulál\w*',
            r'köszön\w*',
            r'szeretettel\s+\w+',
            r'kedves\s+\w+',
            r'várunk',
            r'érkezett',
            r'foglaljon\s+helyet',
            r'tessék\s+\w+'
        ],
        'sentiment': 'positive_welcoming',
        'description': 'Welcoming phrases, congratulations, greetings, introductions'
    },
    
    'excitement': {
        'keywords': [
            'helyes', 'így van', 'így is van', 'fantasztikus', 'nagyszerű',
            'szép', 'igen', 'jókor', 'garantált', 'nyeremény', 'millió',
            'forint', 'sikeres', 'pompás', 'remek', 'elég jól',
            'konstatálhat', 'érdekes', 'világhírű', 'bizony', 'igaza van',
            'egyet', 'tökéletes', 'helyes válasz', 'brávó', 'kiváló'
        ],
        'patterns': [
            r'helyes\s*[!,.]',
            r'így\s+van',
            r'így\s+is\s+van',
            r'\d+\s*(millió|ezer)\s*forint',
            r'garantált\s+\w+',
            r'nagyszerű\w*',
            r'fantasztikus',
            r'igaza\s+van',
            r'bizony\s+bizony'
        ],
        'sentiment': 'positive_excited',
        'description': 'Positive feedback, excitement about money, affirmation of correct answers'
    },
    
    'question': {
        'keywords': [
            'melyik', 'milyen', 'ki nem', 'mi volt', 'hogyan', 'hol',
            'mikor', 'miért', 'mi a neve', 'tegyék', 'nézzük', 'kérdés',
            'válasz', 'mondja', 'mit jelent', 'említse meg', 'sorolja fel',
            'nevez', 'hív', 'származ', 'magyaráz'
        ],
        'patterns': [
            r'^melyik\s+\w+',
            r'^milyen\s+\w+',
            r'^ki\s+(nem\s+)?volt',
            r'^mi\s+(volt|a\s+neve|jelent)',
            r'^hogyan\s+\w+',
            r'^hol\s+\w+',
            r'^mikor\s+\w+',
            r'^miért\s+\w+',
            r'tegyék\s+\w+\s+sorrendbe',
            r'kérdés.*\?$',
            r'\?\s*$'  # Ends with question mark
        ],
        'anti_patterns': [
            r'ez\s+a\s+kérdés',  # Talking about question, not asking
            r'szép\s+kérdés',
            r'nehéz\s+kérdés'
        ],
        'sentiment': 'neutral_inquiring',
        'description': 'Direct questions, quiz questions, asking for information'
    },
    
    'tension': {
        'keywords': [
            'biztos', 'meggyőződés', 'retteg', 'biztos benne', 'elképzelhető',
            'vagy', 'esetleg', 'nehéz', 'remélem', 'gondol', 'úgy érzi',
            'megérzés', 'vacakol', 'csalódott', 'rossz hír', 'tudja',
            'nem tudom', 'segít', 'kicsit segít', 'választ', 'kizár',
            'zaklat', 'elveszt', 'elpukkan', 'érzékel'
        ],
        'patterns': [
            r'biztos\s+(benne|vagy)',
            r'elképzelhető',
            r'vagy\s+\w+\s+vagy',  # "vagy X vagy Y"
            r'esetleg',
            r'ne\s+\w+',
            r'nem\s+tudom',
            r'retteg\w*',
            r'remélem',
            r'megérzés',
            r'segít\w*',
            r'kizár\w*',
            r'elveszt\w*'
        ],
        'sentiment': 'uncertain_tense',
        'description': 'Uncertainty, doubt, tension, deliberation, choices between options'
    },
    
    'neutral': {
        'keywords': [
            'tulajdonképpen', 'tehát', 'úgyhogy', 'ugyanis', 'mert',
            'azért', 'viszont', 'azonban', 'mivel', 'így', 'akkor',
            'most', 'ebben', 'ott', 'itt', 'amikor', 'amely'
        ],
        'patterns': [
            r'^tehát\s+\w+',
            r'tulajdonképpen',
            r'úgyhogy',
            r'viszont',
            r'azonban'
        ],
        'sentiment': 'neutral_explanatory',
        'description': 'Explanatory statements, neutral commentary, factual information'
    },
    
    'transition': {
        'keywords': [
            'akkor', 'most', 'na', 'jó', 'rendben', 'tessék', 'nézzük',
            'lássuk', 'folytatód', 'következő', 'tovább', 'itt van',
            'na jó', 'hát akkor', 'na most', 'és akkor', 'ezek szerint'
        ],
        'patterns': [
            r'^na\s+(jó|most|akkor)',
            r'^hát\s+akkor',
            r'^és\s+akkor',
            r'^akkor\s+\w+',
            r'^most\s+\w+',
            r'^tessék',
            r'^nézzük',
            r'^lássuk',
            r'következő\s+\w+',
            r'folytatód\w*',
            r'itt\s+van',
            r'rendben\s+van'
        ],
        'sentiment': 'neutral_transitional',
        'description': 'Transitional phrases, moving between topics, procedural statements'
    },
    
    'confirmation': {
        'keywords': [
            'igen', 'jó', 'oké', 'rendben', 'megvan', 'értem',
            'persze', 'természetesen', 'úgy van', 'pontosan',
            'megértettem', 'világos', 'kész'
        ],
        'patterns': [
            r'^igen[,.]',
            r'^jó[,.]',
            r'^rendben',
            r'^megvan',
            r'pontosan',
            r'természetesen'
        ],
        'sentiment': 'neutral_confirming',
        'description': 'Simple confirmations, acknowledgments, short agreements'
    }
}


def analyze_semantic_category(text):
    """
    Deep semantic analysis to determine the true category
    Returns: (category, confidence_score, reasoning)
    """
    text_lower = text.lower()
    
    # Clean text
    text_lower = re.sub(r'\[.*?\]', '', text_lower)  # Remove [áthallás] etc.
    text_lower = text_lower.strip()
    
    scores = {category: 0 for category in CLASSIFICATION_RULES.keys()}
    reasons = {category: [] for category in CLASSIFICATION_RULES.keys()}
    
    # Score each category
    for category, rules in CLASSIFICATION_RULES.items():
        # Check keywords
        for keyword in rules['keywords']:
            if keyword in text_lower:
                scores[category] += 2
                reasons[category].append(f"keyword: '{keyword}'")
        
        # Check patterns
        for pattern in rules.get('patterns', []):
            if re.search(pattern, text_lower):
                scores[category] += 3
                reasons[category].append(f"pattern: {pattern}")
        
        # Check anti-patterns (reduce score)
        for anti_pattern in rules.get('anti_patterns', []):
            if re.search(anti_pattern, text_lower):
                scores[category] -= 5
                reasons[category].append(f"ANTI-pattern: {anti_pattern}")
    
    # Additional contextual rules
    
    # Questions should end with ? or have question words at start
    if text_lower.endswith('?'):
        scores['question'] += 5
        reasons['question'].append("ends with ?")
    
    # Questions shouldn't be about the question itself
    if 'ez a kérdés' in text_lower or 'nehéz kérdés' in text_lower:
        scores['question'] -= 3
        scores['tension'] += 2
        reasons['tension'].append("meta-discussion about question")
    
    # Short affirmations are confirmations
    if len(text_lower.split()) <= 5 and any(word in text_lower for word in ['igen', 'jó', 'rendben', 'oké']):
        scores['confirmation'] += 3
        reasons['confirmation'].append("short affirmation")
    
    # Money amounts = excitement
    if re.search(r'\d+\s*(millió|ezer)', text_lower):
        scores['excitement'] += 4
        reasons['excitement'].append("mentions money amount")
    
    # "így van", "helyes" = excitement (positive feedback)
    if re.search(r'(így\s+(is\s+)?van|helyes)', text_lower):
        scores['excitement'] += 3
        reasons['excitement'].append("positive affirmation")
    
    # Long explanatory text = neutral or transition
    if len(text_lower.split()) > 30:
        scores['neutral'] += 2
        scores['transition'] += 1
        reasons['neutral'].append("long explanatory text")
    
    # Multiple "vagy" = tension (offering choices)
    vagy_count = text_lower.count(' vagy ')
    if vagy_count >= 2:
        scores['tension'] += vagy_count * 2
        reasons['tension'].append(f"multiple choices ({vagy_count}x 'vagy')")
    
    # "na" at start = transition
    if text_lower.startswith('na '):
        scores['transition'] += 3
        reasons['transition'].append("starts with 'na'")
    
    # Find best category
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    
    # Calculate confidence (0-100)
    total_score = sum(scores.values())
    confidence = (best_score / total_score * 100) if total_score > 0 else 0
    
    # If score is too low or confidence is too low, mark as neutral
    if best_score < 2 or confidence < 30:
        best_category = 'neutral'
        confidence = 50
    
    reasoning = "; ".join(reasons[best_category][:3])  # Top 3 reasons
    
    return best_category, confidence, reasoning


def reclassify_dataset():
    """Reclassify all audio samples based on semantic analysis"""
    
    print("="*70)
    print("DEEP SEMANTIC RECLASSIFICATION")
    print("István Vágó Milliomos Dataset")
    print("="*70)
    
    # Backup original metadata
    print(f"\n📋 Backing up metadata...")
    shutil.copy(METADATA_FILE, BACKUP_FILE)
    print(f"✓ Backup created: {BACKUP_FILE.name}")
    
    # Read metadata
    print(f"\n📖 Reading metadata...")
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='|')
        rows = list(reader)
    
    print(f"✓ Found {len(rows)} samples")
    
    # Analyze and reclassify
    print(f"\n🔍 Analyzing semantic content...\n")
    
    reclassifications = []
    stats = {
        'unchanged': 0,
        'changed': 0,
        'by_category': {}
    }
    
    for i, row in enumerate(rows, 1):
        audio_file = row['audio_file']
        text = row['text']
        speaker = row['speaker_name']
        
        # Get current category
        current_category = audio_file.split('/')[0]
        
        # Analyze
        new_category, confidence, reasoning = analyze_semantic_category(text)
        
        # Track stats
        if new_category not in stats['by_category']:
            stats['by_category'][new_category] = 0
        stats['by_category'][new_category] += 1
        
        if new_category != current_category:
            stats['changed'] += 1
            status = "🔄 CHANGE"
            
            reclassifications.append({
                'old_path': audio_file,
                'new_category': new_category,
                'text': text,
                'confidence': confidence,
                'reasoning': reasoning
            })
            
            print(f"[{i:2d}] {status}")
            print(f"     Old: {current_category}")
            print(f"     New: {new_category} ({confidence:.0f}% confidence)")
            print(f"     Text: {text[:70]}...")
            print(f"     Why: {reasoning}")
            print()
        else:
            stats['unchanged'] += 1
    
    # Show summary
    print("\n" + "="*70)
    print("RECLASSIFICATION SUMMARY")
    print("="*70)
    print(f"✓ Total samples analyzed: {len(rows)}")
    print(f"✓ Unchanged: {stats['unchanged']}")
    print(f"🔄 Changed: {stats['changed']}")
    print(f"\n📊 Category distribution:")
    for category, count in sorted(stats['by_category'].items()):
        print(f"   {category:15s}: {count:2d} samples")
    
    if stats['changed'] == 0:
        print("\n✅ No changes needed - all samples correctly classified!")
        return
    
    # Ask for confirmation
    print(f"\n{'='*70}")
    print(f"Found {stats['changed']} samples to reclassify.")
    print(f"This will:")
    print(f"  1. Move audio files to new category folders")
    print(f"  2. Update metadata.csv with new paths")
    print(f"  3. Keep backup at: {BACKUP_FILE.name}")
    
    response = input(f"\nProceed with reclassification? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Reclassification cancelled.")
        return
    
    # Perform reclassification
    print(f"\n🔧 Reclassifying files...")
    
    for reclass in reclassifications:
        old_path = DATASET_PATH / reclass['old_path']
        old_filename = old_path.name
        
        # Generate new path
        new_category_dir = DATASET_PATH / reclass['new_category']
        new_category_dir.mkdir(exist_ok=True)
        
        # Find next available number in new category
        existing_files = list(new_category_dir.glob(f"{reclass['new_category']}_*.wav"))
        if existing_files:
            numbers = [int(f.stem.split('_')[-1]) for f in existing_files]
            next_num = max(numbers) + 1
        else:
            next_num = 1
        
        new_filename = f"{reclass['new_category']}_{next_num:03d}.wav"
        new_path = new_category_dir / new_filename
        
        # Move file
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"   Moved: {reclass['old_path']} -> {reclass['new_category']}/{new_filename}")
            
            # Update reclass dict with actual new path
            reclass['new_path'] = f"{reclass['new_category']}/{new_filename}"
        else:
            print(f"   ⚠️  File not found: {old_path}")
            reclass['new_path'] = reclass['old_path']  # Keep old path
    
    # Update metadata.csv
    print(f"\n📝 Updating metadata.csv...")
    
    # Create lookup of old paths to new paths
    path_mapping = {r['old_path']: r['new_path'] for r in reclassifications}
    
    # Update rows
    for row in rows:
        if row['audio_file'] in path_mapping:
            row['audio_file'] = path_mapping[row['audio_file']]
    
    # Write updated metadata
    with open(METADATA_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['audio_file', 'text', 'speaker_name'], delimiter='|')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Metadata updated")
    
    # Save reclassification report
    report_file = DATASET_PATH / "reclassification_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("RECLASSIFICATION REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total changes: {len(reclassifications)}\n\n")
        
        for i, reclass in enumerate(reclassifications, 1):
            f.write(f"[{i}]\n")
            f.write(f"Old: {reclass['old_path']}\n")
            f.write(f"New: {reclass['new_path']}\n")
            f.write(f"Confidence: {reclass['confidence']:.0f}%\n")
            f.write(f"Reasoning: {reclass['reasoning']}\n")
            f.write(f"Text: {reclass['text']}\n")
            f.write("\n")
    
    print(f"✓ Report saved: {report_file.name}")
    
    print("\n" + "="*70)
    print("✅ RECLASSIFICATION COMPLETE!")
    print("="*70)
    print(f"📁 Files moved and organized by semantic category")
    print(f"📋 Metadata updated: {METADATA_FILE.name}")
    print(f"💾 Backup available: {BACKUP_FILE.name}")
    print(f"📄 Detailed report: {report_file.name}")


if __name__ == "__main__":
    reclassify_dataset()
