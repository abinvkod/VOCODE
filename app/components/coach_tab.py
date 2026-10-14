"""
Coach Tab Component: Forensic Speech Remediation & Practice Routines
Analyzes speech flaws, pinpoints exactly what went wrong and how to fix it,
and generates structured daily vocal practice routines.
"""

import streamlit as st

def render_coach_tab(explanation: dict, grade_report: dict, moves: list[dict], metrics: dict, raw_audio_path: str):
    """
    Renders the dedicated Orator Coach tab with flaw fixes and practice routines.
    """
    total_grade = grade_report.get("total_grade", 7.0)
    grade_band = grade_report.get("grade_band", "Proficient")
    pillars = grade_report.get("pillar_scores", {})
    gating = grade_report.get("gating_diagnostics", {})
    deductions = grade_report.get("deductions", [])

    # Identify flaws, blunders, and mistakes
    blunders = [m for m in moves if m.get("move_type") == "BLUNDER"]
    mistakes = [m for m in moves if m.get("move_type") == "MISTAKE"]
    inaccuracies = [m for m in moves if m.get("move_type") == "INACCURACY"]
    all_imperfections = blunders + mistakes + inaccuracies

    # Determine core bottleneck pillar
    pillar_map = {
        "Pitch Modulation": pillars.get("pitch_modulation_out_of_2_5", 2.5) / 2.5,
        "Cadence & Tempo": pillars.get("cadence_and_tempo_out_of_2_5", 2.5) / 2.5,
        "Rhetorical Pausing": pillars.get("rhetorical_pausing_out_of_2_0", 2.0) / 2.0,
        "Dynamic Energy": pillars.get("dynamic_energy_out_of_1_5", 1.5) / 1.5,
        "Spectral Clarity": pillars.get("spectral_clarity_out_of_1_5", 1.5) / 1.5,
    }
    sorted_pillars = sorted(pillar_map.items(), key=lambda x: x[1])
    bottleneck_pillar, bottleneck_pct = sorted_pillars[0]

    # ---------------------------------------------------------
    # 1. COACH HEADER & EXECUTIVE VERDICT
    # ---------------------------------------------------------
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #161B22 0%, #1A2332 100%); border: 1px solid #30363D; border-left: 6px solid #00E5FF; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">🧑‍🏫</span>
                <div>
                    <h3 style="margin: 0; color: #FFFFFF; font-size: 20px; font-weight: 700;">Vocode Master Orator Coach</h3>
                    <span style="color: #8B949E; font-size: 13px;">Diagnostic Speech Remediation & Tailored Practice Plan</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: rgba(0, 229, 255, 0.15); color: #00E5FF; border: 1px solid #00E5FF; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                    Primary Remediation: {bottleneck_pillar} ({round(bottleneck_pct * 100)}% Proficiency)
                </span>
            </div>
        </div>
        <p style="color: #E6EDF3; font-size: 14px; line-height: 1.6; margin: 0;">
            {explanation.get("executive_verdict", "Analysis complete. Review targeted remedies and practice drills below.")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 2. WHAT WENT WRONG & HOW TO FIX IT (MISTAKE-BY-MISTAKE)
    # ---------------------------------------------------------
    st.markdown("### 🎯 What Went Wrong & How to Fix It")
    st.caption("Forensic breakdown of every detected oratorical flaw, its audience impact, and the exact physical fix.")

    if all_imperfections:
        for idx, imp in enumerate(all_imperfections[:5]):
            color = imp.get("color", "#FF1744")
            m_type = imp.get("move_type", "MISTAKE")
            t_start = imp.get("t_start", 0.0)
            t_end = imp.get("t_end", 0.0)
            phrase = imp.get("text", "")
            reason = imp.get("reason", "Acoustic disfluency detected.")

            # Dynamic remedial prescription based on flaw context
            if "freeze" in reason.lower() or "pause" in reason.lower() or "silence" in reason.lower():
                flaw_title = "Awkward Dead-Air Freeze"
                audience_damage = "Disrupts cognitive continuity. The audience perceives loss of composure or forgotten material."
                exact_fix = "Replace the frozen dead air with a deliberate 1.0-second silent eye-contact pause while maintaining physical posture. Inhale on the transition, then resume with renewed vocal projection."
            elif "monotone" in reason.lower() or "pitch" in reason.lower() or "flat" in reason.lower():
                flaw_title = "Pitch Compression & Monotone Delivery"
                audience_damage = "Induces acoustic fatigue. Without pitch modulation, listeners tune out within 15 seconds."
                exact_fix = "Identify the core thesis word in this sentence. Raise your pitch by 4 to 6 semitones on that single word while dropping pitch on the trailing syllables to signal certainty."
            elif "rush" in reason.lower() or "wpm" in reason.lower() or "tempo" in reason.lower():
                flaw_title = "Anxiety-Driven Speed Rush"
                audience_damage = "Words blur together, diminishing retention and signaling nervous rushing."
                exact_fix = "Anchor your tempo to 140 WPM. Elongate your stressed vowel durations and allow 0.5s breathing windows between clauses."
            elif "repeat" in reason.lower() or "stutter" in reason.lower() or "repetition" in reason.lower():
                flaw_title = "Lexical Word Repetition & Hesitation Loop"
                audience_damage = "Direct word repetitions and stutter loops undermine perceived confidence, making delivery feel tentative and breaking listener immersion."
                exact_fix = "Apply the 'Silent Swallow & Reset' technique: when you sense a word repeating or stumbling, immediately stop voice production for 1 second instead of rewinding. Inhale silently and advance cleanly to the next word."
            else:
                flaw_title = f"{m_type.title()} in Delivery Cadence"
                audience_damage = "Diminishes persuasion and detracts from message authority."
                exact_fix = "Re-articulate this phrase with deliberate diaphragmatic support, emphasizing clear consonant attacks on every stressed syllable."

            c_flaw, c_btn = st.columns([0.84, 0.16])
            with c_flaw:
                st.markdown(f"""
                <div style="background: #161B22; border-left: 5px solid {color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; border: 1px solid #30363D; border-left-color: {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="color: {color}; font-weight: 700; font-size: 14px;">{imp.get('icon', '⚠️')} {flaw_title} [{t_start}s - {t_end}s]</span>
                        <span style="background: #21262D; color: #8B949E; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{m_type}</span>
                    </div>
                    <div style="color: #E6EDF3; font-size: 13px; font-style: italic; margin-bottom: 8px;">"{phrase}"</div>
                    <div style="font-size: 13px; margin-bottom: 6px;">
                        <b style="color: #FF7B72;">Why It Hurt Your Speech:</b> <span style="color: #C9D1D9;">{audience_damage}</span>
                    </div>
                    <div style="font-size: 13px;">
                        <b style="color: #00E676;">The Exact Fix:</b> <span style="color: #E6EDF3;">{exact_fix}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                st.write("")
                st.write("")
                if st.button(f"▶ Replay [{t_start}s]", key=f"coach_replay_{idx}", help=f"Jump to {t_start}s in raw audio"):
                    st.session_state["seek_timestamp"] = t_start
                    st.rerun()

    else:
        st.success("🌟 **Exceptional Delivery!** No critical blunders or disfluency freezes detected in this recording.")
        st.markdown("""
        <div style="background: #161B22; border: 1px solid #30363D; border-left: 5px solid #00E676; padding: 16px; border-radius: 8px;">
            <b style="color: #00E676; font-size: 14px;">Masterclass Polish Points to Reach Legendary Status:</b>
            <ul style="color: #C9D1D9; font-size: 13px; margin-top: 8px; line-height: 1.6;">
                <li><b>Micro-Pause Framing:</b> Insert intentional 1.2s pregnant pauses immediately before your climactic punchline to build anticipation.</li>
                <li><b>Harmonic Timbre Shifts:</b> Alternate between intimate conversational chest voice and commanding auditorium projection.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. PERSONALIZED PRACTICE ROUTINES & VOCAL DRILLS
    # ---------------------------------------------------------
    st.markdown("### 🏋️ Tailored Daily Practice Routines")
    st.caption("Actionable, timed drills calibrated to eliminate your specific speech vulnerabilities.")

    col_r1, col_r2 = st.columns(2)

    # Drill 1: Pause & Fluency Anchor
    with col_r1:
        st.markdown("""
        <div style="background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 18px; margin-bottom: 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <b style="color: #00E5FF; font-size: 15px;">Routine 1: The Diaphragmatic Breath Anchor</b>
                <span style="background: #21262D; color: #8B949E; font-size: 11px; padding: 3px 8px; border-radius: 12px;">5 Mins / Day</span>
            </div>
            <div style="color: #8B949E; font-size: 12px; margin-bottom: 12px;">
                <b>Targeted Flaw:</b> Eliminates abrupt freezing, filler words ("um/ah"), and breathlessness.
            </div>
            <div style="background: #0D1117; padding: 12px; border-radius: 6px; font-size: 13px; color: #E6EDF3; line-height: 1.6;">
                <b>Step 1:</b> Inhale deeply into your abdomen for 4 slow counts without raising your shoulders.<br>
                <b>Step 2:</b> Speak a 15-word sentence on a single supported exhalation without stopping.<br>
                <b>Step 3:</b> When transitioning thoughts, pause silently for exactly 2 seconds of deliberate eye contact instead of vocalizing hesitation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Drill 2: Pitch Inflection Staircase
    with col_r2:
        st.markdown("""
        <div style="background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 18px; margin-bottom: 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <b style="color: #00E676; font-size: 15px;">Routine 2: 3-Tier Pitch Inflection Staircase</b>
                <span style="background: #21262D; color: #8B949E; font-size: 11px; padding: 3px 8px; border-radius: 12px;">7 Mins / Day</span>
            </div>
            <div style="color: #8B949E; font-size: 12px; margin-bottom: 12px;">
                <b>Targeted Flaw:</b> Cures monotone delivery and expands pitch dynamism (>16 semitones).
            </div>
            <div style="background: #0D1117; padding: 12px; border-radius: 6px; font-size: 13px; color: #E6EDF3; line-height: 1.6;">
                <b>Step 1 (Root):</b> Read the sentence subject in deep, resonant chest voice.<br>
                <b>Step 2 (Bridge):</b> Raise pitch by 3 semitones on descriptive verbs to create forward momentum.<br>
                <b>Step 3 (Peak):</b> Spike pitch by 6-8 semitones on the climactic key noun, then drop back down on the period to deliver authoritative closure.
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_r3, col_r4 = st.columns(2)

    # Drill 3: Metronome Cadence Ladder
    with col_r3:
        st.markdown("""
        <div style="background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 18px; margin-bottom: 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <b style="color: #FFB74D; font-size: 15px;">Routine 3: Metronome Cadence Lock (140 WPM)</b>
                <span style="background: #21262D; color: #8B949E; font-size: 11px; padding: 3px 8px; border-radius: 12px;">5 Mins / Day</span>
            </div>
            <div style="color: #8B949E; font-size: 12px; margin-bottom: 12px;">
                <b>Targeted Flaw:</b> Prevents nervous rushing (>180 WPM) and sluggish drags (<110 WPM).
            </div>
            <div style="background: #0D1117; padding: 12px; border-radius: 6px; font-size: 13px; color: #E6EDF3; line-height: 1.6;">
                <b>Step 1:</b> Turn on a 140 BPM metronome clicker.<br>
                <b>Step 2:</b> Read a 50-word passage aligning one stressed syllable to each beat.<br>
                <b>Step 3:</b> When you reach a key emotional sentence, deliberately cut tempo in half (70 BPM) to double the gravitas.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Drill 4: PAPR Dynamic Power Burst
    with col_r4:
        st.markdown("""
        <div style="background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 18px; margin-bottom: 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <b style="color: #BA68C8; font-size: 15px;">Routine 4: Consonant Punch & Projection Burst</b>
                <span style="background: #21262D; color: #8B949E; font-size: 11px; padding: 3px 8px; border-radius: 12px;">3 Mins / Day</span>
            </div>
            <div style="color: #8B949E; font-size: 12px; margin-bottom: 12px;">
                <b>Targeted Flaw:</b> Eliminates vocal mumbling and raises PAPR crest factor (>25 dB).
            </div>
            <div style="background: #0D1117; padding: 12px; border-radius: 6px; font-size: 13px; color: #E6EDF3; line-height: 1.6;">
                <b>Step 1:</b> Pick sentences with plosive consonants: <i>P, T, K, B, D, G</i>.<br>
                <b>Step 2:</b> Push crisp air pulses from the abdomen on each plosive start.<br>
                <b>Step 3:</b> Focus acoustic projection forward toward the back wall of the room.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. 7-DAY REHABILITATION ROADMAP
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📅 7-Day Speech Remediation Schedule")
    st.markdown("""
    | Day | Focus Area | Prescribed Drill | Time Commitment |
    | :--- | :--- | :--- | :--- |
    | **Day 1** | **Fluency Foundation** | Routine 1: Diaphragmatic Breath Anchor | 5 Mins |
    | **Day 2** | **Pitch Expansion** | Routine 2: 3-Tier Pitch Inflection Staircase | 7 Mins |
    | **Day 3** | **Cadence Locking** | Routine 3: Metronome Cadence Lock at 140 WPM | 5 Mins |
    | **Day 4** | **Power Projection** | Routine 4: Consonant Punch & PAPR Burst | 3 Mins |
    | **Day 5** | **Integrated Run-Through** | Combine Routines 1 + 2 on Full Speech | 10 Mins |
    | **Day 6** | **Speed Modulation** | Combine Routines 3 + 4 with Varied Cadence | 10 Mins |
    | **Day 7** | **Final Re-Evaluation** | Re-record audio & submit to Vocode Engine | 5 Mins |
    """)

    # AI Model Specific Drills from Explanation
    ai_drills = explanation.get("actionable_vocal_drills", [])
    if ai_drills:
        st.markdown("---")
        st.markdown("### 🤖 Groq LLM Tailored Recommendations")
        for drill in ai_drills:
            st.markdown(f"""
            <div style="background: #161B22; border: 1px solid #30363D; border-left: 4px solid #00E5FF; padding: 12px 16px; border-radius: 6px; margin-bottom: 8px;">
                <b style="color: #00E5FF;">{drill.get('title', 'Vocal Drill')}</b> — <span style="color: #8B949E; font-size: 12px;">{drill.get('focus', 'General')}</span><br>
                <span style="color: #E6EDF3; font-size: 13px;">{drill.get('instructions', '')}</span>
            </div>
            """, unsafe_allow_html=True)
