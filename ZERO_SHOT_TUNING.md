# 🎛️ Zero-Shot Parameter Tuning Guide

## Quick Reference for István Vágó Voice

**Current Issues:** Slow, monotone speech lacking quiz show energy  
**Solution:** Optimize inference parameters and reference audio selection

---

## 🎚️ Key Parameters

### 1. **Temperature** (Most Important for Expressiveness!)

Controls variation and expressiveness in speech.

| Value | Effect | Use Case |
|-------|--------|----------|
| 0.3-0.5 | Very stable, monotone | Audiobooks, neutral narration |
| 0.65-0.75 | Default, balanced | General purpose |
| **0.85-0.95** | **More dynamic, expressive** | **Quiz shows, excitement** ⭐ |
| 1.0+ | Very variable, may be unstable | Experimental |

**Recommended for Vágó:** `0.90-0.95`

```python
TEMPERATURE = 0.95  # Maximum expressiveness without instability
```

**What it does:**
- ✅ Adds natural pitch variation
- ✅ Creates emotional dynamics
- ✅ Prevents flat/robotic delivery
- ⚠️ Too high (>1.0) = unpredictable/garbled

---

### 2. **Speed** (Fix Slow Speech!)

Controls speech rate directly.

| Value | Effect | Speed Change |
|-------|--------|--------------|
| 0.8 | Slower | -20% |
| 1.0 | Normal (default) | baseline |
| **1.1-1.15** | **Slightly faster** | **+10-15%** ⭐ |
| 1.2-1.3 | Faster | +20-30% |
| 1.5+ | Very fast | May lose clarity |

**Recommended for Vágó:** `1.10-1.15`

```python
SPEED = 1.15  # 15% faster speech
```

**What it does:**
- ✅ Matches natural quiz show pacing
- ✅ Adds energy and urgency
- ✅ Reduces monotony
- ⚠️ Too high (>1.3) = rushed/unclear

---

### 3. **Repetition Penalty**

Prevents word/phrase repetition artifacts.

| Value | Effect |
|-------|--------|
| 1.0-3.0 | Low penalty, may repeat |
| 5.0 | Default, balanced |
| **7.0-10.0** | **Higher penalty, cleaner** ⭐ |

**Recommended for Vágó:** `7.0-8.0`

```python
REPETITION_PENALTY = 7.0  # Reduce repetition artifacts
```

**What it does:**
- ✅ Prevents stuttering/looping
- ✅ Cleaner output
- ⚠️ Too high (>15) = unnatural pauses

---

### 4. **Length Penalty**

Controls generated audio duration vs text length.

| Value | Effect |
|-------|--------|
| 0.5-0.8 | Shorter, faster |
| **1.0** | **Default, natural** ⭐ |
| 1.2-1.5 | Longer, slower |

**Recommended for Vágó:** `1.0` (keep default)

```python
LENGTH_PENALTY = 1.0  # Natural duration
```

---

## 🎤 Reference Audio Selection

**Critical for Quality!** Your reference clips define the voice characteristics.

### Current Setup:
```python
REFERENCE_AUDIO = [
    "vago_vagott_01.wav",  # 
    "vago_vagott_02.wav",  # 
    "vago_vagott_03.wav",  # 
]
```

### Optimization Strategy:

#### Step 1: Analyze Your Clips

Listen to each clip and rate:
- **Energy level** (1-10): How enthusiastic?
- **Clarity** (1-10): How clear is speech?
- **Prosody** (1-10): Natural intonation?
- **Background** (1-10): How clean? (10=silent)

#### Step 2: Select Best Clips

**Criteria:**
1. ✅ **High energy** (quiz show excitement)
2. ✅ **Clear articulation** (no mumbling)
3. ✅ **Dynamic prosody** (rising/falling tones)
4. ✅ **Clean audio** (minimal noise)

**How many clips?**
- **1 clip:** Fast, but limited variation
- **2-3 clips:** **Optimal balance** ⭐
- **4+ clips:** More robust, but slower

#### Step 3: Avoid These:

❌ Monotone clips (flat delivery)  
❌ Mumbled/unclear speech  
❌ Background music/noise  
❌ Very long clips (>15 sec)  
❌ Multiple speakers  

### Recommended Configuration:

```python
# Option A: Maximum Energy (2 clips)
REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",  # Most energetic
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",  # High expression
]

# Option B: Balanced Quality (3 clips)
REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",  # Energy
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",  # Expression
    SOURCE_CLIPS_DIR / "vago_vagott_03.wav",  # Clarity
]

# Option C: Try different combinations!
REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "2_vago_finetune2.wav",
    SOURCE_CLIPS_DIR / "5_vago_finetune2.wav",
]
```

---

## 🧪 Experimentation Workflow

### Quick Test Cycle

1. **Modify parameters** in `zero_shot_inference.py`
2. **Run inference:**
   ```powershell
   python scripts\zero_shot_inference.py
   ```
3. **Listen to output** in `output/zero_shot/`
4. **Iterate:** Adjust and retest

### A/B Testing Template

Test one parameter at a time:

```python
# Test 1: Baseline
TEMPERATURE = 0.75
SPEED = 1.0

# Test 2: More expressive
TEMPERATURE = 0.90
SPEED = 1.0

# Test 3: Faster
TEMPERATURE = 0.90
SPEED = 1.15

# Test 4: Maximum energy
TEMPERATURE = 0.95
SPEED = 1.15
```

Run each configuration and compare outputs.

---

## 📊 Recommended Configurations

### Configuration 1: **Balanced** (Default)
```python
TEMPERATURE = 0.85
SPEED = 1.05
REPETITION_PENALTY = 7.0
LENGTH_PENALTY = 1.0

REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",
    SOURCE_CLIPS_DIR / "vago_vagott_03.wav",
]
```
**Best for:** General quiz show use

---

### Configuration 2: **Maximum Energy** ⚡
```python
TEMPERATURE = 0.95
SPEED = 1.15
REPETITION_PENALTY = 7.0
LENGTH_PENALTY = 1.0

REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",  # Most energetic only
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",
]
```
**Best for:** Excitement, celebrations, "Gratulálok!"

---

### Configuration 3: **Fast & Clear** 🏃
```python
TEMPERATURE = 0.80
SPEED = 1.20
REPETITION_PENALTY = 8.0
LENGTH_PENALTY = 0.95

REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_03.wav",  # Clear articulation
]
```
**Best for:** Quick questions, rapid-fire quiz format

---

### Configuration 4: **Dramatic** 🎭
```python
TEMPERATURE = 0.95
SPEED = 1.0  # Normal speed for emphasis
REPETITION_PENALTY = 7.0
LENGTH_PENALTY = 1.1  # Slightly longer for drama

REFERENCE_AUDIO = [
    SOURCE_CLIPS_DIR / "vago_vagott_05.wav",
    SOURCE_CLIPS_DIR / "vago_vagott_02.wav",
]
```
**Best for:** Tension building, "Az idő múlik..."

---

## 🎯 Optimization Checklist

Try these in order:

- [ ] **Step 1:** Increase TEMPERATURE to 0.90
  - Test: Does it sound more expressive?
  
- [ ] **Step 2:** Increase SPEED to 1.15
  - Test: Is pacing better?
  
- [ ] **Step 3:** Select 2 most energetic reference clips
  - Test: More quiz show energy?
  
- [ ] **Step 4:** Adjust REPETITION_PENALTY to 7.0
  - Test: Fewer artifacts?
  
- [ ] **Step 5:** Fine-tune based on results
  - Test: Overall quality acceptable?

---

## 🔬 Advanced Tuning

### For Different Text Types:

**Questions (rising intonation):**
```python
TEMPERATURE = 0.90  # Dynamic
SPEED = 1.1
```

**Excitement (high energy):**
```python
TEMPERATURE = 0.95  # Maximum variation
SPEED = 1.15  # Faster for excitement
```

**Explanations (neutral):**
```python
TEMPERATURE = 0.75  # More stable
SPEED = 1.0
```

**Tension (dramatic pauses):**
```python
TEMPERATURE = 0.85
SPEED = 0.95  # Slightly slower
LENGTH_PENALTY = 1.1  # Longer pauses
```

---

## 📈 Expected Results

### Current (Slow & Monotone):
- ❌ Flat delivery
- ❌ Slow pacing
- ❌ Lacks energy
- ❌ Generic prosody

### After Optimization:
- ✅ More dynamic delivery
- ✅ Faster, natural pacing
- ✅ Better energy
- ✅ Improved prosody

### With Fine-Tuning (Future):
- ✅ Perfect voice match
- ✅ Natural quiz show style
- ✅ Full emotional range
- ✅ Context-aware prosody

---

## 💡 Pro Tips

1. **Test incrementally:** Change one parameter at a time
2. **Use diverse test phrases:** Questions, excitement, neutral
3. **Listen critically:** Compare to original Vágó recordings
4. **Document results:** Keep notes on what works
5. **Reference audio matters most:** 80% of quality comes from good references

### Common Issues & Fixes:

**Issue:** Still too slow
- **Fix:** Increase SPEED to 1.2-1.25

**Issue:** Sounds robotic
- **Fix:** Increase TEMPERATURE to 0.95

**Issue:** Garbled/unstable
- **Fix:** Decrease TEMPERATURE to 0.85

**Issue:** Word repetition
- **Fix:** Increase REPETITION_PENALTY to 8-10

**Issue:** Wrong voice character
- **Fix:** Use different reference audio clips

---

## 🚀 Quick Command Reference

### Test Current Configuration:
```powershell
python scripts\zero_shot_inference.py
```

### Generate Single Phrase (Interactive):
```powershell
python scripts\zero_shot_inference.py
# Choose option 2: Interactive mode
```

### Batch Generate with New Parameters:
1. Edit `scripts/zero_shot_inference.py`
2. Modify TEMPERATURE, SPEED, etc.
3. Run: `python scripts\zero_shot_inference.py`
4. Compare outputs in `output/zero_shot/`

---

## 📝 Parameter Tuning Log Template

Keep track of experiments:

```
Date: 2025-10-02
Test: Increased temperature and speed

Parameters:
- TEMPERATURE: 0.95 (was 0.75)
- SPEED: 1.15 (was 1.0)
- REPETITION_PENALTY: 7.0
- REFERENCE_AUDIO: vago_vagott_02, 05

Results:
- Expressiveness: Improved ✅
- Speed: Much better ✅
- Energy: Higher ✅
- Quality: Good, slight artifacts

Next Steps:
- Try SPEED 1.10 for stability
- Test with different reference clips
```

---

## ✅ What to Expect

**Zero-shot optimization can improve:**
- Speech rate (speed parameter)
- Expressiveness (temperature parameter)
- Reference voice characteristics (audio selection)

**Zero-shot CANNOT match:**
- Perfect voice similarity (needs fine-tuning)
- Learned prosody patterns (needs training)
- Context-aware delivery (needs fine-tuning)

**Bottom Line:**
- **Quick wins:** 30-50% improvement with parameter tuning
- **Production quality:** Requires 15-30 min dataset + fine-tuning

---

## 🎓 Next Steps

1. **Immediate:** Test optimized parameters (see below)
2. **Short-term:** Collect 10-15 min of energetic audio
3. **Long-term:** Fine-tune for production quality

---

**Ready to test? Run the optimized script now!**

```powershell
python scripts\zero_shot_inference.py
```

Listen to the results and compare to previous outputs! 🎯
