# Vocode: 3–10 Minute Video Walkthrough Script

**Track:** Track C: Contrastive Speech Analytics & Temporal Flaw Grounding  
**Target Video Duration:** 6 Minutes (within the 3–10 minute requirement)  
**Deliverable Document:** `docs/video_demo_script.md`

---

## Video Outline & Scene Timing

| Timestamp | Scene | Visual Cue / Screen Activity | Narration Focus |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:45** | **1. The Problem: Subjective Judging** | Title slide + Clip of forensics speech competition | Why speech judging is broken; vague feedback problem |
| **00:45 - 01:45** | **2. The Custom Dataset: 4-Tier Gradient** | VS Code view of `dataset/` + 4-tier audio waveforms | Masterclass vs synthetic flaws across 48 speeches |
| **01:45 - 02:45** | **3. Feature Extraction & Standardization** | Code walkthrough of 100 Hz Praat F0 & -20 LUFS DSP | Acoustic physics: F0 semitones, PAPR, 20% Pause Law |
| **02:45 - 04:30** | **4. Live Dashboard Walkthrough** | Chrome browser at `http://localhost:8501` | Landing page, Evaluator portal, MLK Masterclass vs Botched |
| **04:30 - 05:30** | **5. The Coach Tab & Chess.com Moves** | Zoom into Coach Tab, Jump buttons, Practice drills | Mistake cards, exact physical fixes, daily vocal routines |
| **05:30 - 06:00** | **6. Conclusion & Reproducibility** | GitHub repo overview, tests running, closing | Objective evaluation, reproducibility, future vision |

---

## Detailed Minute-by-Minute Script

### Scene 1: The Core Problem (00:00 – 00:45)
* **Visual:**  
  * Screen opens on title slide: **"Vocode: Objective Speech Analytics & Temporal Flaw Grounding"**.
  * Quick cut to a judge's ballot with handwritten notes: *"Good energy, but work on your presence."*
* **Speaker Narration:**  
  > *"Every year, millions of students and professionals compete in speech and debate, Toastmasters, and public keynotes. But public speaking evaluation is notoriously subjective. Two judges listening to the exact same speech will give wildly different scores based on personal bias. Worse, competitors receive vague advice like 'be more confident' or 'work on your pacing'—with zero objective feedback on where, when, or why they lost points.*
  > *Today, we introduce **Vocode**: an end-to-end multimodal speech evaluation engine that transforms oratorical judging into an exact, reproducible acoustic science."*

---

### Scene 2: The Custom Contrastive Dataset (00:45 – 01:45)
* **Visual:**  
  * Screen switches to terminal/VS Code showing `good speeches/` (48 curated masterclass speeches) and `dataset/approach3_experiment/`.
  * Highlight the paired folders: `tier0_masterclass.wav`, `tier1_distinguished.wav`, `tier2_proficient.wav`, and `tier3_botched.wav`.
  * Open `tier3_flaws.json` to show the exact millisecond bounding intervals.
* **Speaker Narration:**  
  > *"To solve the subjective evaluation gap, we constructed a custom contrastive dataset. We first sourced and transcribed 48 masterclass public speeches—from JFK and Martin Luther King Jr. to Charlie Chaplin and contemporary keynotes.*
  > *Next, we developed a 6-dimensional synthetic flaw injection engine using PSOLA pitch shifting and digital filtering. Rather than simple binary classification, we generated a continuous 4-tier contrastive gradient: Tier 0 Masterclass, Tier 1 Distinguished, Tier 2 Proficient, and Tier 3 Botched. Every flaw—from dead-air freezes to monotone flatlines and rushed cadences—is temporally grounded with millisecond precision in JSON manifests."*

---

### Scene 3: Acoustic Physics & 100 Hz Telemetry (01:45 – 02:45)
* **Visual:**  
  * Show `src/preprocessing/` and run `python -m unittest tests/test_preprocessing.py` in the terminal (11/11 tests passing green).
  * Show formula overlays: F0 semitones, PAPR crest factor, 20% Pause Law.
* **Speaker Narration:**  
  > *"Before evaluation, audio passes through a broadcast-grade standardization pipeline: 16,000 Hz sinc resampling, 70 Hz Butterworth high-pass filtering to remove sub-bass rumble, and EBU R128 loudness normalization to -20 LUFS. We specifically engineered this to preserve 100% of vocal transients and consonants.*
  > *From here, our engine extracts 100 Hz telemetry: micro-prosodic pitch tracking via Praat Parselmouth, PAPR crest factor for vocal punchiness, articulation rate in syllables per second, and adherence to the 20% Oratorical Pause Law.*
  > *These feed into our Non-Unilateral Scoring Engine across 5 core pillars, paired with a dynamic Leniency slider so judges can toggle between strict competition standards and encouraging novice coaching."*

---

### Scene 4: Live Interactive Dashboard Demonstration (02:45 – 04:30)
* **Visual:**  
  * Switch to browser at `http://localhost:8501`.
  * Show the interactive animated audio signal homepage.
  * Click the central **"Evaluator"** square to enter the main dashboard.
  * Show the glitch-animated **VOCODE** title.
  * In the sidebar, select preset: **"MLK: Tier 0 (Masterclass Baseline)"** and click **Evaluate Speech Performance**.
  * Walk through the Score Dial (9.2 / 10), the 5-Pillar Radar Chart, and the clean waveform.
  * Now select contrastive preset: **"MLK: Tier 3 (Botched: 4.8s Freeze + Monotone)"** and click **Evaluate**.
  * Point out the Score Dial dropping to **4.7 / 10**, the Paralyzing Silence gating ceiling capping the score, and the red/orange bands across the waveform timeline.
* **Speaker Narration:**  
  > *"Let's see Vocode in action on our live dashboard. On the homepage, an interactive particle canvas visualizes incoming audio signals. Clicking 'Evaluator' takes us to the evaluation suite.*
  > *Let's evaluate Dr. Martin Luther King Jr.'s masterclass delivery of 'I Have a Dream'. Notice the composite score: 9.2 out of 10. The radar chart shows near-perfect pitch modulation, optimal 20% pausing, and exceptional PAPR punchiness.*
  > *Now, let's load our contrastive Tier 3 botched mirror of the exact same speech text. Instantly, the score drops to 4.7 out of 10. Look at the breakdown waveform: Vocode immediately highlights the 4.8-second dead-air freeze in crimson red and flags the monotone flatline where pitch collapsed below 5 semitones."*

---

### Scene 5: The Forensic Coach Tab & Chess.com Move Cards (04:30 – 05:30)
* **Visual:**  
  * Click on the **🎯 Breakdown** tab.
  * Filter to **"Only Blunders (❌)"**. Click the **▶ Jump** button on the blunder card to show the audio player instantly seeking to the freeze timestamp.
  * Switch to the **🧑‍🏫 Coach** tab.
  * Scroll through:
    1. Executive Verdict banner.
    2. *"What Went Wrong & How to Fix It"* cards showing flaw, audience damage, and the exact physical fix.
    3. Re-play buttons.
    4. The 4 Daily Practice Routines (Diaphragmatic Breath Anchor, Pitch Staircase, 140 WPM Metronome Lock, Consonant Punch).
* **Speaker Narration:**  
  > *"Beyond grading, Vocode provides pedagogical coaching. In the Breakdown tab, every phrase is classified into Chess.com-style move cards: Brilliant, Great, Inaccuracies, Mistakes, and Blunders. Clicking 'Jump' seeks our HTML5 audio player directly to the exact millisecond of the mistake.*
  > *In the dedicated Coach tab, Vocode doesn't just tell you what went wrong—it teaches you how to fix it physically. For dead-air freezes, it prescribes the 1-second silent eye-contact reset. For monotone flatlines, it guides pitch staircasing on operative nouns. And below, it generates a personalized 7-day training plan with 4 targeted daily practice routines."*

---

### Scene 6: Conclusion & Reproducibility (05:30 – 06:00)
* **Visual:**  
  * Return to terminal showing `git status` and `requirements.txt`.
  * Show the Leonardo DiCaprio 2016 Oscar acceptance speech preset running live.
  * End on final slide with GitHub repository link.
* **Speaker Narration:**  
  > *"Vocode is completely reproducible, containerized with pinned dependencies, and fully operational across historic speeches, modern YouTube videos, and user audio uploads.*
  > *By bridging acoustic signal processing, contrastive dataset engineering, and empathetic coaching, Vocode sets a new standard for multimodal speech intelligence. Thank you."*
