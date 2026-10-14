"""
Move Waveform Component: Breakdown Timeline & Waveform Inspector
Visualizes audio waveform with colored rhetorical move regions and interactive inspection cards.
"""

import plotly.graph_objects as go
import streamlit as st
import numpy as np
import soundfile as sf

from src.preprocessing.audio_standardizer import load_audio, downmix_to_mono

def render_move_waveform_inspector(clean_wav_path: str, moves: list[dict]):
    """
    Renders an interactive Plotly timeline with waveform overlay and move indicator cards.
    """
    try:
        y, sr = sf.read(clean_wav_path, dtype='float32')
        if y.ndim > 1:
            y = np.mean(y, axis=1)
    except Exception:
        y, sr = load_audio(clean_wav_path)
        y = downmix_to_mono(y)

    duration = float(len(y) / sr)

    n_points = 1200
    step = max(1, len(y) // n_points)
    downsampled_y = y[::step]
    time_axis = np.linspace(0, duration, len(downsampled_y))

    fig = go.Figure()

    # 1. Base Waveform Line
    fig.add_trace(go.Scatter(
        x=time_axis,
        y=downsampled_y,
        mode='lines',
        line=dict(color='#8B949E', width=1.0),
        name='Acoustic Waveform',
        hoverinfo='skip'
    ))

    # 2. Add Colored Shading Bands for each Rhetorical Move
    for m in moves:
        fig.add_vrect(
            x0=m["t_start"],
            x1=m["t_end"],
            fillcolor=m["color"],
            opacity=0.28,
            line_width=1.5,
            line_color=m["color"],
            annotation_text=f"{m['icon']} {m['move_type']}",
            annotation_position="top left",
            annotation_font=dict(size=10, color=m["color"]),
            layer="below"
        )

    fig.update_layout(
        title=dict(text="<b>Speech Breakdown Waveform Timeline</b>", font=dict(size=16, color="#E6EDF3")),
        paper_bgcolor="#161B22",
        plot_bgcolor="#0D1117",
        height=260,
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis=dict(
            title=dict(text="Time (seconds)", font=dict(color="#8B949E", size=12)),
            tickfont=dict(color="#8B949E"),
            showgrid=True,
            gridcolor="#21262D",
            range=[0, duration]
        ),
        yaxis=dict(
            title=dict(text="Amplitude", font=dict(color="#8B949E", size=12)),
            tickfont=dict(color="#8B949E"),
            showgrid=True,
            gridcolor="#21262D",
            range=[-1.05, 1.05]
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3. Move Legend & Summary Pills
    move_counts = {}
    for m in moves:
        move_counts[m["move_type"]] = move_counts.get(m["move_type"], 0) + 1

    pill_cols = st.columns(5)
    labels = [
        ("✨ Brilliant", "BRILLIANT", "#00E5FF", pill_cols[0]),
        ("🎯 Great/Good", "GREAT", "#00E676", pill_cols[1]),
        ("⚠️ Inaccuracy", "INACCURACY", "#FFEA00", pill_cols[2]),
        ("⚡ Mistake", "MISTAKE", "#FF9100", pill_cols[3]),
        ("❌ Blunder", "BLUNDER", "#FF1744", pill_cols[4])
    ]

    for label, m_key, col_code, pcol in labels:
        cnt = move_counts.get(m_key, 0)
        if m_key == "GREAT":
            cnt += move_counts.get("GOOD", 0)
        with pcol:
            st.markdown(
                f"<div style='border-left: 4px solid {col_code}; background: #21262D; padding: 6px 10px; border-radius: 6px; text-align: center;'>"
                f"<span style='color: #8B949E; font-size: 11px;'>{label}</span><br>"
                f"<b style='color: {col_code}; font-size: 16px;'>{cnt}</b>"
                f"</div>",
                unsafe_allow_html=True
            )
