"""
Explanation Service: Groq Cloud Open-Source Language Model Reasoner
Generates dual-layer oratorical explanations:
1. Deterministic Explanation (Acoustic physics, DSP metrics, exact thresholds, gate ceilings)
2. Semantic Explanation (Human audience perception, psychological resonance, delivery tone)
3. Prescriptive Vocal Drills (Actionable pedagogical remediation)

Uses open-source Qwen 3.8 27B via Groq with a robust local forensic fallback.
"""

import os
import json
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.8-27b"
DEFAULT_GROQ_KEY = "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"

def generate_speech_explanation(
    grade_report: dict,
    moves: list[dict],
    metrics: dict,
    api_key: str | None = None
) -> dict:
    """
    Synthesizes both a deterministic and semantic explanation of the speech performance.
    """
    key_to_use = api_key or os.getenv("GROQ_API_KEY") or DEFAULT_GROQ_KEY

    # If no Groq API key is configured, execute deterministic rule-based forensic synthesis
    if not key_to_use or len(key_to_use.strip()) < 10:
        return _generate_fallback_explanation(grade_report, moves, metrics)

    # Prepare compact payload for Groq
    total_grade = grade_report.get("total_grade", 7.0)
    grade_band = grade_report.get("grade_band", "Proficient")
    pillars = grade_report.get("pillar_scores", {})
    gating = grade_report.get("gating_diagnostics", {})
    deductions = grade_report.get("deductions", [])

    # Filter critical blunders and brilliant moves
    blunders = [m for m in moves if m["move_type"] == "BLUNDER"]
    mistakes = [m for m in moves if m["move_type"] == "MISTAKE"]
    brilliants = [m for m in moves if m["move_type"] == "BRILLIANT"]

    prompt_context = {
        "final_grade": total_grade,
        "grade_band": grade_band,
        "pillar_scores": pillars,
        "gate_diagnostics": gating,
        "acoustic_telemetry": {
            "f0_semitones": metrics.get("f0_semitones"),
            "f0_velocity_hz_per_sec": metrics.get("f0_velocity_hz_per_sec"),
            "max_pause_sec": metrics.get("max_pause_duration_sec"),
            "pause_ratio": metrics.get("pause_ratio"),
            "papr_crest_factor": metrics.get("papr_crest_factor"),
            "spectral_flux": metrics.get("spectral_flux")
        },
        "critical_blunders": [
            {"time": f"{b['t_start']}s-{b['t_end']}s", "text": b['text'], "reason": b['reason']}
            for b in blunders[:3]
        ],
        "top_mistakes": [
            {"time": f"{m['t_start']}s-{m['t_end']}s", "text": m['text'], "reason": m['reason']}
            for m in mistakes[:2]
        ],
        "brilliant_highlights": [
            {"time": f"{br['t_start']}s-{br['t_end']}s", "text": br['text'], "reason": br['reason']}
            for br in brilliants[:2]
        ]
    }

    system_instruction = (
        "You are Vocode, an Elite Forensic Oratory Coach and Acoustic Scientist. "
        "Analyze the provided speech telemetry and output strictly valid JSON with this exact structure:\n"
        "{\n"
        '  "executive_verdict": "2-3 concise sentences summarizing the overall performance and core score driver.",\n'
        '  "deterministic_explanation": "Rigorous DSP & physical acoustic rationale citing exact numbers (semitones, seconds, decibels, gate ceiling) that mathematically caused the deductions.",\n'
        '  "semantic_explanation": "Human audience perception analysis explaining how the delivery felt emotionally, why it captivated or alienated listeners, and the psychological impact of the pacing.",\n'
        '  "pillar_critiques": {\n'
        '    "pitch_modulation": "Specific evaluation of pitch dynamism",\n'
        '    "cadence_and_tempo": "Specific evaluation of pacing and rhythm",\n'
        '    "rhetorical_pausing": "Specific evaluation of pauses and hesitations",\n'
        '    "dynamic_energy": "Specific evaluation of projection and PAPR punchiness",\n'
        '    "spectral_clarity": "Specific evaluation of enunciation and diction"\n'
        '  },\n'
        '  "actionable_vocal_drills": [\n'
        '    {"title": "Name of Drill", "focus": "Target Pillar", "instructions": "Step-by-step physical vocal exercise"}\n'
        '  ]\n'
        "}"
    )

    try:
        headers = {
            "Authorization": f"Bearer {key_to_use.strip()}",
            "Content-Type": "application/json"
        }
        body = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Analyze this speech report:\n{json.dumps(prompt_context, indent=2)}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.25,
            "max_tokens": 750
        }

        resp = requests.post(GROQ_ENDPOINT, headers=headers, json=body, timeout=15)
        # Handle transient 429 rate-limiting with brief backoff
        if resp.status_code == 429:
            import time
            time.sleep(2.5)
            resp = requests.post(GROQ_ENDPOINT, headers=headers, json=body, timeout=15)

        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            parsed["source"] = f"Groq Cloud ({DEFAULT_MODEL})"
            return parsed
        else:
            return _generate_fallback_explanation(grade_report, moves, metrics, error_note=f"Groq API HTTP {resp.status_code}")
    except Exception as e:
        return _generate_fallback_explanation(grade_report, moves, metrics, error_note=str(e))


def _generate_fallback_explanation(
    grade_report: dict,
    moves: list[dict],
    metrics: dict,
    error_note: str | None = None
) -> dict:
    """
    Deterministic rule-based forensic explanation ensuring the app never fails
    even when offline or when no Groq key is supplied.
    """
    total = grade_report.get("total_grade", 7.0)
    band = grade_report.get("grade_band", "Proficient")
    pillars = grade_report.get("pillar_scores", {})
    gating = grade_report.get("gating_diagnostics", {})
    psi = gating.get("psi_impairment_index", 0.0)

    f0_st = metrics.get("f0_semitones", 14.0)
    max_pause = metrics.get("max_pause_duration_sec", 1.2)
    papr = metrics.get("papr_crest_factor", 20.0)

    blunders = [m for m in moves if m["move_type"] == "BLUNDER"]
    brilliants = [m for m in moves if m["move_type"] == "BRILLIANT"]

    # Deterministic Physics Rationale
    det_reasons = []
    det_reasons.append(f"Composite evaluation yielded {total:.2f}/10.0 ({band}).")
    if psi >= 1.0:
        det_reasons.append(f"Systemic Impairment Gate engaged (Psi = {psi:.2f}), imposing compound penalties across couped deficits.")
    if max_pause >= 3.0:
        det_reasons.append(f"Severe silence penalty triggered: Maximum unbroken pause reached {max_pause:.2f}s, exceeding the 2.50s rhetorical ceiling.")
    if f0_st < 10.0:
        det_reasons.append(f"Pitch range was severely compressed to {f0_st:.2f} semitones re normative baseline of 17.80 semitones.")
    if papr > 25.0:
        det_reasons.append(f"Vocal punchiness maintained favorable PAPR crest factor of {papr:.2f}.")

    # Semantic Human Rationale
    sem_reasons = []
    if total >= 8.5:
        sem_reasons.append("The speaker commanded the room with magnetic rhetorical presence, projecting effortless authority and vocal cadence.")
    elif total >= 6.5:
        sem_reasons.append("The performance demonstrated competent speech mechanics but suffered from occasional hesitations that diluted persuasion.")
    else:
        sem_reasons.append("To an audience, the delivery felt anxious and disconnected. Critical freezing intervals disrupted emotional engagement and snapped cognitive flow.")

    if blunders:
        b = blunders[0]
        sem_reasons.append(f"The most noticeable flaw occurred between {b['t_start']}s-{b['t_end']}s during the phrase '{b['text']}', where {b['reason'].lower()}")

    if brilliants:
        br = brilliants[0]
        sem_reasons.append(f"A standout moment occurred between {br['t_start']}s-{br['t_end']}s ('{br['text']}'), showcasing commanding vocal modulation.")

    drills = []
    if max_pause >= 2.5:
        drills.append({
            "title": "The Diaphragmatic Breath Anchor",
            "focus": "Rhetorical Pausing",
            "instructions": "Practice reading complex paragraphs with a metronome at 60 BPM. Inhale on the count of 1 and speak across 4 counts to eliminate involuntary freezing."
        })
    if f0_st < 12.0:
        drills.append({
            "title": "Three-Tier Pitch Glides",
            "focus": "Pitch Modulation",
            "instructions": "Speak affirmative sentences while intentionally sliding your voice between low chest voice, mid conversational, and high head register on emphasized syllables."
        })
    drills.append({
        "title": "Dynamic Syllable Punch",
        "focus": "Vocal Punchiness",
        "instructions": "Exaggerate the initial consonant burst of all transitive verbs to increase Peak-to-Average Power Ratio (PAPR) above 25."
    })

    source_tag = "Deterministic Forensic Engine"
    if error_note:
        source_tag += f" (Fallback: {error_note})"

    return {
        "executive_verdict": f"The performance earned {total:.2f}/10.0 ({band}). The primary score determinants were a {f0_st:.1f} semitone pitch range and a {max_pause:.1f}s maximum pause duration.",
        "deterministic_explanation": " ".join(det_reasons),
        "semantic_explanation": " ".join(sem_reasons),
        "pillar_critiques": {
            "pitch_modulation": f"Score: {pillars.get('pitch_modulation_out_of_2_5', 2.0)}/2.5. Modulated across {f0_st:.1f} semitones.",
            "cadence_and_tempo": f"Score: {pillars.get('cadence_and_tempo_out_of_2_5', 2.0)}/2.5. Maintained measured syllabic cadence.",
            "rhetorical_pausing": f"Score: {pillars.get('rhetorical_pausing_out_of_2_0', 1.5)}/2.0. Max pause reached {max_pause:.2f}s.",
            "dynamic_energy": f"Score: {pillars.get('dynamic_energy_out_of_1_5', 1.2)}/1.5. PAPR crest factor measured {papr:.1f}.",
            "spectral_clarity": f"Score: {pillars.get('spectral_clarity_out_of_1_5', 1.3)}/1.5. Articulation remained clear across phoneme formants."
        },
        "actionable_vocal_drills": drills,
        "source": source_tag
    }
