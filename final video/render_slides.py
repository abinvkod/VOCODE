import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SLIDES_DIR = "final video/slides"
os.makedirs(SLIDES_DIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080

def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_base_canvas():
    # Deep slate tech background
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 14, 23))
    draw = ImageDraw.Draw(img)
    # Subtle gradient or grid lines
    for y in range(0, HEIGHT, 60):
        draw.line([0, y, WIDTH, y], fill=(15, 23, 36), width=1)
    for x in range(0, WIDTH, 60):
        draw.line([x, 0, x, HEIGHT], fill=(15, 23, 36), width=1)
    return img, draw

def draw_header(draw, title_text, category_text="TRACK C: CONTRASTIVE SPEECH ANALYTICS"):
    # Header bar
    draw.rectangle([0, 0, WIDTH, 84], fill=(14, 18, 28))
    draw.line([0, 84, WIDTH, 84], fill=(30, 41, 59), width=2)
    
    font_cat = get_font(18, bold=True)
    font_title = get_font(28, bold=True)
    
    draw.text((60, 16), category_text.upper(), font=font_cat, fill=(56, 189, 248))
    draw.text((60, 42), title_text, font=font_title, fill=(248, 250, 252))
    
    # Right badge
    font_badge = get_font(16, bold=True)
    badge = "VOCODE ENGINE • 2026"
    bbox = font_badge.getbbox(badge)
    bw = bbox[2] - bbox[0] + 32
    bx = WIDTH - 60 - bw
    draw.rounded_rectangle([bx, 22, WIDTH - 60, 62], radius=8, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((bx + 16, 32), badge, font=font_badge, fill=(56, 189, 248))

def draw_footer(draw, text="VOCODE: Contrastive Speech Analytics & Temporal Flaw Grounding"):
    draw.rectangle([0, HEIGHT - 44, WIDTH, HEIGHT], fill=(14, 18, 28))
    draw.line([0, HEIGHT - 44, WIDTH, HEIGHT - 44], fill=(30, 41, 59), width=1)
    font_foot = get_font(15, bold=False)
    draw.text((60, HEIGHT - 32), text, font=font_foot, fill=(148, 163, 184))
    draw.text((WIDTH - 380, HEIGHT - 32), "Multimodal AI Hackathon 2026", font=font_foot, fill=(100, 116, 139))

def draw_card(draw, box, fill=(18, 24, 38), outline=(37, 47, 66), radius=16, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

# ==============================================================================
# SLIDE 1A: TITLE CARD
# ==============================================================================
def render_slide_1a():
    img = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 20))
    draw = ImageDraw.Draw(img)
    
    # Background glowing radial motif
    for r in range(450, 0, -15):
        alpha = int(25 * (1 - r / 450))
        draw.ellipse([WIDTH//2 - r, HEIGHT//2 - r - 40, WIDTH//2 + r, HEIGHT//2 + r - 40], outline=(14 + alpha, 40 + alpha, 70 + alpha), width=3)
    
    # Hackathon Banner
    f_badge = get_font(20, bold=True)
    badge_txt = "MULTIMODAL AI HACKATHON 2026  •  TRACK C"
    bbox = f_badge.getbbox(badge_txt)
    bw = bbox[2] - bbox[0] + 40
    bx = (WIDTH - bw) // 2
    draw.rounded_rectangle([bx, 220, bx + bw, 266], radius=23, fill=(19, 36, 62), outline=(56, 189, 248), width=2)
    draw.text((bx + 20, 232), badge_txt, font=f_badge, fill=(56, 189, 248))
    
    # Main Title
    f_title = get_font(84, bold=True)
    title = "VOCODE"
    bbox = f_title.getbbox(title)
    draw.text(((WIDTH - (bbox[2]-bbox[0])) // 2, 290), title, font=f_title, fill=(255, 255, 255))
    
    # Subtitle
    f_sub = get_font(34, bold=True)
    sub = "Contrastive Speech Analytics & Temporal Flaw Grounding"
    bbox = f_sub.getbbox(sub)
    draw.text(((WIDTH - (bbox[2]-bbox[0])) // 2, 400), sub, font=f_sub, fill=(56, 189, 248))
    
    # Tagline
    f_tag = get_font(24, bold=False)
    tag = "A Physics-Grounded Multimodal Framework for Objective Oratorical Evaluation"
    bbox = f_tag.getbbox(tag)
    draw.text(((WIDTH - (bbox[2]-bbox[0])) // 2, 460), tag, font=f_tag, fill=(148, 163, 184))
    
    # Features Pill Box
    f_pill = get_font(20, bold=True)
    pills = [
        "100 Hz Acoustic Physics",
        "4-Tier Contrastive Dataset",
        "Non-Unilateral 10.0 Rubric",
        "Chess.com Move Cards",
        "Dual-Layer LLM Reasoner"
    ]
    start_x = 200
    y_p = 580
    for p in pills:
        bbox = f_pill.getbbox(p)
        pw = bbox[2] - bbox[0] + 32
        draw.rounded_rectangle([start_x, y_p, start_x + pw, y_p + 48], radius=12, fill=(24, 32, 48), outline=(45, 60, 88), width=1)
        draw.text((start_x + 16, y_p + 12), p, font=f_pill, fill=(226, 232, 240))
        start_x += pw + 24
        if start_x > 1700:
            break
            
    # Credits
    f_cred = get_font(20, bold=False)
    draw.text(((WIDTH - 300) // 2, 920), "Team VOCODE  •  Complete Showcase", font=f_cred, fill=(100, 116, 139))
    
    img.save(os.path.join(SLIDES_DIR, "slide_1a_title.png"))

# ==============================================================================
# SLIDE 1B: THE ADJUDICATION CRISIS
# ==============================================================================
def render_slide_1b():
    img, draw = create_base_canvas()
    draw_header(draw, "The Adjudication Crisis in Public Oratory", "PROBLEM CONTEXT")
    
    # Left Card: The Competitive Speaking Reality
    draw_card(draw, [100, 130, 930, 980], fill=(16, 22, 34), outline=(37, 47, 66))
    f_card_t = get_font(28, bold=True)
    draw.text((140, 165), "Competitive Spoken Performance", font=f_card_t, fill=(248, 250, 252))
    
    f_body = get_font(20, bold=False)
    bullets = [
        "• High Stakes: Forensics, Toastmasters, TED, Declamation.",
        "• Complex Interaction: Pitch inflection, cadence, pauses, energy.",
        "• Traditional Judges rely on intuitive, subjective perception.",
        "• Severe Halo Effect: Charisma often obscures acoustic defects."
    ]
    y = 230
    for b in bullets:
        draw.text((140, y), b, font=f_body, fill=(203, 213, 225))
        y += 44
        
    # Ballot Box visual
    draw.rounded_rectangle([140, 440, 890, 930], radius=12, fill=(24, 30, 44), outline=(56, 189, 248), width=2)
    draw.text((170, 470), "REAL COMPETITOR BALLOT (TRADITIONAL ADJUDICATION):", font=get_font(18, bold=True), fill=(56, 189, 248))
    
    quotes = [
        "\"Score: 78/100\"",
        "\"Notes: Good energy overall, but work on your vocal presence.\"",
        "\"Pacing felt somewhat rushed in the middle. Be more confident.\"",
        "\"Vocal variety lacked punch. Connect better with the audience.\""
    ]
    y_q = 530
    for q in quotes:
        draw.text((170, y_q), q, font=get_font(20, bold=True), fill=(251, 191, 36) if "Score" in q else (241, 245, 249))
        y_q += 50
    draw.text((170, 840), "❌ 0 Timestamps   ❌ 0 Objective Metrics   ❌ 0 Physical Fixes", font=get_font(20, bold=True), fill=(239, 68, 68))

    # Right Card: The Solution: VOCODE's Acoustic Physics
    draw_card(draw, [990, 130, 1820, 980], fill=(16, 24, 38), outline=(56, 189, 248), width=2)
    draw.text((1030, 165), "The VOCODE Solution: Acoustic Ground Truth", font=f_card_t, fill=(56, 189, 248))
    
    sol_bullets = [
        "• 100 Hz Praat Pitch Telemetry: Quantifies exact semitone range.",
        "• Peak-to-Average Power Ratio (PAPR): Measures vocal punch in dB.",
        "• 20% Oratorical Pause Law: Tracks dead-air vs. breathless run-ons.",
        "• Millisecond Grounding: Bounding flaw intervals [t_start, t_end].",
        "• Dual-Layer LLM Reasoner: Deterministic DSP + Psychological impact."
    ]
    y = 230
    for b in sol_bullets:
        draw.text((1030, y), b, font=f_body, fill=(203, 213, 225))
        y += 44
        
    draw.rounded_rectangle([1030, 480, 1780, 930], radius=12, fill=(15, 31, 48), outline=(16, 185, 129), width=2)
    draw.text((1060, 510), "VOCODE OBJECTIVE FORENSIC REPORT (SAMPLE):", font=get_font(18, bold=True), fill=(16, 185, 129))
    vocode_stats = [
        "✓ Overall Score: 4.70 / 10.0 (Tier: Hesitant / Monotone Flaws)",
        "✓ Pitch Dynamic Range: 6.8 semitones (Deficit: Flatline < 10.56 st)",
        "✓ Max Silence Duration: 4.80s at [00:18.20 -> 00:23.00] (Blunder)",
        "✓ Gate Ceiling: Capped at 5.0 by Paralyzing Silence Coupling",
        "✓ Prescribed Physical Fix: 1-Second Silent Eye-Contact Reset Drill"
    ]
    y_v = 570
    for s in vocode_stats:
        draw.text((1060, y_v), s, font=get_font(20, bold=True), fill=(241, 245, 249))
        y_v += 48
    draw.text((1060, 850), "✓ Millisecond Precision  ✓ Mathematically Proven  ✓ Actionable Drills", font=get_font(20, bold=True), fill=(16, 185, 129))

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_1b_crisis.png"))

# ==============================================================================
# SLIDE 2A: THE THREE FATAL FLAWS
# ==============================================================================
def render_slide_2a():
    img, draw = create_base_canvas()
    draw_header(draw, "The Three Fatal Flaws of Traditional Speech Adjudication", "CORE PROBLEM STATEMENT")
    
    cards = [
        {
            "num": "01",
            "title": "Unilateral Penalization Bias",
            "subtitle": "Transient Metric Isolation",
            "points": [
                "• Rule-based tools evaluate metrics in isolation.",
                "• Example: An intentional 2.5s pregnant pause before a climax is flagged as 'dead-air'.",
                "• Example: An intimate low-volume inflection is penalized as 'mumbling'.",
                "• Lacks holistic oratorical synergy awareness."
            ],
            "solution": "VOCODE: Systemic Impairment Coupling (Ψ_impair) with Dynamic Gate Ceiling.",
            "color": (239, 68, 68)
        },
        {
            "num": "02",
            "title": "The Subjective Feedback Gap",
            "subtitle": "Post-Hoc Impressionism",
            "points": [
                "• Judges provide vague qualitative adjectives ('felt flat', 'lackluster').",
                "• Participants receive no temporal coordinates where points were lost.",
                "• No actionable guidance on the physical vocal mechanics required to improve.",
                "• Different judges produce wildly diverging scores."
            ],
            "solution": "VOCODE: Millisecond Temporal Grounding with Chess.com Move Cards & Physical Drills.",
            "color": (245, 158, 11)
        },
        {
            "num": "03",
            "title": "The ASR Corpus Void",
            "subtitle": "Word Error Rate vs Prosody",
            "points": [
                "• Speech corpora (LibriSpeech, CommonVoice) focus solely on Speech-to-Text.",
                "• Measure 'what' was spoken (WER), not 'how' it was delivered.",
                "• Zero paired datasets existed mapping masterclass rhetoric against flawed delivery of the exact same text."
            ],
            "solution": "VOCODE: Engineered 4-Tier Paired Contrastive Dataset across 48 Iconic Speeches.",
            "color": (56, 189, 248)
        }
    ]
    
    start_x = 80
    w_card = 540
    for c in cards:
        draw_card(draw, [start_x, 130, start_x + w_card, 980], fill=(16, 22, 34), outline=(37, 47, 66))
        
        # Number badge
        draw.rounded_rectangle([start_x + 30, 160, start_x + 100, 210], radius=8, fill=(30, 41, 59), outline=c["color"], width=2)
        draw.text((start_x + 44, 168), c["num"], font=get_font(24, bold=True), fill=c["color"])
        
        draw.text((start_x + 120, 162), c["title"], font=get_font(22, bold=True), fill=(248, 250, 252))
        draw.text((start_x + 120, 192), c["subtitle"], font=get_font(16, bold=False), fill=(148, 163, 184))
        
        draw.line([start_x + 30, 230, start_x + w_card - 30, 230], fill=(30, 41, 59), width=1)
        
        y = 260
        for p in c["points"]:
            # Wrap text if needed
            words = p.split()
            line = ""
            for w in words:
                test_line = line + " " + w if line else w
                bbox = get_font(18, bold=False).getbbox(test_line)
                if bbox[2] - bbox[0] > w_card - 60:
                    draw.text((start_x + 30, y), line, font=get_font(18, bold=False), fill=(203, 213, 225))
                    y += 28
                    line = "  " + w
                else:
                    line = test_line
            if line:
                draw.text((start_x + 30, y), line, font=get_font(18, bold=False), fill=(203, 213, 225))
                y += 34
                
        # Bottom Solution Box
        draw.rounded_rectangle([start_x + 20, 780, start_x + w_card - 20, 950], radius=10, fill=(15, 29, 46), outline=(16, 185, 129), width=1)
        draw.text((start_x + 35, 796), "VOCODE RESOLUTION:", font=get_font(16, bold=True), fill=(16, 185, 129))
        
        # Wrap solution
        words = c["solution"].split()
        line = ""
        y_s = 830
        for w in words:
            test_line = line + " " + w if line else w
            bbox = get_font(17, bold=False).getbbox(test_line)
            if bbox[2] - bbox[0] > w_card - 70:
                draw.text((start_x + 35, y_s), line, font=get_font(17, bold=False), fill=(241, 245, 249))
                y_s += 26
                line = w
            else:
                line = test_line
        if line:
            draw.text((start_x + 35, y_s), line, font=get_font(17, bold=False), fill=(241, 245, 249))
            
        start_x += w_card + 40
        
    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_2a_flaws.png"))

# ==============================================================================
# SLIDE 3A: DATASET & 4-TIER GRADIENT
# ==============================================================================
def render_slide_3a():
    img, draw = create_base_canvas()
    draw_header(draw, "Custom Paired Contrastive Dataset Architecture", "DATA ENGINEERING & STRESS TESTING (30%)")
    
    # Left: Masterclass Baseline Sourcing (48 speeches)
    draw_card(draw, [80, 130, 850, 980], fill=(16, 22, 34))
    draw.text((120, 165), "Masterclass Baseline (48 Iconic Speeches)", font=get_font(26, bold=True), fill=(56, 189, 248))
    draw.text((120, 205), "Pristine historical orations serving as oratorical ground truth.", font=get_font(18, bold=False), fill=(148, 163, 184))
    
    speeches = [
        ("Dr. Martin Luther King Jr.", "I Have a Dream (1963) — Prophetic Cadence"),
        ("John F. Kennedy", "Inaugural Address (1961) — Dynamic Contrast"),
        ("Sir Winston Churchill", "We Shall Fight on the Beaches — Resonant Delivery"),
        ("Steve Jobs", "Stanford Commencement (2005) — Conversational Agility"),
        ("Admiral William H. McRaven", "Make Your Bed (2014) — Rhythmic Projection"),
        ("Charlie Chaplin", "The Great Dictator (1940) — Crescendo Mastery")
    ]
    y = 260
    for name, desc in speeches:
        draw.rounded_rectangle([120, y, 810, y + 64], radius=8, fill=(24, 32, 48), outline=(37, 47, 66), width=1)
        draw.text((140, y + 10), name, font=get_font(19, bold=True), fill=(248, 250, 252))
        draw.text((140, y + 36), desc, font=get_font(15, bold=False), fill=(56, 189, 248))
        y += 76
        
    draw.rounded_rectangle([120, 750, 810, 940], radius=10, fill=(15, 29, 46), outline=(56, 189, 248), width=1)
    draw.text((140, 770), "THE SCIENTIFIC CONTROL VARIABLE:", font=get_font(18, bold=True), fill=(56, 189, 248))
    draw.text((140, 805), "By using identical verbatim transcripts across tiers,", font=get_font(18, bold=False), fill=(203, 213, 225))
    draw.text((140, 835), "textual quality is 100% controlled. The ONLY variance", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.text((140, 865), "is physical acoustic delivery dynamics.", font=get_font(18, bold=True), fill=(16, 185, 129))
    draw.text((140, 900), "Repository Location: good speeches/ (48 Clean Audio Files)", font=get_font(15, bold=False), fill=(148, 163, 184))

    # Right: The 4-Tier Bad Mirror Gradient
    draw_card(draw, [890, 130, 1840, 980], fill=(16, 22, 34))
    draw.text((930, 165), "The 4-Tier Contrastive Degradation Spectrum", font=get_font(26, bold=True), fill=(248, 250, 252))
    draw.text((930, 205), "Controlled algorithmic flaw injections grounded with millisecond labels.", font=get_font(18, bold=False), fill=(148, 163, 184))
    
    tiers = [
        ("Tier 0: Masterclass (Score: 9.0 - 10.0)", "Original iconic oration. Pitch dynamic range > 14 semitones, 20% pause law adhered, crisp PAPR punch > 22 dB.", (16, 185, 129)),
        ("Tier 1: Distinguished (Score: 7.5 - 8.9)", "Mild hesitation, restrained dynamic range (10-12 semitones), minor breath clipping.", (56, 189, 248)),
        ("Tier 2: Proficient (Score: 6.0 - 7.4)", "Noticeable cadence dragging (< 110 WPM) or mild monotone flattening (8-10 semitones).", (245, 158, 11)),
        ("Tier 3: Botched (Score: 2.0 - 5.5)", "Catastrophic anxiety: 4.8s dead-air freeze, robotic PSOLA monotone flatline (< 5 semitones), rushed 220+ WPM runaway.", (239, 68, 68))
    ]
    y_t = 260
    for t_name, t_desc, col in tiers:
        draw.rounded_rectangle([930, y_t, 1800, y_t + 110], radius=10, fill=(24, 30, 44), outline=col, width=2)
        draw.text((955, y_t + 14), t_name, font=get_font(20, bold=True), fill=col)
        # wrap text
        words = t_desc.split()
        line = ""
        y_d = y_t + 46
        for w in words:
            test_line = line + " " + w if line else w
            if get_font(16, bold=False).getbbox(test_line)[2] > 800:
                draw.text((955, y_d), line, font=get_font(16, bold=False), fill=(203, 213, 225))
                y_d += 24
                line = w
            else:
                line = test_line
        if line:
            draw.text((955, y_d), line, font=get_font(16, bold=False), fill=(203, 213, 225))
        y_t += 128
        
    # Flaw Manifest Box
    draw.rounded_rectangle([930, 800, 1800, 940], radius=8, fill=(18, 28, 42), outline=(37, 47, 66), width=1)
    draw.text((955, 818), "MANIFEST GROUND TRUTH: dataset/approach3_experiment/tier3_flaws.json", font=get_font(16, bold=True), fill=(56, 189, 248))
    draw.text((955, 850), "{\"flaw\": \"paralyzing_freeze\", \"start\": 18.20, \"end\": 23.00, \"duration\": 4.80, \"penalty\": 2.80}", font=get_font(17, bold=True), fill=(251, 191, 36))
    draw.text((955, 888), "{\"flaw\": \"psola_monotone\", \"start\": 0.00, \"end\": 18.20, \"semitone_compression\": 0.35}", font=get_font(17, bold=True), fill=(239, 68, 68))

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_3a_dataset.png"))

# ==============================================================================
# SLIDE 4A: SYSTEM PIPELINE
# ==============================================================================
def render_slide_4a():
    img, draw = create_base_canvas()
    draw_header(draw, "End-to-End Multimodal System Pipeline Architecture", "ENGINEERING PIPELINE")
    
    stages = [
        ("Stage 1", "Ephemeral Ingestion", [
            "• yt-dlp & file upload",
            "• 4-Layer Gatekeeper",
            "• Monologue verification",
            "• 0 MB residual storage"
        ], (56, 189, 248)),
        ("Stage 2", "7-Stage Standardization", [
            "• Universal 32-bit decode",
            "• 16 kHz sinc resample",
            "• 70 Hz Butterworth HPF",
            "• -20 LUFS EBU R128 Norm"
        ], (96, 165, 250)),
        ("Stage 3", "100 Hz Telemetry", [
            "• Whisper forced align",
            "• Praat Parselmouth F0",
            "• PAPR Crest Factor (dB)",
            "• 20% Pause Law tracker"
        ], (129, 140, 248)),
        ("Stage 4", "Non-Unilateral Rubric", [
            "• 5 Oratorical Pillars (10pt)",
            "• Systemic Impairment (Ψ)",
            "• Dynamic Gating Ceiling",
            "• Leniency Continuum (λ)"
        ], (168, 85, 247)),
        ("Stage 5", "Move Classifier", [
            "• Chess.com Move Cards",
            "• Brilliant, Great, Good",
            "• Inaccuracy, Mistake",
            "• Blunder Grounding"
        ], (236, 72, 153)),
        ("Stage 6", "Dual LLM Reasoner", [
            "• Groq Qwen 27B / Llama 3",
            "• Deterministic DSP proof",
            "• Audience psychological impact",
            "• 4 Daily Practice Drills"
        ], (16, 185, 129))
    ]
    
    x_start = 60
    w_box = 280
    for idx, (st_name, st_title, st_pts, st_col) in enumerate(stages):
        # Draw Box
        draw_card(draw, [x_start, 150, x_start + w_box, 860], fill=(16, 22, 34), outline=st_col, width=2)
        
        # Stage pill
        draw.rounded_rectangle([x_start + 20, 175, x_start + w_box - 20, 215], radius=6, fill=(24, 32, 48), outline=st_col, width=1)
        draw.text((x_start + 35, 185), st_name.upper(), font=get_font(16, bold=True), fill=st_col)
        
        draw.text((x_start + 20, 240), st_title, font=get_font(20, bold=True), fill=(248, 250, 252))
        draw.line([x_start + 20, 280, x_start + w_box - 20, 280], fill=(30, 41, 59), width=1)
        
        y_p = 310
        for p in st_pts:
            draw.text((x_start + 20, y_p), p, font=get_font(16, bold=False), fill=(203, 213, 225))
            y_p += 44
            
        # Arrow to next stage
        if idx < len(stages) - 1:
            arr_x = x_start + w_box + 5
            draw.polygon([(arr_x, 480), (arr_x + 15, 490), (arr_x, 500)], fill=(56, 189, 248))
            
        x_start += w_box + 26
        
    # Bottom Summary Bar
    draw.rounded_rectangle([60, 890, 1860, 960], radius=10, fill=(15, 29, 46), outline=(56, 189, 248), width=1)
    draw.text((90, 915), "PIPELINE GUARANTEE: Speaker-Agnostic Pitch Normalization • Zero-Residual Audio Storage Bloat • 100% Deterministic Reproducibility", font=get_font(18, bold=True), fill=(241, 245, 249))

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_4a_pipeline.png"))

# ==============================================================================
# SLIDE 6A: SCORING ARCHITECTURE & MATHEMATICS
# ==============================================================================
def render_slide_6a():
    img, draw = create_base_canvas()
    draw_header(draw, "The 10.0-Point Non-Unilateral Scoring Architecture", "MATHEMATICAL FORMULATION")
    
    # Left: The 5 Oratorical Pillars
    draw_card(draw, [80, 130, 930, 980], fill=(16, 22, 34))
    draw.text((120, 165), "The 5 Oratorical Pillars (10.0 Pts Total)", font=get_font(26, bold=True), fill=(56, 189, 248))
    
    pillars = [
        ("1. Pitch Modulation & Expressiveness", "2.5 pts", "ΔF0 semitones, pitch velocity (v_F0). Penalizes flatlines (<10.56 st).", (56, 189, 248)),
        ("2. Cadence, Pacing & Speech Rate", "2.5 pts", "WPM (130-170 ideal). Penalizes runaway rushing (>220) & dragging (<110).", (96, 165, 250)),
        ("3. Rhetorical Pausing & Fluency", "2.0 pts", "The 20% Pause Law, dead-air freeze penalty (>3.0s), lexical stutter loops.", (129, 140, 248)),
        ("4. Dynamic Energy & Vocal Projection", "1.5 pts", "Peak-to-Average Power Ratio (PAPR crest factor in dB). Punch vs whisper.", (168, 85, 247)),
        ("5. Spectral Clarity & Articulation", "1.5 pts", "Harmonic-to-Noise Ratio (HNR > 15 dB), high-frequency enunciation clarity.", (236, 72, 153))
    ]
    y_pil = 230
    for p_title, p_wt, p_sub, p_col in pillars:
        draw.rounded_rectangle([120, y_pil, 890, y_pil + 110], radius=8, fill=(24, 32, 48), outline=p_col, width=1)
        draw.text((140, y_pil + 12), p_title, font=get_font(20, bold=True), fill=(248, 250, 252))
        
        # Weight badge
        draw.rounded_rectangle([800, y_pil + 10, 875, y_pil + 46], radius=6, fill=p_col)
        draw.text((810, y_pil + 16), p_wt, font=get_font(16, bold=True), fill=(10, 14, 23))
        
        draw.text((140, y_pil + 54), p_sub, font=get_font(16, bold=False), fill=(203, 213, 225))
        y_pil += 128

    # Right: Non-Unilateral Gate Ceiling & Chess.com Moves
    draw_card(draw, [970, 130, 1840, 980], fill=(16, 22, 34))
    draw.text((1010, 165), "Systemic Impairment Coupling & Move Cards", font=get_font(26, bold=True), fill=(248, 250, 252))
    
    # Formula Card
    draw.rounded_rectangle([1010, 220, 1800, 380], radius=10, fill=(15, 29, 46), outline=(56, 189, 248), width=2)
    draw.text((1040, 240), "DYNAMIC GATE CEILING EQUATION:", font=get_font(18, bold=True), fill=(56, 189, 248))
    draw.text((1040, 280), "Gate Ceiling = 10.0 - 0.55 · (N_deficits - 1) - Ψ_impair", font=get_font(24, bold=True), fill=(251, 191, 36))
    draw.text((1040, 330), "Prevents unilateral penalties: quiet speech with high pitch agility is", font=get_font(17, bold=False), fill=(203, 213, 225))
    draw.text((1040, 355), "recognized as intimate rhetoric rather than penalized for low volume.", font=get_font(17, bold=True), fill=(16, 185, 129))

    # Chess.com Move Hierarchy
    draw.text((1010, 410), "Chess.com-Style Move Classification Hierarchy:", font=get_font(22, bold=True), fill=(248, 250, 252))
    moves = [
        ("✨ Brilliant Move", "Dramatic pitch excursion (ΔF0 > 14 st) synchronized with PAPR punch & climactic pause.", (56, 189, 248)),
        ("🎯 Great Move", "Fluid cadence (130-175 WPM) with resonant pitch inflection and natural breath phrasing.", (16, 185, 129)),
        ("👍 Good Move", "Standard, clear delivery meeting baseline oratorical expectations.", (148, 163, 184)),
        ("⚠️ Inaccuracy", "Mild hesitation (<2.0s), slight breath clipping, or restrained pitch dynamics.", (251, 191, 36)),
        ("⚡ Mistake", "Rushed cadence (>220 WPM), clipped pauses (<14%), or repetitive lexical fillers.", (249, 115, 22)),
        ("❌ Blunder", "Critical breakdown: dead-air freeze (>3.0s), robotic flatline (<5 st), or panic stammers.", (239, 68, 68))
    ]
    y_m = 450
    for m_name, m_desc, m_col in moves:
        draw.rounded_rectangle([1010, y_m, 1800, y_m + 68], radius=8, fill=(24, 30, 44), outline=m_col, width=1)
        draw.text((1030, y_m + 10), m_name, font=get_font(18, bold=True), fill=m_col)
        draw.text((1030, y_m + 38), m_desc, font=get_font(15, bold=False), fill=(203, 213, 225))
        y_m += 80

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_6a_architecture.png"))

# ==============================================================================
# SLIDE 7A: OFFICIAL RUBRIC ALIGNMENT & VALIDATION
# ==============================================================================
def render_slide_7a():
    img, draw = create_base_canvas()
    draw_header(draw, "Official Hackathon Track C Evaluation Rubric Compliance", "EVALUATION CRITERIA & EVIDENCE")
    
    # Official Table
    criteria = [
        ("Causal Explainability & Temporal Grounding", "25%", "Millisecond timestamps [ts, te] on flaw regions; dual deterministic DSP proofs + Groq Qwen/Llama semantic audience critiques.", "app/services/move_classifier.py\napp/services/explanation_service.py", (56, 189, 248)),
        ("Data Engineering & Stress Testing", "30%", "48 curated masterclass speeches; 4-tier synthetic degradation spectrum; 200-clip empirical benchmark corpus across 5 quality tiers.", "good speeches/\nsrc/injector/flaw_injector.py\nfindings/dataset_200_evaluation_results.json", (16, 185, 129)),
        ("Feature Extraction", "20%", "100 Hz Praat F0 dynamics, pitch velocity, PAPR crest factor, 20% Pause Law tracker, -20 LUFS EBU R128 standardization.", "src/preprocessing/telemetry.py\nsrc/preprocessing/audio_standardizer.py", (168, 85, 247)),
        ("Visualization & Dashboard", "15%", "Interactive Streamlit app with rotating 60 fps tape reels, Plotly gauge dial, full-width Chess.com waveform, millisecond HTML5 audio player.", "app/app.py\napp/components/move_waveform.py\napp/components/coach_tab.py", (251, 191, 36)),
        ("Reproducibility & Code Quality", "10%", "Fully containerized Dockerfile, pinned requirements.txt, 11/11 unit tests passing, zero-residual audio lifecycle, clean CLI scripts.", "Dockerfile\nrequirements.txt\ntests/test_preprocessing.py", (236, 72, 153))
    ]
    
    y_row = 140
    for crit, wt, desc, loc, col in criteria:
        draw_card(draw, [80, y_row, 1840, y_row + 115], fill=(16, 22, 34), outline=col, width=1)
        
        # Weight badge
        draw.rounded_rectangle([110, y_row + 18, 210, y_row + 68], radius=8, fill=col)
        draw.text((130, y_row + 28), wt, font=get_font(26, bold=True), fill=(10, 14, 23))
        draw.text((115, y_row + 76), "WEIGHT", font=get_font(14, bold=True), fill=col)
        
        # Criterion Title
        draw.text((240, y_row + 16), crit, font=get_font(22, bold=True), fill=(248, 250, 252))
        
        # Description
        words = desc.split()
        line = ""
        y_d = y_row + 52
        for w in words:
            test_line = line + " " + w if line else w
            if get_font(16, bold=False).getbbox(test_line)[2] > 980:
                draw.text((240, y_d), line, font=get_font(16, bold=False), fill=(203, 213, 225))
                y_d += 24
                line = w
            else:
                line = test_line
        if line:
            draw.text((240, y_d), line, font=get_font(16, bold=False), fill=(203, 213, 225))
            
        # Repo Location box
        draw.rounded_rectangle([1340, y_row + 14, 1810, y_row + 101], radius=6, fill=(24, 32, 48), outline=(37, 47, 66), width=1)
        draw.text((1355, y_row + 22), "VERIFIED REPO LOCATION:", font=get_font(13, bold=True), fill=(56, 189, 248))
        lines = loc.split("\n")
        y_loc = y_row + 44
        for l in lines:
            draw.text((1355, y_loc), l, font=get_font(14, bold=False), fill=(148, 163, 184))
            y_loc += 20
            
        y_row += 135
        
    # Statistical Benchmark Banner
    draw.rounded_rectangle([80, 830, 1840, 960], radius=10, fill=(15, 31, 48), outline=(16, 185, 129), width=2)
    draw.text((110, 850), "EMPIRICAL BENCHMARK VALIDATION (200 CLIPS ACROSS 5 TIERS):", font=get_font(18, bold=True), fill=(16, 185, 129))
    draw.text((110, 888), "• Pearson Correlation: r = 0.461 (p < 0.001)    • Spearman Rank Correlation: ρ = 0.589 (p < 0.001)", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.text((110, 920), "• Mean Absolute Error: 1.17 / 10.0 pts          • Exact Tier Classification Agreement: 71.0%", font=get_font(18, bold=True), fill=(56, 189, 248))

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_7a_rubrics.png"))

# ==============================================================================
# SLIDE 8A: CONCLUSION & REPRODUCIBILITY
# ==============================================================================
def render_slide_8a():
    img, draw = create_base_canvas()
    draw_header(draw, "Conclusion, Deployment & Reproducibility", "SUMMARY & DELIVERABLES")
    
    # Left: Deployment & Docker
    draw_card(draw, [80, 130, 930, 980], fill=(16, 22, 34))
    draw.text((120, 165), "Reproducible Deployment Architecture", font=get_font(26, bold=True), fill=(56, 189, 248))
    
    draw.text((120, 220), "One-Command Local Docker Execution:", font=get_font(18, bold=True), fill=(241, 245, 249))
    draw.rounded_rectangle([120, 255, 890, 360], radius=8, fill=(10, 14, 23), outline=(56, 189, 248), width=1)
    draw.text((140, 275), "$ docker build -t vocode:latest .", font=get_font(20, bold=True), fill=(16, 185, 129))
    draw.text((140, 315), "$ docker run -p 8501:8501 vocode:latest", font=get_font(20, bold=True), fill=(56, 189, 248))
    
    bullets = [
        "• Containerized on python:3.12-slim with ffmpeg & libsndfile1.",
        "• Headless Streamlit flags pre-configured (--server.headless=true).",
        "• 11/11 Preprocessing and Telemetry Unit Tests Passing.",
        "• Ephemeral audio processing guarantees 0 MB persistent storage bloat.",
        "• Fallback offline DSP grading operational even without external API."
    ]
    y_b = 400
    for b in bullets:
        draw.text((120, y_b), b, font=get_font(18, bold=False), fill=(203, 213, 225))
        y_b += 44
        
    draw.rounded_rectangle([120, 680, 890, 930], radius=10, fill=(15, 29, 46), outline=(37, 47, 66), width=1)
    draw.text((140, 705), "SOURCE CODE REPOSITORY & DOCUMENTATION:", font=get_font(18, bold=True), fill=(56, 189, 248))
    draw.text((140, 745), "GitHub: https://github.com/lazarus/HackathonMM2", font=get_font(20, bold=True), fill=(241, 245, 249))
    draw.text((140, 785), "Problem Statement Reference: ps.pdf", font=get_font(17, bold=False), fill=(203, 213, 225))
    draw.text((140, 815), "Comprehensive Technical Report: final_report.pdf", font=get_font(17, bold=False), fill=(203, 213, 225))
    draw.text((140, 845), "Live Prototype: http://localhost:8501", font=get_font(17, bold=False), fill=(16, 185, 129))

    # Right: Project Summary & Vision
    draw_card(draw, [970, 130, 1840, 980], fill=(16, 22, 34))
    draw.text((1010, 165), "Transforming Oratorical Evaluation", font=get_font(26, bold=True), fill=(248, 250, 252))
    
    achievements = [
        ("Physics-Grounded Objective Truth", "Replaces subjective adjudication with 100 Hz micro-prosodic physical metrics, eliminating judge bias and halo effects."),
        ("First Paired Contrastive Oratorical Dataset", "Holds text constant across a 4-tier spectrum (Masterclass to Botched) across 48 speeches, establishing a definitive ML benchmark."),
        ("Non-Unilateral Evaluation Fairness", "Models holistic synergy via Systemic Impairment (Ψ_impair) and dynamic leniency continuum (λ ∈ [0, 100])."),
        ("Actionable Pedagogical Coaching", "Chess.com move categorization paired with dual-layer LLM explanations and targeted daily physical drills.")
    ]
    y_a = 230
    for a_title, a_desc in achievements:
        draw.rounded_rectangle([1010, y_a, 1800, y_a + 120], radius=8, fill=(24, 30, 44), outline=(56, 189, 248), width=1)
        draw.text((1035, y_a + 14), a_title, font=get_font(20, bold=True), fill=(56, 189, 248))
        # wrap
        words = a_desc.split()
        line = ""
        y_ad = y_a + 48
        for w in words:
            test_line = line + " " + w if line else w
            if get_font(16, bold=False).getbbox(test_line)[2] > 730:
                draw.text((1035, y_ad), line, font=get_font(16, bold=False), fill=(203, 213, 225))
                y_ad += 24
                line = w
            else:
                line = test_line
        if line:
            draw.text((1035, y_ad), line, font=get_font(16, bold=False), fill=(203, 213, 225))
        y_a += 140
        
    draw.rounded_rectangle([1010, 810, 1800, 930], radius=8, fill=(15, 31, 48), outline=(16, 185, 129), width=2)
    draw.text((1035, 835), "THANK YOU FOR WATCHING", font=get_font(22, bold=True), fill=(16, 185, 129))
    draw.text((1035, 875), "VOCODE — Multimodal AI Hackathon 2026 • Track C", font=get_font(18, bold=False), fill=(241, 245, 249))

    draw_footer(draw)
    img.save(os.path.join(SLIDES_DIR, "slide_8a_conclusion.png"))

if __name__ == "__main__":
    print("Generating broadcast slides...")
    render_slide_1a()
    render_slide_1b()
    render_slide_2a()
    render_slide_3a()
    render_slide_4a()
    render_slide_6a()
    render_slide_7a()
    render_slide_8a()
    print("Base slides generated successfully!")
