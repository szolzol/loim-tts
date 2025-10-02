# 🎙️ István Vágó Audio Collection Guide

## Quick Reference

**Goal:** Collect 15-30 minutes of high-energy quiz show audio  
**Current Status:** 1.7 minutes  
**Gap:** Need 13-28 more minutes  
**Timeline:** 1-2 weeks for quality collection

---

## 🎯 Target Profile for István Vágó

### What Makes His Voice Unique?
- ✨ **High energy** - Enthusiastic quiz show presenter style
- 🎭 **Dramatic range** - Questions rise, celebrations peak
- ⚡ **Dynamic pacing** - Varies speed for tension/excitement
- 🎪 **Showmanship** - Engaging, theatrical delivery
- 🗣️ **Clear articulation** - Professional broadcast quality

### Why Zero-Shot Is Monotone
Zero-shot uses **generic prosody** from the base model trained on audiobooks and podcasts (neutral reading style). It doesn't capture:
- Rising question intonation
- Excitement peaks
- Tension building
- Emotional variation

**Fine-tuning teaches these patterns from your samples!**

---

## 📊 Collection Checklist

### Phase 1: Minimum Viable (10 minutes)
Target: Basic prosody improvement

- [ ] **Questions (4 min)** - 30-40 question clips
  - Rising intonation samples
  - "Ki volt...?", "Mikor...?", "Hol...?"
  - Mix of short/long questions
  
- [ ] **Excitement (3 min)** - 20-30 celebration clips
  - "Gratulálok!", "Helyes!"
  - Peak energy samples
  - Victory announcements
  
- [ ] **Tension (2 min)** - 15-20 suspense clips
  - "Az idő múlik...", "Gondolkozzon..."
  - Building anticipation
  
- [ ] **Neutral (1 min)** - 8-12 explanation clips
  - Transitions, rules
  - Calm delivery

### Phase 2: Production Quality (20 minutes)
Target: Commercial-grade results

- [ ] Double each category from Phase 1
- [ ] Add edge cases: disappointment, encouragement
- [ ] Include varied sentence structures
- [ ] Cover full emotional spectrum

### Phase 3: Professional (30+ minutes)
Target: ElevenLabs/Fish Audio level

- [ ] Comprehensive coverage of all quiz scenarios
- [ ] Multiple takes of key phrases
- [ ] Full prosodic diversity
- [ ] Edge case handling

---

## 🔍 Content Discovery Strategy

### YouTube Search Terms (Hungarian)

**Quiz Shows:**
```
"Vágó István Póker"
"Vágó István Maradj talpon"
"Vágó István Legyen Ön is milliomos"
"Vágó István kvíz műsorvezető"
"Vágó István kérdések"
"Vágó István helyes válasz"
```

**Content Types:**
```
"Vágó István legjobb pillanatok"  (best moments)
"Vágó István gratulálok"  (celebrations)
"Vágó István izgalmas"  (exciting moments)
"Vágó István questions"  (even in English!)
```

### Finding Clean Audio

**✅ LOOK FOR:**
- Studio recordings (TV shows)
- Clear foreground voice
- Minimal background music
- Recent shows (2010+)
- HD quality videos

**❌ AVOID:**
- Compilations with music overlay
- Interviews (wrong energy)
- Panel shows with crosstalk
- Low-quality uploads
- Auto-generated content

### Quality Indicators

**Video Quality Hints:**
- 720p+ resolution (better audio)
- Official channel uploads
- Professional production
- Clean thumbnails
- Recent upload dates

**Audio Quality Check:**
- Listen for background noise
- Check for music during speech
- Verify single speaker clarity
- Ensure no echo/reverb
- Confirm natural delivery

---

## 🛠️ Tools & Workflow

### Step 1: Download Videos

**Install yt-dlp:**
```powershell
pip install yt-dlp
```

**Download Audio (Best Quality):**
```powershell
# Single video
yt-dlp -f bestaudio --extract-audio --audio-format wav --audio-quality 0 "https://youtube.com/watch?v=VIDEO_ID"

# Playlist
yt-dlp -f bestaudio --extract-audio --audio-format wav --audio-quality 0 "https://youtube.com/playlist?list=PLAYLIST_ID"

# Download to specific folder
yt-dlp -f bestaudio --extract-audio --audio-format wav --audio-quality 0 -o "f:\CODE\tts-2\raw_downloads\%(title)s.%(ext)s" "URL"
```

**Tips:**
- Use `--playlist-items 1-5` to limit playlist downloads
- Use `-o` to organize downloads by content type
- Check file sizes (large = better quality)

### Step 2: Audio Editing (Audacity - Free)

**Download:** https://www.audacityteam.org/

**Import Audio:**
1. File > Open > Select downloaded WAV
2. Analyze waveform for speech segments

**Extract Clean Speech Segments:**

**Finding Good Clips:**
- Look for Vágó speaking WITHOUT music
- Avoid audience applause/laughter
- Skip overlapping speakers
- Target 4-8 second segments

**Selection Process:**
1. Click and drag to select segment
2. Play to verify (Space bar)
3. Adjust selection edges (fine-tune)
4. Export: File > Export > Export Selected Audio

**Keyboard Shortcuts:**
- `Space` - Play/Pause
- `C` - Play selection
- `Ctrl+1` - Zoom to selection
- `Ctrl+B` - Add label
- `Ctrl+Shift+E` - Export multiple

### Step 3: Batch Processing Pipeline

**Noise Reduction (One-time per file):**
1. Select 1-2 sec of silence (background noise)
2. Effect > Noise Reduction > Get Noise Profile
3. Select all (Ctrl+A)
4. Effect > Noise Reduction > Apply
5. Settings: 
   - Noise reduction: 12 dB
   - Sensitivity: 6.00
   - Frequency smoothing: 3 bands

**Per-Clip Processing:**
1. **Trim Silence:** Effect > Truncate Silence
   - Threshold: -40 dB
   - Duration: 0.3 seconds
   
2. **Normalize:** Effect > Normalize
   - Normalize peak: -1.0 dB
   - Remove DC offset: ✓
   
3. **Check Quality:**
   - Listen at 0.5x speed (check for artifacts)
   - Verify no clicks/pops
   - Ensure smooth start/end

**Export Settings:**
- Format: WAV (Microsoft) 16-bit PCM
- Sample Rate: 22050 Hz
- Channels: Mono

### Step 4: File Organization

**Naming Convention:**
```
{category}_{number}_{content_hint}.wav

Examples:
question_01_ki_volt.wav
excitement_01_gratulalok.wav
tension_01_ido_mulik.wav
neutral_01_magyarazat.wav
```

**Folder Structure:**
```
f:\CODE\tts-2\
├── new_collection/
│   ├── questions/
│   │   ├── question_01_ki_volt.wav
│   │   ├── question_02_mikor.wav
│   │   └── ...
│   ├── excitement/
│   │   ├── excitement_01_gratulalok.wav
│   │   ├── excitement_02_helyes.wav
│   │   └── ...
│   ├── tension/
│   │   ├── tension_01_ido_mulik.wav
│   │   └── ...
│   └── neutral/
│       └── ...
```

### Step 5: Transcription

**Option A: Whisper AI (Then Correct)**
```powershell
# Use existing script
python scripts\transcribe_audio.py
```

**Option B: Manual (Most Accurate)**
1. Play audio slowly (0.7x speed in Audacity)
2. Type exactly what you hear
3. Include ALL punctuation (affects prosody!)
4. Use proper Hungarian diacritics

**Transcription Rules:**
```
✅ GOOD:
"Ki volt az, aki 1848-ban vezette a forradalmat?"

❌ BAD:
"ki volt az aki 1848-ban vezette a forradalmat"
(missing punctuation, no capitals)

✅ GOOD:
"Gratulálok! Helyes válasz!"

❌ BAD:
"Gratulálok helyes valasz"
(wrong punctuation, missing diacritics)
```

**Critical Punctuation:**
- `.` - Falling intonation (statement)
- `?` - Rising intonation (question) ← **ESSENTIAL!**
- `!` - High energy (excitement) ← **ESSENTIAL!**
- `,` - Pause, continuation
- `...` - Hesitation, suspense

### Step 6: Quality Validation

**Audio Checks:**
```powershell
# Run our analysis tool
python scripts\prepare_dataset.py --analyze-only
```

**Manual Verification:**
- [ ] All files mono 22050 Hz
- [ ] No clipping (waveform doesn't hit edges)
- [ ] Consistent volume levels
- [ ] No background music during speech
- [ ] Clean start/end (no cutoff words)

**Transcription Checks:**
- [ ] 100% word accuracy
- [ ] All diacritics correct (á, é, í, ó, ö, ő, ú, ü, ű)
- [ ] Punctuation matches delivery
- [ ] No spelling errors
- [ ] Matches audio exactly

---

## 📈 Progress Tracking

### Collection Log Template

```markdown
## Collection Session: [DATE]

**Source:** [YouTube URL or description]
**Duration downloaded:** [XX minutes]
**Usable clips extracted:** [XX clips]
**Total duration added:** [X.X minutes]

### Clips Added:
- Questions: X clips, X.X minutes
- Excitement: X clips, X.X minutes
- Tension: X clips, X.X minutes
- Neutral: X clips, X.X minutes

**Running Total:** X.X / 20.0 minutes target

### Notes:
- Quality issues encountered
- Best clips found
- Areas still needed
```

### Dataset Inventory

**Current Status:**
```
Questions:     X.X min (Target: 8 min)  [====      ] 40%
Excitement:    X.X min (Target: 6 min)  [===       ] 30%
Tension:       X.X min (Target: 4 min)  [==        ] 20%
Neutral:       X.X min (Target: 2 min)  [=         ] 10%
────────────────────────────────────────────────────
Total:         1.7 min (Target: 20 min) [=         ] 8.5%
```

---

## ⚡ Quick Tips

### For Fastest Collection:

1. **Find ONE good source** (20-30 min show)
   - Download entire episode
   - Extract 10-15 clips systematically
   - Get 5+ minutes in one session

2. **Batch similar content**
   - Extract all questions from one video
   - Then all excitement clips
   - More efficient than switching

3. **Quality over quantity**
   - 5 perfect clips > 20 mediocre ones
   - Skip anything with background noise
   - Don't waste time cleaning bad audio

4. **Use templates**
   - Save Audacity macro for processing
   - Use consistent export settings
   - Copy filename patterns

### Common Mistakes to Avoid:

❌ **Collecting too much neutral speech**
- Quiz shows need energy!
- Boring clips won't help prosody

❌ **Ignoring transcription quality**
- Bad transcriptions = bad training
- Missing punctuation = wrong prosody

❌ **Using low-quality sources**
- YouTube auto-transcripts are unreliable
- Compressed audio hurts results

❌ **Inconsistent processing**
- Different sample rates break training
- Mixed mono/stereo causes issues

---

## 🎬 Example YouTube Videos (Search These)

**Recommended Shows to Mine:**

1. **"Maradj talpon" (Stay Standing)**
   - Great question pacing
   - Clear excitement moments
   - Good energy throughout

2. **"Legyen Ön is milliomos" (Who Wants to Be a Millionaire)**
   - Excellent tension building
   - Clear question/answer structure
   - Professional audio quality

3. **"Póker" (Poker quiz show)**
   - Vágó's signature show
   - High production value
   - Lots of usable content

**Search Strategy:**
```
1. Search: "Vágó István [show name] teljes adás"  (full episode)
2. Filter: This year (for quality)
3. Sort: By view count
4. Check: Official channels first
5. Download: Best quality available
```

---

## 🚀 Next Steps After Collection

Once you have 15-20 minutes:

1. **Organize files:**
   ```powershell
   # Copy to source_clips
   Copy-Item "new_collection\*\*.wav" "source_clips\"
   ```

2. **Update metadata:**
   ```powershell
   # Run transcription
   python scripts\transcribe_audio.py
   
   # Review and correct
   # Edit processed_clips\metadata.csv
   ```

3. **Validate dataset:**
   ```powershell
   # Check quality
   python scripts\prepare_dataset.py
   
   # Review output statistics
   ```

4. **Start fine-tuning:**
   ```powershell
   # Train on expanded dataset
   python scripts\train_xtts.py
   ```

5. **Monitor progress:**
   - Check samples every 5 epochs
   - Listen for prosody improvement
   - Compare to zero-shot baseline

---

## 💡 Pro Tips from Experience

**Finding Gold:**
- Episode climaxes have best energy
- Final answer reveals = pure excitement
- Wrong answer moments = good tension
- Opening segments = best questions

**Audio Quality Shortcuts:**
- Official broadcaster channels → better quality
- Newer shows → higher production value
- Quiz shows → cleaner audio than talk shows
- Studio recordings → better than field recordings

**Efficiency Hacks:**
- Use 1.5x playback speed to scan videos faster
- Mark good timestamps before extracting
- Process in batches (10 clips at once)
- Save Audacity presets for consistency

**Red Flags (Skip These):**
- Heavy music throughout
- Poor audio balance (music louder than voice)
- Multiple speakers talking over each other
- Audience noise dominating
- Echo or reverb issues
- Old recordings (VHS quality)

---

## 📞 Resources

**Tools:**
- **yt-dlp:** https://github.com/yt-dlp/yt-dlp
- **Audacity:** https://www.audacityteam.org/
- **VLC Media Player:** For quick preview

**Hungarian Resources:**
- **MTV Archive:** https://mediaklikk.hu/
- **YouTube:** Search "Vágó István"
- **Hungarian TV Networks:** TV2, RTL Klub

**Community:**
- Coqui TTS Discord: https://discord.gg/coqui
- TTS Subreddit: r/TTSmodding

---

## ✅ Ready to Start?

**Immediate Action Plan:**

1. **Today (2 hours):**
   - Search YouTube for 3-5 good videos
   - Download best quality
   - Extract 10-15 clips
   - Target: +5 minutes

2. **This Week (1 hour/day):**
   - Continue extracting clips
   - Focus on questions and excitement
   - Target: +10 minutes total

3. **Weekend:**
   - Transcribe all new clips
   - Validate quality
   - Organize for training
   - Target: 15-20 min dataset ready

**You're ready to collect professional-quality training data!** 🎯

Remember: **Quality > Quantity** - 15 minutes of perfect clips beats 30 minutes of mediocre ones!
