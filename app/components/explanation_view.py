"""
Explanation View Component: Dual-Layer Groq Open-Source Reasoner
Provides modular renderers for:
1. Executive Coaching Verdict Banner
2. Technical Breakdown (Deterministic Acoustic Physics & DSP telemetry)
3. Qualitative Breakdown (Semantic Audience Perception & Vocal Drills)
"""

import streamlit as st

def render_executive_verdict_banner(explanation_data: dict):
    """
    Renders the prominent executive verdict banner across the breakdown suite.
    """
    exec_verdict = explanation_data.get("executive_verdict", "")
    source = explanation_data.get("source", "Groq Cloud (qwen/qwen3.8-27b)")

    st.markdown(
        f"<div style='background: #161B22; border: 1px solid #30363D; border-left: 5px solid #00E5FF; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;'>"
        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
        f"<span style='color: #00E5FF; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;'>Executive Coaching Verdict</span>"
        f"<span style='background: #21262D; color: #8B949E; font-size: 11px; padding: 2px 8px; border-radius: 4px;'>Powered by {source}</span>"
        f"</div>"
        f"<div style='color: #E6EDF3; font-size: 14px; line-height: 1.5;'>{exec_verdict}</div>"
        f"</div>",
        unsafe_allow_html=True
    )


def render_technical_breakdown(explanation_data: dict, metrics: dict = None, grade_report: dict = None):
    """
    Renders the Technical Breakdown (Deterministic Acoustic Rationale).
    """
    det_expl = explanation_data.get("deterministic_explanation", "")
    critiques = explanation_data.get("pillar_critiques", {})

    st.markdown("#### 🔬 Technical Breakdown (Deterministic Acoustic Rationale)")
    st.caption("Physics-grounded signal processing audit (semitones, seconds, decibels, and mathematical gate ceilings)")

    st.markdown(
        f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 16px; margin-bottom: 16px;'>"
        f"<div style='color: #C9D1D9; font-size: 13px; line-height: 1.6;'>{det_expl}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📐 Acoustic Physics Diagnostics")
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 14px; font-size: 12px; color: #8B949E; line-height: 1.8;'>"
            f"• <b style='color: #E6EDF3;'>Pitch Modulation:</b> {critiques.get('pitch_modulation', 'N/A')}<br>"
            f"• <b style='color: #E6EDF3;'>Rhetorical Pausing:</b> {critiques.get('rhetorical_pausing', 'N/A')}<br>"
            f"• <b style='color: #E6EDF3;'>Dynamic Energy:</b> {critiques.get('dynamic_energy', 'N/A')}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown("##### ⚖️ Mathematical Gating & Telemetry")
        if grade_report:
            gating = grade_report.get("gating_diagnostics", {})
            psi = gating.get("psi_impairment_index", 0.0)
            cap = gating.get("gate_cap", 10.0)
            gates = gating.get("triggered_gates", [])
            gate_text = ", ".join(gates) if gates else "None (Unconstrained)"

            st.markdown(
                f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 14px; font-size: 12px; color: #8B949E; line-height: 1.8;'>"
                f"• <b style='color: #E6EDF3;'>Compound Impairment Index (&Psi;):</b> <code>{psi:.2f}</code><br>"
                f"• <b style='color: #E6EDF3;'>Mathematical Gate Cap:</b> <code>{cap:.1f}/10.0</code><br>"
                f"• <b style='color: #E6EDF3;'>Triggered Penalty Gates:</b> <span style='color: {'#FF5252' if gates else '#00E676'};'>{gate_text}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        elif metrics:
            st.markdown(
                f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 14px; font-size: 12px; color: #8B949E; line-height: 1.8;'>"
                f"• <b style='color: #E6EDF3;'>Pitch Dynamic Range:</b> {metrics.get('f0_semitones', 0):.1f} semitones<br>"
                f"• <b style='color: #E6EDF3;'>Max Pause Duration:</b> {metrics.get('max_pause_duration_sec', 0):.2f}s<br>"
                f"• <b style='color: #E6EDF3;'>PAPR Crest Factor:</b> {metrics.get('papr_crest_factor', 0):.1f} dB"
                f"</div>",
                unsafe_allow_html=True
            )


def render_qualitative_breakdown(explanation_data: dict):
    """
    Renders the Qualitative Breakdown (Semantic Audience Perception & Vocal Drills).
    """
    sem_expl = explanation_data.get("semantic_explanation", "")
    critiques = explanation_data.get("pillar_critiques", {})
    drills = explanation_data.get("actionable_vocal_drills", [])

    st.markdown("#### 🎭 Qualitative Breakdown (Semantic Audience Perception)")
    st.caption("Human perceptual psychology, emotional resonance, and listener engagement impact")

    st.markdown(
        f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 16px; margin-bottom: 16px;'>"
        f"<div style='color: #C9D1D9; font-size: 13px; line-height: 1.6;'>{sem_expl}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("##### 👥 Audience Perception Dimensions")
    st.markdown(
        f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 14px; font-size: 12px; color: #8B949E; line-height: 1.8; margin-bottom: 20px;'>"
        f"• <b style='color: #E6EDF3;'>Cadence & Narrative Flow:</b> {critiques.get('cadence_and_tempo', 'N/A')}<br>"
        f"• <b style='color: #E6EDF3;'>Diction, Authority & Polish:</b> {critiques.get('spectral_clarity', 'N/A')}"
        f"</div>",
        unsafe_allow_html=True
    )

    # Actionable Vocal Drills
    if drills:
        st.markdown("##### 🏋️ Prescriptive Vocal Coaching Drills")
        drill_cols = st.columns(len(drills))
        for i, drill in enumerate(drills):
            target_col = drill_cols[i] if i < len(drill_cols) else st
            with target_col:
                st.markdown(
                    f"<div style='background: #161B22; border: 1px solid #30363D; border-top: 3px solid #00E676; border-radius: 8px; padding: 14px; height: 100%;'>"
                    f"<span style='color: #00E676; font-size: 11px; font-weight: 700; text-transform: uppercase;'>{drill.get('focus', 'Vocal Exercise')}</span><br>"
                    f"<b style='color: #E6EDF3; font-size: 14px;'>{drill.get('title', 'Targeted Drill')}</b>"
                    f"<p style='color: #8B949E; font-size: 12px; margin-top: 8px; line-height: 1.5;'>{drill.get('instructions', '')}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )


def render_dual_explanation_view(explanation_data: dict):
    """
    Backward-compatible side-by-side view.
    """
    render_executive_verdict_banner(explanation_data)
    col1, col2 = st.columns(2)
    with col1:
        render_technical_breakdown(explanation_data)
    with col2:
        render_qualitative_breakdown(explanation_data)
