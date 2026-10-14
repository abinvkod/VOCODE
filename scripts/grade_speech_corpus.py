import os
import json
import numpy as np

METRICS_FILE = "findings/detailed_evaluation_metrics.json"
ARCHETYPES_FILE = "findings/oratorical_groups_consensus.json"
OUTPUT_FILE = "findings/corpus_grades.json"

def grade_speech(
    metrics: dict,
    benchmarks: dict,
    temporal_flaws: list[dict] = None,
    leniency: float = 0.0
) -> dict:
    """
    Evaluates a speech on the 10.0-point rubric across the 5 core pillars:
    1. Pitch Modulation (max 2.5)
    2. Cadence & Tempo (max 2.5)
    3. Rhetorical Pausing (max 2.0)
    4. Dynamic Energy (max 1.5)
    5. Spectral Clarity (max 1.5)
    
    leniency: Human calibration parameter from 0.0 to 100.0.
      - 0.0: Uncompromising strict coaching standard (punishes bad speeches to 4.0 - 5.5 / 10).
      - 50.0: Balanced professional standard.
      - 100.0: Encouraging, lenient novice standard (forgiving flaws up to ~7.0 / 10).
    """
    deductions = []
    
    # -------------------------------------------------------------
    # PILLAR 1: Pitch Modulation & Expressiveness (Max: 2.5 pts)
    # -------------------------------------------------------------
    p1_score = 2.5
    f0_st = metrics.get("f0_semitones", 17.8)
    f0_vel = metrics.get("f0_velocity_hz_per_sec", 648.0)
    
    # Check pitch dynamic range against corpus floor (10.56 st) and mean (17.8 st)
    if f0_st < 7.0:
        pen = 0.8
        p1_score -= pen
        deductions.append({
            "pillar": "Pitch Modulation",
            "deduction": pen,
            "metric": f"f0_semitones: {f0_st} st",
            "flaw": "Severe Monotone Compression",
            "explanation": f"Pitch range was severely compressed to {f0_st} st (corpus floor: 10.56 st). Flat teleprompter-like delivery."
        })
    elif f0_st < 10.56:
        pen = 0.5
        p1_score -= pen
        deductions.append({
            "pillar": "Pitch Modulation",
            "deduction": pen,
            "metric": f"f0_semitones: {f0_st} st",
            "flaw": "Moderate Pitch Compression",
            "explanation": f"Pitch range was {f0_st} st, falling below the 10.56 st corpus baseline floor. Lacks dynamic vocal inflection."
        })
    elif f0_st < 14.0:
        pen = 0.2
        p1_score -= pen
        deductions.append({
            "pillar": "Pitch Modulation",
            "deduction": pen,
            "metric": f"f0_semitones: {f0_st} st",
            "flaw": "Mild Pitch Restraint",
            "explanation": f"Pitch range of {f0_st} st is slightly restrained compared to corpus average (17.8 st)."
        })
        
    # Check pitch velocity (micro-inflection rate)
    if f0_vel < 400.0:
        pen = 0.3
        p1_score -= pen
        deductions.append({
            "pillar": "Pitch Modulation",
            "deduction": pen,
            "metric": f"f0_velocity: {f0_vel} Hz/s",
            "flaw": "Sluggish Vocal Inflection",
            "explanation": f"Pitch velocity was {f0_vel} Hz/s (baseline: 648 Hz/s), indicating slow inflectional modulation."
        })
    p1_score = max(0.0, round(p1_score, 2))

    # -------------------------------------------------------------
    # PILLAR 2: Cadence, Pacing & Speech Rate (Max: 2.5 pts)
    # -------------------------------------------------------------
    p2_score = 2.5
    rate = metrics.get("articulation_rate_sps", 5.68)
    tempo_std = metrics.get("tempo_stability_std", 0.28)
    
    # Check speech rate against corpus floor (5.22) and ceiling (6.10)
    if rate > 6.4:
        pen = 0.4
        p2_score -= pen
        deductions.append({
            "pillar": "Cadence & Tempo",
            "deduction": pen,
            "metric": f"articulation_rate: {rate} syl/s",
            "flaw": "Rushed Delivery",
            "explanation": f"Speech rate accelerated to {rate} syl/s (corpus ceiling: 6.10 syl/s). Audience has insufficient time to digest points."
        })
    elif rate > 6.10:
        pen = 0.2
        p2_score -= pen
        deductions.append({
            "pillar": "Cadence & Tempo",
            "deduction": pen,
            "metric": f"articulation_rate: {rate} syl/s",
            "flaw": "Mild Cadence Acceleration",
            "explanation": f"Speech rate of {rate} syl/s is slightly brisk compared to corpus average (5.68 syl/s)."
        })
    elif rate < 4.5:
        pen = 0.4
        p2_score -= pen
        deductions.append({
            "pillar": "Cadence & Tempo",
            "deduction": pen,
            "metric": f"articulation_rate: {rate} syl/s",
            "flaw": "Sluggish Dragging",
            "explanation": f"Speech rate dragged at {rate} syl/s (corpus floor: 5.22 syl/s), eroding momentum."
        })
    elif rate < 5.22:
        pen = 0.2
        p2_score -= pen
        deductions.append({
            "pillar": "Cadence & Tempo",
            "deduction": pen,
            "metric": f"articulation_rate: {rate} syl/s",
            "flaw": "Slow Pacing",
            "explanation": f"Speech rate of {rate} syl/s is slower than typical oratorical tempo."
        })
        
    # Check tempo stability
    if tempo_std > 0.50:
        pen = 0.3
        p2_score -= pen
        deductions.append({
            "pillar": "Cadence & Tempo",
            "deduction": pen,
            "metric": f"tempo_stability_std: {tempo_std}",
            "flaw": "Erratic Cadence Fluctuation",
            "explanation": f"High tempo variance ({tempo_std}) reflects erratic speed changes across sentences."
        })
    p2_score = max(0.0, round(p2_score, 2))

    # -------------------------------------------------------------
    # PILLAR 3: Rhetorical Pausing & Fluency (Max: 2.0 pts)
    # -------------------------------------------------------------
    p3_score = 2.0
    pause_ratio = metrics.get("pause_ratio", 0.20)
    avg_pause = metrics.get("avg_pause_duration_sec", 0.72)
    hesitation_cnt = metrics.get("hesitation_pause_count", 0)
    
    # Check 20% Pause Law (bounds: 17% - 23%)
    if pause_ratio < 0.14:
        pen = 0.5
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"pause_ratio: {pause_ratio*100:.1f}%",
            "flaw": "Severe Breathless Run-On",
            "explanation": f"Pause ratio was only {pause_ratio*100:.1f}% (corpus floor: 17.0%). Suffocating delivery with almost no breathing room."
        })
    elif pause_ratio < 0.17:
        pen = 0.25
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"pause_ratio: {pause_ratio*100:.1f}%",
            "flaw": "Insufficient Pausing",
            "explanation": f"Pause ratio of {pause_ratio*100:.1f}% is below the 20% oratorical law."
        })
    elif pause_ratio > 0.25:
        pen = 0.4
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"pause_ratio: {pause_ratio*100:.1f}%",
            "flaw": "Disjointed Hesitation",
            "explanation": f"Pause ratio reached {pause_ratio*100:.1f}% (corpus ceiling: 23.0%), making the speech sound halted."
        })
        
    # Check hesitation pauses (>1.5s dead air) and maximum freeze duration
    duration = metrics.get("duration_sec", 60.0)
    hesitation_rate_per_min = (hesitation_cnt / (duration / 60.0)) if duration > 0 else 0
    max_pause_sec = metrics.get("max_pause_duration_sec", 1.5)
    
    # Critical Factor: Paralyzing Dead-Air Freeze (> 3.0s or > 5.0s)
    if max_pause_sec >= 5.0:
        pen = 0.8
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"max_pause_duration: {max_pause_sec:.1f}s",
            "flaw": "Paralyzing Dead-Air Freeze",
            "explanation": f"Prolonged stage freeze of {max_pause_sec:.1f} seconds completely ruptured audience rapport."
        })
    elif max_pause_sec >= 3.0:
        pen = 0.4
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"max_pause_duration: {max_pause_sec:.1f}s",
            "flaw": "Extended Awkward Silence",
            "explanation": f"Unfilled silence of {max_pause_sec:.1f} seconds exceeded rhetorical bounds."
        })
        
    if hesitation_rate_per_min > 2.0:
        pen = 0.3
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing",
            "deduction": pen,
            "metric": f"hesitations_per_min: {hesitation_rate_per_min:.1f}",
            "flaw": "Frequent Hesitations",
            "explanation": f"Frequent silences exceeding 1.5 seconds ({hesitation_cnt} total) disrupted narrative flow."
        })

    # Critical Factor: Filler words & vocal disfluencies
    fillers_per_min = metrics.get("filler_words_per_min", 0.0)
    if fillers_per_min > 5.0:
        pen = 0.8
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"filler_words_per_min: {fillers_per_min:.1f}",
            "flaw": "Severe Filler Word Clutter",
            "explanation": f"High density of vocal fillers ({fillers_per_min:.1f}/min, e.g. 'um', 'uh', 'like') undermines audience retention and credibility."
        })
    elif fillers_per_min > 2.0:
        pen = 0.4
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"filler_words_per_min: {fillers_per_min:.1f}",
            "flaw": "Frequent Filler Words",
            "explanation": f"Noticeable filler word frequency ({fillers_per_min:.1f}/min) disrupts smooth syntactic phrasing."
        })

    # Critical Factor: Strict Sentence / Phrase Repetitions & False Starts
    rep_density = metrics.get("repetition_density_per_min", 0.0)
    false_starts = metrics.get("false_start_count", 0)
    word_reps = metrics.get("word_repetition_count", metrics.get("repetition_count", 0))
    
    if rep_density >= 20.0 or false_starts >= 4:
        pen = 0.9
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"repetition_density: {rep_density:.1f}/min, false_starts: {false_starts}",
            "flaw": "Severe Sentence Repetition & Syntactic Loop",
            "explanation": f"Heavy cyclic phrase restarts ({rep_density:.1f}/min) and false starts ({false_starts}) reflect cognitive stalling or loss of train of thought."
        })
    elif rep_density >= 12.0 or false_starts >= 2:
        pen = 0.5
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"repetition_density: {rep_density:.1f}/min, false_starts: {false_starts}",
            "flaw": "Frequent Phrase Duplication & Restarts",
            "explanation": f"Repeated phrase loops ({rep_density:.1f}/min) disrupt narrative coherence."
        })
        
    rep_words_list = metrics.get("repeated_words", [])
    rep_examples = f" (e.g. '{', '.join(rep_words_list[:3])}')" if rep_words_list else ""
    if word_reps >= 3:
        pen = 0.35
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"word_repetitions: {word_reps}",
            "flaw": "Audible Lexical Stutter Repetitions",
            "explanation": f"Multiple consecutive word stutter repetitions ({word_reps} instances{rep_examples}) impair oratorical fluency and authority."
        })
    elif word_reps >= 1:
        pen = 0.15
        p3_score -= pen
        deductions.append({
            "pillar": "Rhetorical Pausing & Fluency",
            "deduction": pen,
            "metric": f"word_repetitions: {word_reps}",
            "flaw": "Lexical Word Repetition",
            "explanation": f"Unintended consecutive word repetition ({word_reps} instance{rep_examples}) momentarily halts speech flow."
        })

    p3_score = max(0.0, round(p3_score, 2))

    # -------------------------------------------------------------
    # PILLAR 4: Dynamic Energy & Vocal Projection (Max: 1.5 pts)
    # -------------------------------------------------------------
    p4_score = 1.5
    energy_range = metrics.get("energy_dynamic_range_db", 41.67)
    papr = metrics.get("papr_crest_factor", 39.65)
    yelling_strain = metrics.get("yelling_detected", False)
    
    # Critical Factor: Uncontrolled Shouting & Vocal Strain (Phil Davison pathology)
    if yelling_strain:
        pen = 0.6
        p4_score -= pen
        deductions.append({
            "pillar": "Dynamic Energy",
            "deduction": pen,
            "metric": "yelling_detected: True",
            "flaw": "Uncontrolled Shouting & Vocal Strain",
            "explanation": "Delivery pushed into unmodulated high-register shouting with negligible dynamic shade, causing severe listener fatigue."
        })
        
    if energy_range < 25.0:
        pen = 0.4
        p4_score -= pen
        deductions.append({
            "pillar": "Dynamic Energy",
            "deduction": pen,
            "metric": f"energy_dynamic_range: {energy_range} dB",
            "flaw": "Compressed Volume Dynamics",
            "explanation": f"Volume range was only {energy_range} dB (corpus floor: 27.36 dB). Monotonous volume throughout."
        })
    elif energy_range < 30.0:
        pen = 0.2
        p4_score -= pen
        deductions.append({
            "pillar": "Dynamic Energy",
            "deduction": pen,
            "metric": f"energy_dynamic_range: {energy_range} dB",
            "flaw": "Mild Dynamic Flatness",
            "explanation": f"Volume dynamic range was {energy_range} dB, slightly lower than typical masterclass contrast."
        })
        
    # Check vocal punchiness (PAPR)
    if papr < 15.0:
        pen = 0.3
        p4_score -= pen
        deductions.append({
            "pillar": "Dynamic Energy",
            "deduction": pen,
            "metric": f"papr_crest_factor: {papr}",
            "flaw": "Low Vocal Punchiness",
            "explanation": f"PAPR of {papr} indicates lack of contrast between stressed and unstressed syllables."
        })
    p4_score = max(0.0, round(p4_score, 2))

    # -------------------------------------------------------------
    # PILLAR 5: Spectral Clarity & Enunciation (Max: 1.5 pts)
    # -------------------------------------------------------------
    p5_score = 1.5
    flux = metrics.get("spectral_flux", 4.73)
    
    if flux < 2.5:
        pen = 0.4
        p5_score -= pen
        deductions.append({
            "pillar": "Spectral Clarity",
            "deduction": pen,
            "metric": f"spectral_flux: {flux}",
            "flaw": "Slurred Enunciation",
            "explanation": f"Low spectral flux ({flux}) indicates sluggish consonant articulation and muddled diction."
        })
    elif flux < 3.2:
        pen = 0.2
        p5_score -= pen
        deductions.append({
            "pillar": "Spectral Clarity",
            "deduction": pen,
            "metric": f"spectral_flux: {flux}",
            "flaw": "Subdued Phonetic Contrast",
            "explanation": f"Spectral flux of {flux} is below corpus average (4.73)."
        })
    p5_score = max(0.0, round(p5_score, 2))

    # -------------------------------------------------------------
    # TEMPORALLY GROUNDED FLAW OCCURRENCES (Track C Integration)
    # -------------------------------------------------------------
    if temporal_flaws:
        for flaw in temporal_flaws:
            f_type = flaw.get("flaw_type", flaw.get("flaw_id", "UNKNOWN"))
            t_s = flaw.get("t_start", 0.0)
            t_e = flaw.get("t_end", 0.0)
            expl = flaw.get("causal_explanation", flaw.get("description", "Acoustic anomaly detected."))
            
            if "monotone" in f_type.lower() or "FLAW-1" in f_type:
                # Severity based on duration or flattening
                dur = t_e - t_s
                pen = 0.9 if dur >= 6.0 else 0.35
                p1_score = max(0.0, p1_score - pen)
                deductions.append({
                    "pillar": "Pitch Modulation",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Flatline (Monotone)",
                    "explanation": expl
                })
            elif "rushed" in f_type.lower() or "FLAW-2" in f_type:
                pen = 0.8
                p2_score = max(0.0, p2_score - pen)
                deductions.append({
                    "pillar": "Cadence & Tempo",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Cadence Acceleration",
                    "explanation": expl
                })
            elif "hesitation" in f_type.lower() or "dead_air" in f_type.lower() or "pause" in f_type.lower() or "FLAW-3" in f_type:
                dur = t_e - t_s
                pen = 1.2 if dur >= 3.0 else (0.6 if dur >= 2.0 else 0.25)
                p3_score = max(0.0, p3_score - pen)
                deductions.append({
                    "pillar": "Rhetorical Pausing",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Dead-Air Freeze" if dur >= 3.0 else "Temporally Grounded Hesitation",
                    "explanation": expl
                })
            elif "stammer" in f_type.lower() or "repetition" in f_type.lower():
                pen = 0.9
                p2_score = max(0.0, p2_score - pen)
                deductions.append({
                    "pillar": "Cadence & Tempo",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Stammer Repetition Loop",
                    "explanation": expl
                })
            elif "clipped" in f_type.lower() or "FLAW-4" in f_type:
                pen = 0.8
                p3_score = max(0.0, p3_score - pen)
                deductions.append({
                    "pillar": "Rhetorical Pausing",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Clipped Pause",
                    "explanation": expl
                })
            elif "energy" in f_type.lower() or "inversion" in f_type.lower() or "FLAW-5" in f_type:
                pen = 0.9
                p4_score = max(0.0, p4_score - pen)
                deductions.append({
                    "pillar": "Dynamic Energy",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Climax Energy Collapse",
                    "explanation": expl
                })
            elif "mumble" in f_type.lower() or "trail" in f_type.lower() or "FLAW-6" in f_type:
                pen = 0.9
                p5_score = max(0.0, p5_score - pen)
                deductions.append({
                    "pillar": "Spectral Clarity",
                    "deduction": pen,
                    "temporal_interval": [t_s, t_e],
                    "flaw": "Temporally Grounded Mumble & Trail-Off",
                    "explanation": expl
                })


    p1_score = round(p1_score, 2)
    p2_score = round(p2_score, 2)
    p3_score = round(p3_score, 2)
    p4_score = round(p4_score, 2)
    p5_score = round(p5_score, 2)

    # -------------------------------------------------------------
    # NON-UNILATERAL COMPOUND GATING ARCHITECTURE
    # -------------------------------------------------------------
    import math
    lam = max(0.0, min(100.0, float(leniency)))
    penalty_scale = 1.70 - 0.90 * (lam / 100.0)
    
    # 1. Systemic Quality Impairment Index (Psi_impair)
    # Higher weights for core quality destroyers (Repetitions, Freezes, Severe Monotone, Shouting Strain)
    psi_impair = 0.0
    critical_deficits = 0
    
    # High impact factor: Repetition & Syntactic Breakdown (weight: 1.8)
    if rep_density >= 20.0 or false_starts >= 4:
        psi_impair += 1.6
        critical_deficits += 1
    elif rep_density >= 12.0 or false_starts >= 2:
        psi_impair += 0.8
        critical_deficits += 1
        
    # High impact factor: Filler word clutter
    if fillers_per_min >= 4.5:
        psi_impair += 1.2
        critical_deficits += 1
    elif fillers_per_min >= 2.0:
        psi_impair += 0.6
        critical_deficits += 1
        
    # High impact factor: Monotone flatline (weight: 1.5)
    if f0_st < 7.0:
        psi_impair += 1.5
        critical_deficits += 1
    elif f0_st < 10.56:
        psi_impair += 0.7
        critical_deficits += 1
    elif f0_st < 13.5:
        psi_impair += 0.2
        
    # High impact factor: Paralyzing Dead-Air Freeze (weight: 1.6)
    if max_pause_sec >= 5.0:
        psi_impair += 1.5
        critical_deficits += 1
    elif max_pause_sec >= 3.0:
        psi_impair += 0.8
        critical_deficits += 1
        
    # High impact factor: Breathless Run-On Pauses (weight: 1.2)
    if pause_ratio < 0.13:
        psi_impair += 1.3
        critical_deficits += 1
    elif pause_ratio < 0.17:
        psi_impair += 0.4
        
    # High impact factor: Uncontrolled Screaming / Vocal Strain (weight: 1.3)
    if yelling_strain:
        psi_impair += 1.4
        critical_deficits += 1
        
    # Non-Unilateral Coupling Term (amplifies when multiple critical dimensions fail simultaneously)
    coupling = 0.55 * max(0, critical_deficits - 1)
    
    raw_deductions_sum = (2.5 - p1_score) + (2.5 - p2_score) + (2.0 - p3_score) + (1.5 - p4_score) + (1.5 - p5_score)
    total_deduction = (raw_deductions_sum + coupling) * penalty_scale
    
    # Non-Unilateral Soft Ceiling Gate:
    # A single isolated deficit does NOT unilaterally clamp the entire speech.
    # Compound gating triggers when multiple critical dimensions fail simultaneously (deficits >= 2)
    # or when an individual dimension suffers catastrophic collapse (psi_impair >= 2.0).
    if critical_deficits >= 2 or psi_impair >= 2.0:
        max_allowed_ceiling = 10.0 - 4.8 * math.tanh(max(0.0, psi_impair - 0.6) / 2.0) * (1.0 - 0.40 * (lam / 100.0))
    else:
        max_allowed_ceiling = 10.0
    
    raw_score = 10.0 - total_deduction
    total_score = min(raw_score, max_allowed_ceiling)
    total_score = max(1.0, min(10.0, round(total_score, 1)))
    
    # Assign Performance Band
    if total_score >= 9.0:
        grade_band = "Masterclass Oratory (Tier 0)"
    elif total_score >= 8.0:
        grade_band = "Distinguished / Minor Polish (Tier 1)"
    elif total_score >= 6.5:
        grade_band = "Proficient / Noticeable Flaws (Tier 2)"
    elif total_score >= 5.0:
        grade_band = "Developing / Inconsistent (Tier 3)"
    else:
        grade_band = "Novice / Severely Flawed (Tier 3)"
        
    return {
        "title": metrics.get("title"),
        "speaker": metrics.get("speaker"),
        "total_grade": total_score,
        "grade_band": grade_band,
        "pillar_scores": {
            "pitch_modulation_out_of_2_5": p1_score,
            "cadence_and_tempo_out_of_2_5": p2_score,
            "rhetorical_pausing_out_of_2_0": p3_score,
            "dynamic_energy_out_of_1_5": p4_score,
            "spectral_clarity_out_of_1_5": p5_score
        },
        "gating_diagnostics": {
            "psi_impairment_index": round(psi_impair, 2),
            "critical_deficits_count": critical_deficits,
            "coupling_penalty": round(coupling, 2),
            "gate_ceiling": round(max_allowed_ceiling, 2)
        },
        "deductions_count": len(deductions),
        "deductions": deductions
    }

def main():
    with open(METRICS_FILE, 'r', encoding='utf-8') as f:
        corpus_metrics = json.load(f)
        
    with open(ARCHETYPES_FILE, 'r', encoding='utf-8') as f:
        consensus_data = json.load(f)
    benchmarks = consensus_data.get("corpus_benchmarks", {})
    
    graded_corpus = []
    print(f"Grading {len(corpus_metrics)} speech samples on the 10.0-point rubric...\n")
    
    for idx, entry in enumerate(corpus_metrics, 1):
        grade_res = grade_speech(entry, benchmarks)
        grade_res["folder"] = entry.get("folder")
        graded_corpus.append(grade_res)
        
        status_tag = f"[{idx}/{len(corpus_metrics)}] {grade_res['total_grade']}/10.0 ({grade_res['grade_band'][:15]})"
        print(f"{status_tag:38} | {grade_res['title'][:45]}")

    # Compute Grade Summary Statistics
    grades = [g["total_grade"] for g in graded_corpus]
    avg_grade = round(float(np.mean(grades)), 2)
    median_grade = round(float(np.median(grades)), 2)
    max_grade = float(np.max(grades))
    min_grade = float(np.min(grades))
    
    band_counts = {}
    for g in graded_corpus:
        b = g["grade_band"].split("(")[0].strip()
        band_counts[b] = band_counts.get(b, 0) + 1
        
    summary_report = {
        "total_evaluated_speeches": len(graded_corpus),
        "mean_grade": avg_grade,
        "median_grade": median_grade,
        "highest_grade": max_grade,
        "lowest_grade": min_grade,
        "grade_band_distribution": band_counts,
        "graded_speeches": sorted(graded_corpus, key=lambda x: x["total_grade"], reverse=True)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2)
        
    print("\n=======================================================")
    print("GRADING COMPLETE!")
    print(f"Corpus Average Grade: {avg_grade} / 10.0 (Median: {median_grade} / 10.0)")
    print(f"Highest Grade: {max_grade} / 10.0 | Lowest: {min_grade} / 10.0")
    print(f"Grade Band Counts: {band_counts}")
    print(f"Saved full scorecard to: {OUTPUT_FILE}")
    print("=======================================================")

if __name__ == "__main__":
    main()
