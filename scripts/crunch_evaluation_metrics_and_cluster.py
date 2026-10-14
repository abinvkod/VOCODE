import os
import json
import glob
import numpy as np
import scipy.signal as signal
import soundfile as sf
import librosa
import parselmouth
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score

BASE_DIR = "good speeches"
FINDINGS_DIR = "findings"

def extract_detailed_evaluation_metrics(wav_path: str) -> dict:
    """
    Extracts the full 12-factor evaluation metrics across the 5 core oratorical pillars:
    Pillar 1: Pitch Modulation & Expressiveness
    Pillar 2: Cadence, Pacing & Speech Rate
    Pillar 3: Rhetorical Pausing & Fluency
    Pillar 4: Dynamic Energy & Vocal Projection
    Pillar 5: Spectral Clarity & Phonetic Enunciation
    """
    y, sr = sf.read(wav_path, dtype='float32')
    if y.ndim > 1:
        y = np.mean(y, axis=1 if y.shape[1] < y.shape[0] else 0)
    duration = float(len(y) / sr)
    
    # -------------------------------------------------------------
    # PILLAR 1: Pitch Modulation & Expressiveness (Praat Parselmouth)
    # -------------------------------------------------------------
    snd = parselmouth.Sound(wav_path)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75.0, pitch_ceiling=500.0)
    pitch_values = pitch.selected_array['frequency']
    voiced_f0 = pitch_values[pitch_values > 0]
    
    voiced_frame_ratio = float(len(voiced_f0) / len(pitch_values)) if len(pitch_values) > 0 else 0.0
    
    if len(voiced_f0) > 20:
        f0_mean = float(np.mean(voiced_f0))
        f0_std = float(np.std(voiced_f0))
        f0_median = float(np.median(voiced_f0))
        f0_p05 = float(np.percentile(voiced_f0, 5))
        f0_p95 = float(np.percentile(voiced_f0, 95))
        f0_semitones = float(12.0 * np.log2((f0_p95 + 1e-6) / (f0_p05 + 1e-6)))
        
        # Speaker-normalized z-score pitch contour
        z_f0 = (voiced_f0 - f0_mean) / (f0_std + 1e-6)
        f0_z_std = float(np.std(z_f0)) # relative modulation
        
        # Pitch velocity (absolute rate of pitch modulation |dF0/dt| in Hz/sec)
        diff_f0 = np.abs(np.diff(voiced_f0)) / 0.01
        f0_velocity = float(np.mean(diff_f0)) if len(diff_f0) > 0 else 0.0
        
        # Local pitch excursions (max semitone leap across 200ms windows)
        win = 20
        if len(voiced_f0) > win:
            local_ratios = [voiced_f0[i+win] / (voiced_f0[i] + 1e-6) for i in range(len(voiced_f0) - win)]
            f0_max_jump_semitones = float(np.max(np.abs(12.0 * np.log2(np.array(local_ratios) + 1e-6))))
        else:
            f0_max_jump_semitones = 6.0
    else:
        f0_mean = 120.0
        f0_std = 12.0
        f0_median = 120.0
        f0_semitones = 3.0
        f0_z_std = 0.5
        f0_velocity = 20.0
        f0_max_jump_semitones = 2.0

    # -------------------------------------------------------------
    # PILLAR 2: Dynamic Energy & Vocal Projection
    # -------------------------------------------------------------
    frame_len = 512
    hop_len = 160 # 10ms frame step at 16kHz
    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    rms_db = 20.0 * np.log10(rms + 1e-7)
    
    energy_mean_db = float(np.mean(rms_db))
    energy_std_db = float(np.std(rms_db))
    energy_p05 = float(np.percentile(rms_db, 5))
    energy_p95 = float(np.percentile(rms_db, 95))
    energy_dynamic_range_db = float(energy_p95 - energy_p05)
    
    # Peak-to-Average Power Ratio (PAPR / Crest Factor / Vocal Punchiness)
    mean_power = float(np.mean(rms**2) + 1e-10)
    max_power = float(np.max(rms**2) + 1e-10)
    papr_crest_factor = float(max_power / mean_power)

    # -------------------------------------------------------------
    # PILLAR 3: Rhetorical Pausing & Fluency
    # -------------------------------------------------------------
    # Adaptive silence threshold: 20th percentile + 3.0 dB
    silence_thresh = np.percentile(rms_db, 20) + 3.0
    is_silent = rms_db < silence_thresh
    
    silence_segments = []
    in_silence = False
    run_start = 0
    for idx, sil in enumerate(is_silent):
        if sil and not in_silence:
            in_silence = True
            run_start = idx
        elif not sil and in_silence:
            in_silence = False
            dur_sec = (idx - run_start) * (hop_len / sr)
            if dur_sec >= 0.25: # minimum pause threshold 250ms
                silence_segments.append(dur_sec)
    if in_silence:
        dur_sec = (len(is_silent) - run_start) * (hop_len / sr)
        if dur_sec >= 0.25:
            silence_segments.append(dur_sec)
            
    total_pause_time = float(sum(silence_segments))
    pause_ratio = float(total_pause_time / (duration + 1e-6))
    pause_count = len(silence_segments)
    pauses_per_minute = float((pause_count / (duration + 1e-6)) * 60.0)
    avg_pause_duration = float(np.mean(silence_segments)) if silence_segments else 0.0
    
    # Rhetorical dramatic pauses (500ms - 1500ms) vs hesitations (>1500ms)
    rhetorical_pauses = [p for p in silence_segments if 0.50 <= p <= 1.50]
    hesitation_pauses = [p for p in silence_segments if p > 1.50]
    
    rhetorical_pause_ratio = float(len(rhetorical_pauses) / pause_count) if pause_count > 0 else 0.0
    hesitation_count = len(hesitation_pauses)

    # -------------------------------------------------------------
    # PILLAR 4: Cadence, Pacing & Speech Rate
    # -------------------------------------------------------------
    # Syllabic onset envelope peak picking (syllable proxy)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_len)
    peaks = signal.find_peaks(onset_env, distance=15)[0]
    syllable_count = len(peaks)
    active_speech_time = max(1.0, duration - total_pause_time)
    articulation_rate_sps = float(syllable_count / active_speech_time)
    
    # Cadence stability (variation in local 5-second syllable rates)
    chunk_frames = int(5.0 * (sr / hop_len))
    num_chunks = len(onset_env) // chunk_frames
    if num_chunks > 1:
        chunk_rates = []
        for c in range(num_chunks):
            sub_peaks = [p for p in peaks if c * chunk_frames <= p < (c+1) * chunk_frames]
            chunk_rates.append(len(sub_peaks) / 5.0)
        tempo_stability_std = float(np.std(chunk_rates))
    else:
        tempo_stability_std = 0.5

    # -------------------------------------------------------------
    # PILLAR 5: Spectral Clarity & Phonetic Enunciation
    # -------------------------------------------------------------
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_len)[0]
    sc_mean = float(np.mean(spectral_centroid))
    sc_std = float(np.std(spectral_centroid))
    
    # Spectral Flux (rate of change of spectral timbre)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_len)
    spectral_flux = float(np.sqrt(np.mean(np.diff(mel_spec, axis=1)**2)))

    # Maximum pause duration and vocal strain / shouting dynamics
    max_pause_duration = float(np.max(silence_segments)) if silence_segments else 0.0
    active_rms = rms_db[rms_db > -35.0]
    active_rms_std = float(np.std(active_rms)) if len(active_rms) > 10 else 10.0
    yelling_detected = bool(f0_mean > 220.0 and active_rms_std < 7.5 and energy_mean_db > -25.0)

    return {
        "duration_sec": round(duration, 2),
        "voiced_frame_ratio": round(voiced_frame_ratio, 3),
        # Pillar 1: Pitch Modulation
        "f0_mean_hz": round(f0_mean, 2),
        "f0_std_hz": round(f0_std, 2),
        "f0_median_hz": round(f0_median, 2),
        "f0_semitones": round(f0_semitones, 2),
        "f0_velocity_hz_per_sec": round(f0_velocity, 2),
        "f0_max_jump_semitones": round(f0_max_jump_semitones, 2),
        # Pillar 2: Dynamic Energy
        "energy_mean_db": round(energy_mean_db, 2),
        "energy_std_db": round(energy_std_db, 2),
        "active_dynamic_std_db": round(active_rms_std, 2),
        "energy_dynamic_range_db": round(energy_dynamic_range_db, 2),
        "papr_crest_factor": round(papr_crest_factor, 2),
        "yelling_detected": yelling_detected,
        # Pillar 3: Pauses & Fluency
        "pause_ratio": round(pause_ratio, 3),
        "pause_count": pause_count,
        "pauses_per_minute": round(pauses_per_minute, 2),
        "avg_pause_duration_sec": round(avg_pause_duration, 3),
        "max_pause_duration_sec": round(max_pause_duration, 2),
        "rhetorical_pause_ratio": round(rhetorical_pause_ratio, 3),
        "hesitation_pause_count": hesitation_count,
        # Pillar 4: Cadence & Pacing
        "articulation_rate_sps": round(articulation_rate_sps, 2),
        "tempo_stability_std": round(tempo_stability_std, 2),
        # Pillar 5: Spectral Quality
        "spectral_centroid_mean_hz": round(sc_mean, 2),
        "spectral_centroid_std_hz": round(sc_std, 2),
        "spectral_flux": round(spectral_flux, 4)
    }

def main():
    os.makedirs(FINDINGS_DIR, exist_ok=True)
    folders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    corpus_entries = []
    
    print("Crunching evaluation metrics across all preprocessed speeches...")
    for idx, folder in enumerate(folders, 1):
        folder_path = os.path.join(BASE_DIR, folder)
        clean_wav = os.path.join(folder_path, "preprocessed_clean.wav")
        meta_file = os.path.join(folder_path, "metadata.json")
        
        if not os.path.exists(clean_wav):
            continue
            
        title = folder
        speaker = "Unknown"
        if os.path.exists(meta_file):
            try:
                with open(meta_file) as f:
                    m = json.load(f)
                    title = m.get("title", folder)
            except Exception:
                pass
                
        # Clean title
        if "|" in title:
            speaker_candidate = title.split("|")[0].strip()
        elif "-" in title:
            speaker_candidate = title.split("-")[0].strip()
        else:
            speaker_candidate = title.split()[0] if title else "Orator"
            
        metrics = extract_detailed_evaluation_metrics(clean_wav)
        metrics["folder"] = folder
        metrics["title"] = title
        metrics["speaker"] = speaker_candidate
        corpus_entries.append(metrics)
        print(f"[{len(corpus_entries)}/34] Processed: {title[:45]} | Range: {metrics['f0_semitones']}st | Pause: {metrics['pause_ratio']*100:.1f}%")

    # Save master tabular dataset
    metrics_json_path = os.path.join(FINDINGS_DIR, "detailed_evaluation_metrics.json")
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(corpus_entries, f, indent=2)
    print(f"\nSaved detailed evaluation metrics to {metrics_json_path}")

    # -------------------------------------------------------------
    # CLUSTERING & CONSENSUS ANNOTATION
    # -------------------------------------------------------------
    feature_columns = [
        "f0_semitones",
        "f0_velocity_hz_per_sec",
        "energy_dynamic_range_db",
        "papr_crest_factor",
        "pause_ratio",
        "pauses_per_minute",
        "avg_pause_duration_sec",
        "rhetorical_pause_ratio",
        "articulation_rate_sps",
        "tempo_stability_std",
        "spectral_centroid_mean_hz",
        "spectral_flux"
    ]
    
    X = np.array([[entry[col] for col in feature_columns] for entry in corpus_entries])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # PCA Embedding
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = [round(float(v), 3) for v in pca.explained_variance_ratio_]
    
    # Silhouette & Calinski-Harabasz score analysis
    k_scores = {}
    for k in [2, 3, 4, 5]:
        km = KMeans(n_clusters=k, random_state=42, n_init=15)
        labels = km.fit_predict(X_scaled)
        sil = float(silhouette_score(X_scaled, labels))
        ch = float(calinski_harabasz_score(X_scaled, labels))
        k_scores[k] = {"silhouette": sil, "calinski_harabasz": ch}
        
    # We select k=3 as it yields the most natural rhetorical archetypes
    optimal_k = 3
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=15)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    for i, entry in enumerate(corpus_entries):
        entry["cluster_id"] = int(cluster_labels[i])
        entry["pca_dim1"] = round(float(X_pca[i, 0]), 3)
        entry["pca_dim2"] = round(float(X_pca[i, 1]), 3)

    # -------------------------------------------------------------
    # CONSENSUS PROFILES & ANNOTATIONS FOR EACH GROUP
    # -------------------------------------------------------------
    # Compute overall corpus baselines
    corpus_means = {col: round(float(np.mean([e[col] for e in corpus_entries])), 2) for col in feature_columns}
    
    archetype_definitions = {
        0: {
            "archetype_id": 0,
            "title": "Passionate Crescendo & High-Activation Orators",
            "style_definition": "High emotional activation, expansive musical dynamic range, dramatic pitch velocity, and deliberate extended theatrical pauses before thesis crescendos.",
            "rhetorical_intent": "Inspirational appeals, moral declamations, urgent calls to action, and cinematic dramatic storytelling.",
            "rubric_grading_posture": "Judges expect expansive pitch excursion on operative keywords (>=18 semitones) and substantial dramatic pauses (>=0.85s) before climaxes. Penalize flat inflection or rushed climaxes."
        },
        1: {
            "archetype_id": 1,
            "title": "Authoritative & Measured Statesmen",
            "style_definition": "Controlled musical pitch dynamic range, steady articulation tempo, disciplined syntactic pause placement, and high pause cadence with medium pause lengths.",
            "rhetorical_intent": "Presidential inaugurations, wartime declarations, motivational instruction, and strategic thought leadership.",
            "rubric_grading_posture": "Judges reward disciplined clause bounding, steady cadence stability, and dignified vocal projection without theatrical melodrama. Penalize erratic pacing or disjointed syntax."
        },
        2: {
            "archetype_id": 2,
            "title": "Intimate & Meditative Narrative Exposition",
            "style_definition": "Gentle vocal modulation, slower articulation tempo, wide studio mastering dynamic range, and extended meditative pauses.",
            "rhetorical_intent": "Reflective philosophies, personal parables, deep pedagogical instruction, and introspective lectures.",
            "rubric_grading_posture": "Judges reward warmth, steady breath control, vocal clarity, and unhurried pacing. Penalize harsh loudness spikes or rushed narrative transitions."
        }
    }
    
    # Match the clusters to their most appropriate archetype definition based on pitch range & pause duration
    groups_summary = {}
    for c_id in range(optimal_k):
        members = [e for e in corpus_entries if e["cluster_id"] == c_id]
        if not members:
            continue
        c_mean_pitch = np.mean([m["f0_semitones"] for m in members])
        c_mean_pause = np.mean([m["avg_pause_duration_sec"] for m in members])
        c_mean_rate = np.mean([m["articulation_rate_sps"] for m in members])
        c_mean_papr = np.mean([m["papr_crest_factor"] for m in members])
        
        # Decide archetype identity based on cluster centroid traits
        if c_mean_pitch > 19.0:
            arch_meta = archetype_definitions[0] # Crescendo Orators
        elif c_mean_rate < 5.2 or len(members) <= 2:
            arch_meta = archetype_definitions[2] # Narrative/Meditative
        else:
            arch_meta = archetype_definitions[1] # Measured Statesmen
            
        centroids = {col: round(float(np.mean([m[col] for m in members])), 2) for col in feature_columns}
        deviations_from_corpus = {
            col: round(float(((centroids[col] - corpus_means[col]) / (corpus_means[col] + 1e-6)) * 100.0), 1)
            for col in feature_columns
        }
        
        groups_summary[c_id] = {
            "group_id": c_id,
            "name": arch_meta["title"],
            "speech_count": len(members),
            "percentage_of_corpus": round(float((len(members) / len(corpus_entries)) * 100.0), 1),
            "style_definition": arch_meta["style_definition"],
            "rhetorical_intent": arch_meta["rhetorical_intent"],
            "rubric_grading_posture": arch_meta["rubric_grading_posture"],
            "centroids": centroids,
            "deviations_vs_corpus_percent": deviations_from_corpus,
            "representative_speeches": [
                {
                    "title": m["title"],
                    "speaker": m["speaker"],
                    "pitch_semitones": m["f0_semitones"],
                    "pause_ratio": m["pause_ratio"],
                    "articulation_rate": m["articulation_rate_sps"]
                }
                for m in members[:6]
            ]
        }
        
    master_consensus = {
        "corpus_size": len(corpus_entries),
        "feature_metrics": feature_columns,
        "corpus_benchmarks": corpus_means,
        "pca_variance_explained": var_explained,
        "clustering_metrics": k_scores,
        "oratorical_groups": groups_summary
    }
    
    consensus_out = os.path.join(FINDINGS_DIR, "oratorical_groups_consensus.json")
    with open(consensus_out, 'w', encoding='utf-8') as f:
        json.dump(master_consensus, f, indent=2)
        
    print("\n=======================================================")
    print("CRUNCHING & CONSENSUS ANNOTATION COMPLETE!")
    print(f"Total Speeches: {len(corpus_entries)}")
    for g_id, g_data in groups_summary.items():
        print(f"Group {g_id}: {g_data['name']} ({g_data['speech_count']} speeches, {g_data['percentage_of_corpus']}%)")
    print(f"Full Consensus Profile saved to: {consensus_out}")
    print("=======================================================")

if __name__ == "__main__":
    main()
