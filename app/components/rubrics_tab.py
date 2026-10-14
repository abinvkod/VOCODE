"""
Rubrics Tab Component: 5 Oratorical Pillars & Deduction Audit Trail
Displays itemized progress bars, 5-Pillar Radar Chart, and the complete mathematical deduction ledger.
"""

import plotly.graph_objects as go
import streamlit as st

PILLAR_METADATA = [
    {
        "key": "pitch_modulation_out_of_2_5",
        "name": "Pitch Modulation",
        "max": 2.5,
        "color": "#00E5FF",
        "desc": "Measures micro-prosodic semitone span, melodic contouring, and pitch velocity."
    },
    {
        "key": "cadence_and_tempo_out_of_2_5",
        "name": "Cadence & Tempo",
        "max": 2.5,
        "color": "#00E676",
        "desc": "Measures syllabic articulation rate (SPS), WPM stability, and rhythmic acceleration."
    },
    {
        "key": "rhetorical_pausing_out_of_2_0",
        "name": "Rhetorical Pausing",
        "max": 2.0,
        "color": "#FFD600",
        "desc": "Evaluates strategic dead-air ratio, rhetorical breath pauses, and unforced hesitation."
    },
    {
        "key": "dynamic_energy_out_of_1_5",
        "name": "Dynamic Energy",
        "max": 1.5,
        "color": "#FF9100",
        "desc": "Quantifies Peak-to-Average Power Ratio (PAPR) crest factor and projection vigor."
    },
    {
        "key": "spectral_clarity_out_of_1_5",
        "name": "Spectral Clarity",
        "max": 1.5,
        "color": "#E040FB",
        "desc": "Tracks spectral flux, formantic resonance balance, and absence of slurring."
    }
]

def render_rubrics_tab(grade_report: dict, metrics: dict):
    """
    Renders the complete 5-pillar rubric breakdown, radar chart, and itemized deduction ledger.
    """
    pillar_scores = grade_report.get("pillar_scores", {})
    deductions = grade_report.get("deductions", [])

    st.markdown("### 📊 Rubric Scorecard (10.0 Scale)")

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown("#### Pillar Scorecards")
        for p in PILLAR_METADATA:
            val = float(pillar_scores.get(p["key"], p["max"]))
            pct = min(1.0, max(0.0, val / p["max"]))
            st.markdown(
                f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;'>"
                f"<div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>"
                f"<span style='color: #E6EDF3; font-weight: 600; font-size: 13px;'>{p['name']}</span>"
                f"<span style='color: {p['color']}; font-weight: 700; font-size: 13px;'>{val:.2f} / {p['max']:.1f}</span>"
                f"</div>"
                f"<div style='background: #21262D; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 6px;'>"
                f"<div style='background: {p['color']}; height: 100%; width: {pct * 100}%; border-radius: 4px;'></div>"
                f"</div>"
                f"<span style='color: #8B949E; font-size: 11px;'>{p['desc']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("#### 5-Pillar Oratorical Radar")
        categories = ["Pitch", "Cadence", "Pauses", "Energy", "Clarity"]
        scores_pct = [
            (float(pillar_scores.get("pitch_modulation_out_of_2_5", 2.5)) / 2.5) * 100,
            (float(pillar_scores.get("cadence_and_tempo_out_of_2_5", 2.5)) / 2.5) * 100,
            (float(pillar_scores.get("rhetorical_pausing_out_of_2_0", 2.0)) / 2.0) * 100,
            (float(pillar_scores.get("dynamic_energy_out_of_1_5", 1.5)) / 1.5) * 100,
            (float(pillar_scores.get("spectral_clarity_out_of_1_5", 1.5)) / 1.5) * 100
        ]
        baseline_pct = [92, 94, 90, 88, 91] # Masterclass baseline

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=baseline_pct + [baseline_pct[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0, 230, 118, 0.12)',
            line=dict(color='#00E676', width=1.5, dash='dash'),
            name='Masterclass Benchmark'
        ))
        fig.add_trace(go.Scatterpolar(
            r=scores_pct + [scores_pct[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0, 229, 255, 0.35)',
            line=dict(color='#00E5FF', width=2.5),
            name='Current Speaker'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8B949E", size=10), gridcolor="#30363D"),
                angularaxis=dict(tickfont=dict(color="#E6EDF3", size=12), gridcolor="#30363D"),
                bgcolor="#0D1117"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#E6EDF3"), orientation="h", y=-0.15),
            height=340,
            margin=dict(l=30, r=30, t=20, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Itemized Deduction Audit Ledger
    st.markdown("---")
    st.markdown(f"#### 🔍 Mathematical Deduction Ledger ({len(deductions)} items detected)")

    if not deductions:
        st.success("✨ Flawless performance: No mathematical acoustic penalties were assessed.")
    else:
        for idx, d in enumerate(deductions, 1):
            pen = float(d.get("deduction", 0.0))
            pillar = d.get("pillar", "General")
            flaw = d.get("flaw", "Acoustic Anomaly")
            expl = d.get("explanation", "")
            interval = d.get("temporal_interval")

            interval_str = f" • [{interval[0]:.2f}s - {interval[1]:.2f}s]" if interval else ""

            st.markdown(
                f"<div style='background: #161B22; border-left: 4px solid #FF1744; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;'>"
                f"<div style='display: flex; justify-content: space-between; align-items: center;'>"
                f"<b style='color: #FF5252; font-size: 13px;'>{idx}. {flaw}{interval_str}</b>"
                f"<span style='background: #361717; color: #FF5252; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>-{pen:.2f} pts</span>"
                f"</div>"
                f"<div style='color: #8B949E; font-size: 12px; margin-top: 4px;'><b>Pillar:</b> {pillar} | {expl}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
