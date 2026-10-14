"""
Score Dial Component: Plotly Speedometer Gauge & Tier Visualizer
Renders an interactive speedometer gauge displaying overall oratorical score on a 10.0-point scale.
"""

import plotly.graph_objects as go
import streamlit as st

def render_score_dial(total_grade: float, grade_band: str, gate_ceiling: float, psi_index: float):
    """
    Renders an interactive Plotly Gauge Indicator dial with color gradients.
    """
    # Color logic
    if total_grade >= 8.5:
        dial_color = "#00E676"  # Emerald
    elif total_grade >= 6.5:
        dial_color = "#FFD600"  # Gold
    elif total_grade >= 5.0:
        dial_color = "#FF9100"  # Amber
    else:
        dial_color = "#FF1744"  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_grade,
        domain={'x': [0, 1], 'y': [0, 1]},
        delta={'reference': 8.5, 'increasing': {'color': "#00E676"}, 'decreasing': {'color': "#FF1744"}},
        title={'text': f"<b>{grade_band}</b>", 'font': {'size': 20, 'color': "#FFFFFF"}},
        number={'suffix': " / 10.0", 'font': {'size': 38, 'color': dial_color}},
        gauge={
            'axis': {'range': [0, 10.0], 'tickwidth': 2, 'tickcolor': "#8B949E", 'tickfont': {'color': "#8B949E"}},
            'bar': {'color': dial_color, 'thickness': 0.3},
            'bgcolor': "#161B22",
            'borderwidth': 1,
            'bordercolor': "#30363D",
            'steps': [
                {'range': [0, 5.0], 'color': "rgba(255, 23, 68, 0.20)"},
                {'range': [5.0, 6.5], 'color': "rgba(255, 145, 0, 0.20)"},
                {'range': [6.5, 8.0], 'color': "rgba(255, 214, 0, 0.20)"},
                {'range': [8.0, 10.0], 'color': "rgba(0, 230, 118, 0.20)"}
            ],
            'threshold': {
                'line': {'color': "#FF5252", 'width': 4},
                'thickness': 0.8,
                'value': gate_ceiling
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#E6EDF3", 'family': "sans-serif"},
        height=280,
        margin=dict(l=25, r=25, t=40, b=15)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Diagnostic Subtitle Pill
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 12px;'>Gate Ceiling</span><br>"
            f"<b style='color: #E6EDF3; font-size: 16px;'>{gate_ceiling:.2f} / 10.0</b>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 12px;'>Systemic Impairment (Ψ)</span><br>"
            f"<b style='color: {'#FF1744' if psi_index >= 1.0 else '#00E676'}; font-size: 16px;'>{psi_index:.2f}</b>"
            f"</div>",
            unsafe_allow_html=True
        )
