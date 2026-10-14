"""
Move Classifier Service: "Chess.com"-Style Rhetorical Move Analyzer
Classifies continuous temporal regions of speech into oratorical moves:
- Brilliant (Cyan): Masterclass rhetorical emphasis, punchy PAPR, dramatic pause.
- Good / Great (Green): Fluid cadence, natural pitch dynamics, balanced pauses.
- Inaccuracy (Yellow): Mild hesitation, minor pitch flattening.
- Mistake (Orange): Rushed runaway pacing, clipped pauses, vocal strain.
- Blunder (Red): Paralyzing dead-air freeze, monotone flatline, stammer loops.
"""

import re
import numpy as np
import librosa
import soundfile as sf
import parselmouth

MOVE_CONFIG = {
    "BRILLIANT": {
        "label": "Brilliant Move",
        "icon": "✨",
        "color": "#00E5FF",      # Electric Cyan
        "bg_color": "rgba(0, 229, 255, 0.25)",
        "description": "Masterclass rhetorical delivery: Dynamic pitch peak combined with emphatic vocal punchiness."
    },
    "GREAT": {
        "label": "Great Move",
        "icon": "🎯",
        "color": "#00E676",      # Emerald Green
        "bg_color": "rgba(0, 230, 118, 0.20)",
        "description": "Fluid cadence, resonant pitch inflection, and well-balanced rhetorical phrasing."
    },
    "GOOD": {
        "label": "Good Move",
        "icon": "👍",
        "color": "#76FF03",      # Lime Green
        "bg_color": "rgba(118, 255, 3, 0.15)",
        "description": "Standard, clear delivery meeting baseline oratorical expectations."
    },
    "INACCURACY": {
        "label": "Inaccuracy",
        "icon": "⚠️",
        "color": "#FFEA00",      # Yellow
        "bg_color": "rgba(255, 234, 0, 0.25)",
        "description": "Mild hesitation or slightly restrained pitch modulation; slightly stalled momentum."
    },
    "MISTAKE": {
        "label": "Mistake",
        "icon": "⚡",
        "color": "#FF9100",      # Amber / Orange
        "bg_color": "rgba(255, 145, 0, 0.25)",
        "description": "Rushed pacing runaway, clipped inter-phrase breath, or harsh vocal strain."
    },
    "BLUNDER": {
        "label": "Blunder",
        "icon": "❌",
        "color": "#FF1744",      # Crimson Red
        "bg_color": "rgba(255, 23, 68, 0.35)",
        "description": "Critical rhetorical failure: Paralyzing dead-air freeze, robotic monotone flatline, or stammer loop."
    }
}

def classify_speech_moves(
    clean_wav_path: str,
    speech_events: list[dict],
    deductions: list[dict] | None = None
) -> list[dict]:
    """
    Analyzes temporal segments and assigns a Chess.com-style classification
    to each phrase and inter-phrase pause.
    """
    y, sr = sf.read(clean_wav_path, dtype='float32')
    if y.ndim > 1:
        y = np.mean(y, axis=1 if y.shape[1] < y.shape[0] else 0)
    duration = float(len(y) / sr)

    # 1. Pitch tracking using Parselmouth Praat
    snd = parselmouth.Sound(clean_wav_path)
    pitch = snd.to_pitch(time_step=0.02, pitch_floor=75.0, pitch_ceiling=500.0)
    pitch_values = pitch.selected_array['frequency']
    pitch_times = pitch.xs()

    # 2. Short-time RMS energy
    hop_len = int(0.02 * sr)
    frame_len = hop_len * 2
    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_len)

    moves = []

    # Map deductions to intervals if available
    grounded_penalties = []
    if deductions:
        for d in deductions:
            if "temporal_interval" in d:
                grounded_penalties.append(d)

    # If no speech events provided, synthesize 5-second uniform chunks
    if not speech_events:
        step = 5.0
        speech_events = [
            {"start": t, "end": min(duration, t + step), "text": f"Segment {i+1}"}
            for i, t in enumerate(np.arange(0, duration, step))
        ]

    for idx, ev in enumerate(speech_events):
        t_start = ev.get("start", 0.0)
        t_end = ev.get("end", duration)
        text = ev.get("text", "").strip()
        dur = max(0.1, t_end - t_start)

        # Slice pitch in interval
        p_mask = (pitch_times >= t_start) & (pitch_times <= t_end)
        seg_f0 = pitch_values[p_mask]
        voiced = seg_f0[seg_f0 > 0]

        # Slice energy
        e_mask = (rms_times >= t_start) & (rms_times <= t_end)
        seg_rms = rms[e_mask]

        # Compute interval metrics
        f0_st_range = 0.0
        if len(voiced) > 5:
            p05, p95 = np.percentile(voiced, 5), np.percentile(voiced, 95)
            f0_st_range = float(12.0 * np.log2((p95 + 1e-6) / (p05 + 1e-6)))

        mean_pwr = float(np.mean(seg_rms**2) + 1e-10) if len(seg_rms) > 0 else 1e-5
        max_pwr = float(np.max(seg_rms**2) + 1e-10) if len(seg_rms) > 0 else 1e-5
        papr = float(max_pwr / mean_pwr)

        words = len(text.split()) if text else max(1, int(dur * 2.5))
        wpm = (words / dur) * 60.0

        # Check for explicit flaw collision
        matched_flaw = None
        for g in grounded_penalties:
            g_s, g_e = g["temporal_interval"]
            # Overlap check
            if max(t_start, g_s) < min(t_end, g_e):
                matched_flaw = g
                break

        # Check for immediate lexical repetitions in phrase text
        rep_matches = re.findall(r"\b([a-zA-Z]+)(?:\s+\1)+\b", text, flags=re.IGNORECASE) if text else []

        # Decision Logic
        if matched_flaw:
            flaw_name = matched_flaw.get("flaw", "")
            if any(k in flaw_name.lower() for k in ["freeze", "dead-air", "flatline", "stammer"]):
                move_type = "BLUNDER"
                reason = matched_flaw.get("explanation", "Critical speech collapse detected.")
            else:
                move_type = "MISTAKE"
                reason = matched_flaw.get("explanation", "Noticeable oratorical mistake.")
        elif rep_matches:
            rep_w = rep_matches[0]
            if len(rep_matches) >= 2 or dur >= 4.0:
                move_type = "BLUNDER"
                reason = f"Severe Lexical Stutter Loop: Repetition of '{rep_w}' disrupts narrative continuity and audience focus."
            else:
                move_type = "MISTAKE"
                reason = f"Lexical Word Repetition: Unintended consecutive repetition of '{rep_w}' signals cognitive hesitation."
        elif dur >= 3.0 and words == 0:
            move_type = "BLUNDER"
            reason = f"Paralyzing silence freeze ({dur:.1f}s) broken narrative pacing."
        elif f0_st_range < 5.0 and dur >= 4.0:
            move_type = "BLUNDER"
            reason = f"Monotone flatline: Pitch modulation collapsed to {f0_st_range:.1f} semitones."
        elif wpm > 220:
            move_type = "MISTAKE"
            reason = f"Rushed runaway: Speaking rate spiked to {wpm:.0f} WPM, hindering enunciation."
        elif f0_st_range < 8.0 and dur >= 3.0:
            move_type = "INACCURACY"
            reason = f"Restrained inflection: Pitch range was limited to {f0_st_range:.1f} semitones."
        elif papr > 30.0 and f0_st_range > 14.0:
            move_type = "BRILLIANT"
            reason = f"Peak rhetorical emphasis: Vocal punchiness (PAPR {papr:.1f}) with dynamic pitch range ({f0_st_range:.1f} st)."
        elif 130 <= wpm <= 175 and f0_st_range >= 11.0:
            move_type = "GREAT"
            reason = f"Optimal cadence ({wpm:.0f} WPM) with natural vocal inflections ({f0_st_range:.1f} st)."
        else:
            move_type = "GOOD"
            reason = f"Stable delivery at {wpm:.0f} WPM."

        cfg = MOVE_CONFIG[move_type]
        moves.append({
            "index": idx + 1,
            "t_start": round(t_start, 2),
            "t_end": round(t_end, 2),
            "duration": round(dur, 2),
            "text": text,
            "move_type": move_type,
            "label": cfg["label"],
            "icon": cfg["icon"],
            "color": cfg["color"],
            "bg_color": cfg["bg_color"],
            "reason": reason,
            "metrics": {
                "wpm": round(wpm, 1),
                "f0_semitones": round(f0_st_range, 1),
                "papr": round(papr, 1)
            }
        })

    return moves
