# Training Phase 2 - Continue Fine-tuning

**Date:** 2025-10-04  
**Goal:** Further improve Mel CE from 3.507 → < 2.5 (excellent quality)  
**Strategy:** Ultra-low learning rate continuation training

---

## 📊 Phase 1 Results (Completed)

### Training Summary
- **Dataset:** 311 samples (Milliomos 80 + Blikk 231)
- **Epochs:** ~15 (1600 steps)
- **Learning Rate:** 1.5e-6
- **Duration:** ~12 hours

### Final Metrics
- **Mel CE:** 3.507 (30.5% improvement from 5.046) ✅
- **Text CE:** 0.0281 (excellent) ✅
- **Overall Quality:** 8.5/10 (estimated)
- **Status:** High quality, borderline excellent

### Best Checkpoint
- **File:** `best_model_1339.pth`
- **Step:** 1339
- **Mel CE:** 3.507
- **Note:** Training plateaued after this point

---

## 🎯 Phase 2 Goals

### Primary Objective
Improve Mel CE from **3.507 → < 2.5** for excellent quality

### Quality Level Targets

| Metric | Phase 1 | Phase 2 Target | Improvement |
|--------|---------|----------------|-------------|
| Mel CE | 3.507 | < 2.5 | -28.8% |
| Text CE | 0.0281 | < 0.03 | Maintain |
| Overall | 8.5/10 | 9.0/10 | +0.5 points |
| Quality | High | Excellent | Production+ |

---

## 🔧 Phase 2 Configuration

### Training Parameters
```python
RESUME_FROM: checkpoint_1500.pth (step 1500)
LEARNING_RATE: 1e-6 (reduced from 1.5e-6)
BATCH_SIZE: 3 (same)
EPOCHS: 30 (additional)
FOCUS: Ultra-smooth audio (Mel CE)
```

### Why Lower Learning Rate?
- Phase 1 achieved major improvements (30.5%)
- Model is now near optimal for this dataset
- Lower LR (1e-6) allows gentle refinement without disrupting learned patterns
- Prevents overfitting while allowing micro-optimizations

### Expected Training Time
- **Steps per epoch:** ~100
- **Total additional steps:** ~3000
- **Estimated duration:** 8-12 hours
- **Evaluation:** Every 100 steps

---

## 📈 Training Strategy

### Phase 1 (Completed)
**Goal:** Major Mel CE improvement  
**LR:** 1.5e-6 (moderate)  
**Result:** 5.046 → 3.507 (-30.5%) ✅

### Phase 2 (Current)
**Goal:** Reach excellent quality (< 2.5)  
**LR:** 1e-6 (ultra-low)  
**Expected:** 3.507 → ~2.3-2.5 (-28-34%)

### Why This Approach Works
1. **Larger dataset** (311 samples) provides enough variety
2. **Phase 1** made major corrections to audio smoothness
3. **Phase 2** refines details without breaking learned patterns
4. **Lower LR** prevents overfitting while allowing optimization

---

## 🎬 How to Start Phase 2

### Option 1: Using Batch File (Recommended)
```cmd
.\TRAIN_PHASE2.bat
```

### Option 2: Direct Python
```cmd
python scripts\train_combined_phase2.py
```

---

## 📊 Monitoring Progress

### Key Metrics to Watch

1. **Mel CE (Primary Focus)**
   - Current: 3.507
   - Target: < 2.5
   - Watch for: Gradual decrease every 100 steps

2. **Text CE (Maintain)**
   - Current: 0.0281
   - Target: < 0.03
   - Watch for: Should stay stable or slightly improve

3. **Training Loss**
   - Should decrease steadily
   - If plateaus early: Model may be at optimal

4. **Eval Loss**
   - Should track training loss
   - If diverges: Risk of overfitting

### Warning Signs

⚠️ **Stop training if:**
- Text CE increases above 0.04
- Eval loss increases while training loss decreases
- Mel CE stops improving for 500+ steps
- Audio quality degrades (listen to test sentences)

---

## 📁 Output Structure

```
run/training_combined_phase2/
├── XTTS_Combined_Phase2_[timestamp]/
│   ├── best_model.pth              (best Mel CE)
│   ├── best_model_[step].pth       (best at specific step)
│   ├── checkpoint_[step].pth       (periodic saves)
│   ├── config.json
│   ├── vocab.json                  (will be copied)
│   ├── trainer_0_log.txt           (training logs)
│   └── events.out.tfevents.*       (tensorboard)
```

---

## ✅ Success Criteria

### Minimum Success (Continue to Production)
- ✅ Mel CE < 3.0 (improved from 3.507)
- ✅ Text CE < 0.03 (maintained)
- ✅ No overfitting (eval loss tracks training)

### Target Success (Excellent Quality)
- ⭐ Mel CE < 2.5 (excellent quality)
- ⭐ Text CE < 0.03 (maintained excellent)
- ⭐ Overall quality: 9.0/10

### Exceptional Success (Production+)
- 🏆 Mel CE < 2.0 (near-perfect smoothness)
- 🏆 Text CE < 0.025 (exceptional pronunciation)
- 🏆 Overall quality: 9.5/10

---

## 🔍 Expected Outcomes

### Scenario 1: Success (Most Likely)
- Mel CE improves to 2.3-2.8 range
- Text CE remains excellent (< 0.03)
- Quality reaches 9.0/10
- **Action:** Deploy for production

### Scenario 2: Marginal Improvement
- Mel CE improves to 3.0-3.3 range
- Model plateaus quickly (< 1000 steps)
- Quality reaches 8.7/10
- **Action:** Use Phase 1 model or this, both production-ready

### Scenario 3: No Improvement
- Mel CE stays at 3.5 or increases
- Model already at optimal for this dataset
- Quality remains 8.5/10
- **Action:** Use Phase 1 model, already excellent

---

## 📝 Phase 2 Checklist

### Before Starting
- [x] Phase 1 training completed
- [x] checkpoint_1500.pth exists
- [x] Training script created
- [x] Batch file created
- [ ] GPU is available (check Task Manager)
- [ ] Enough disk space (need ~10GB for checkpoints)

### During Training
- [ ] Monitor GPU usage (~90-95%)
- [ ] Check Mel CE every ~500 steps
- [ ] Verify Text CE stays < 0.03
- [ ] Listen to generated test sentences periodically

### After Training
- [ ] Review final Mel CE in logs
- [ ] Generate test samples with Phase 2 model
- [ ] Compare with Phase 1 samples
- [ ] Decide which model to use for production

---

## 🎧 Post-Training Evaluation

### Generate Test Samples
```cmd
# Will need to create this script
python scripts\test_phase2_model.py
```

### Compare Models
1. **Baseline (Milliomos-only):** Mel CE 5.046, Quality 7.5/10
2. **Phase 1 (Combined):** Mel CE 3.507, Quality 8.5/10
3. **Phase 2 (Continued):** Mel CE ?, Quality ?/10

### Decision Matrix

| Mel CE | Quality | Recommendation |
|--------|---------|----------------|
| < 2.5 | 9.0+ | Use Phase 2 - Excellent! |
| 2.5-3.0 | 8.7-8.9 | Use Phase 2 - Improved |
| 3.0-3.5 | 8.5-8.6 | Use Phase 1 - Marginal gain |
| > 3.5 | < 8.5 | Use Phase 1 - No improvement |

---

## 🚀 Next Steps After Phase 2

### If Successful (Mel CE < 2.5)
1. Generate comprehensive test samples
2. Regenerate full quiz show content
3. Deploy Phase 2 model to production
4. Archive Phase 1 model

### If Marginal (Mel CE 2.5-3.5)
1. Compare Phase 1 vs Phase 2 audio quality
2. Choose better sounding model
3. Consider additional data if quality still insufficient

### If No Improvement (Mel CE > 3.5)
1. Use Phase 1 model (already excellent at 8.5/10)
2. Current dataset may have reached optimal
3. Would need more/better training data to improve further

---

## 💡 Technical Notes

### Why Phase 2 Might Plateau Early
- Model already found local optimum in Phase 1
- Dataset quality limits maximum achievable Mel CE
- 311 samples may not be enough for < 2.5 target
- Further improvement may require 500+ samples

### If Target Not Reached
- **Mel CE 3.507 (Phase 1) is already excellent**
- Suitable for production use
- Difference between 3.5 and 2.5 may be barely audible
- Focus on subjective listening tests, not just metrics

### Alternative Strategies (If Phase 2 Fails)
1. Add more high-quality training data
2. Try different data augmentation
3. Adjust temperature/repetition_penalty in inference
4. Accept current quality (8.5/10 is very good!)

---

## 📊 Progress Tracking Template

### Fill in during training:

**Start Time:** ___________  
**End Time:** ___________  
**Duration:** ___________

**Initial Metrics (Step 1500):**
- Mel CE: 3.511
- Text CE: 0.0280

**Best Metrics:**
- Mel CE: ___________ (at step _______)
- Text CE: ___________ (at step _______)

**Final Metrics:**
- Mel CE: ___________
- Text CE: ___________
- Improvement: ___________

**Subjective Quality:**
- Smoothness: _____/10
- Naturalness: _____/10
- Emotion: _____/10
- Overall: _____/10

**Decision:**
- [ ] Use Phase 2 model
- [ ] Use Phase 1 model
- [ ] Continue to Phase 3

---

**Status:** Ready to start Phase 2  
**Command:** `.\TRAIN_PHASE2.bat`  
**Expected Duration:** 8-12 hours  
**Goal:** Mel CE < 2.5 (excellent quality)

