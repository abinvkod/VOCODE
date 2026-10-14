"""
Evaluation Service: 100 Hz Acoustic Telemetry & Non-Unilateral Rubric Grading
Computes physical oratorical features across the 5 pillars and evaluates on a 10.0-pt scale.
"""

import os
import json
from scripts.crunch_evaluation_metrics_and_cluster import extract_detailed_evaluation_metrics
from scripts.grade_speech_corpus import grade_speech

ARCHETYPES_FILE = "findings/oratorical_groups_consensus.json"

def evaluate_audio(
    clean_wav_path: str,
    speech_events: list[dict] | None = None,
    leniency: float = 0.0,
    external_flaws: list[dict] | None = None
) -> dict:
    """
    Extracts dense acoustic metrics and grades the speech across the 5 Oratorical Pillars.
    Supports dynamic leniency calibration (0.0 = strict competition standard, 100.0 = encouraging).
    """
    benchmarks = {}
    if os.path.exists(ARCHETYPES_FILE):
        try:
            with open(ARCHETYPES_FILE, "r", encoding="utf-8") as f:
                consensus_data = json.load(f)
                benchmarks = consensus_data.get("corpus_benchmarks", {})
        except Exception:
            pass

    # Extract 100 Hz acoustic telemetry
    metrics = extract_detailed_evaluation_metrics(clean_wav_path)

    # Attach speech events and transcript stats if available
    if speech_events:
        import re
        full_text = " ".join(e.get("text", "") for e in speech_events).strip()
        words = full_text.split()
        dur_min = max(0.1, metrics.get("duration_sec", 60.0) / 60.0)
        metrics["words_per_minute"] = round(len(words) / dur_min, 1)

        # 1. Immediate consecutive word repetitions ("the the", "I I", "and and")
        word_reps = re.findall(r"\b([a-zA-Z]+)(?:\s+\1)+\b", full_text, flags=re.IGNORECASE)
        
        # 2. Immediate phrase repetitions (2-3 word blocks duplicated immediately)
        phrase_rep_count = 0
        for n in [2, 3]:
            for i in range(len(words) - 2 * n + 1):
                p1 = " ".join(words[i:i+n]).lower()
                p2 = " ".join(words[i+n:i+2*n]).lower()
                if p1 == p2 and len(p1) > 4:
                    phrase_rep_count += 1

        total_reps = len(word_reps) + phrase_rep_count
        rep_density = total_reps / dur_min

        # 3. Filler words ("um", "uh", "er", "ah", "like", "you know")
        token_list = re.findall(r"\b[a-zA-Z]+\b", full_text.lower())
        filler_set = {"um", "uh", "er", "ah"}
        detected_fillers = [w for w in token_list if w in filler_set]
        filler_density = len(detected_fillers) / dur_min

        metrics["word_repetition_count"] = len(word_reps)
        metrics["phrase_repetition_count"] = phrase_rep_count
        metrics["repetition_count"] = total_reps
        metrics["repetition_density_per_min"] = round(rep_density, 2)
        metrics["repeated_words"] = [w.lower() for w in word_reps]
        metrics["filler_words_per_min"] = round(filler_density, 2)
        metrics["filler_count"] = len(detected_fillers)

    # Grade on 10.0-point rubric
    grade_report = grade_speech(
        metrics=metrics,
        benchmarks=benchmarks,
        temporal_flaws=external_flaws or [],
        leniency=leniency
    )

    return {
        "metrics": metrics,
        "grade_report": grade_report
    }
