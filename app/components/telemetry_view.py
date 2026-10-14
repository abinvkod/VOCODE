"""
Telemetry View Component: Deep 100 Hz Multi-Track Acoustic Contours
Visualizes pitch F0 contour (Hz), RMS energy envelope (dB FS), and dynamic rhythm metrics.
"""

import plotly.graph_objects as go
import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import parselmouth

def render_telemetry_view(clean_wav_path: str, metrics: dict):
    """
    Renders synchronized time-series plots of Pitch F0 and RMS Energy.
    """
    y, sr = sf.read(clean_wav_path, dtype='float32')
    duration = float(len(y) / sr)

    snd = parselmouth.Sound(clean_wav_path)
    pitch = snd.to_pitch(time_step=0.02, pitch_floor=75.0, pitch_ceiling=500.0)
    pitch_values = pitch.selected_array['frequency']
    pitch_times = pitch.xs()

    hop_len = int(0.02 * sr)
    frame_len = hop_len * 2
    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    rms_db = 20.0 * np.log10(np.maximum(rms, 1e-5))
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_len)

    # Plot 1: Pitch F0 Contour
    fig_f0 = go.Figure()
    voiced_mask = pitch_values > 0
    clean_f0_times = pitch_times[voiced_mask]
    clean_f0_vals = pitch_values[voiced_mask]

    fig_f0.add_trace(go.Scatter(
        x=clean_f0_times,
        y=clean_f0_vals,
        mode='lines',
        line=dict(color='#00E5FF', width=2),
        name='F0 Pitch (Hz)'
    ))
    fig_f0.update_layout(
        title=dict(text="<b>Fundamental Frequency Contour F0(t)</b>", font=dict(size=14, color="#E6EDF3")),
        paper_bgcolor="#161B22",
        plot_bgcolor="#0D1117",
        height=220,
        margin=dict(l=40, r=20, t=35, b=25),
        xaxis=dict(title=dict(text="Time (s)", font=dict(color="#8B949E", size=12)), gridcolor="#21262D", range=[0, duration], tickfont=dict(color="#8B949E")),
        yaxis=dict(title=dict(text="Hz", font=dict(color="#8B949E", size=12)), gridcolor="#21262D", tickfont=dict(color="#8B949E"))
    )
    st.plotly_chart(fig_f0, use_container_width=True)

    # Plot 2: RMS Energy Envelope
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Scatter(
        x=rms_times,
        y=rms_db,
        mode='lines',
        line=dict(color='#00E676', width=2),
        name='RMS Energy (dB FS)'
    ))
    fig_energy.update_layout(
        title=dict(text="<b>Dynamic Energy Envelope RMS(t)</b>", font=dict(size=14, color="#E6EDF3")),
        paper_bgcolor="#161B22",
        plot_bgcolor="#0D1117",
        height=220,
        margin=dict(l=40, r=20, t=35, b=25),
        xaxis=dict(title=dict(text="Time (s)", font=dict(color="#8B949E", size=12)), gridcolor="#21262D", range=[0, duration], tickfont=dict(color="#8B949E")),
        yaxis=dict(title=dict(text="dB FS", font=dict(color="#8B949E", size=12)), gridcolor="#21262D", tickfont=dict(color="#8B949E"))
    )
    st.plotly_chart(fig_energy, use_container_width=True)

    # Summary Metrics Table
    st.markdown("##### 🔬 Summary Acoustic Features")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 11px;'>Pitch Range</span><br>"
            f"<b style='color: #00E5FF; font-size: 16px;'>{metrics.get('f0_semitones', 0):.1f} st</b>"
            f"</div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 11px;'>Max Pause</span><br>"
            f"<b style='color: #FFD600; font-size: 16px;'>{metrics.get('max_pause_duration_sec', 0):.2f}s</b>"
            f"</div>",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 11px;'>PAPR Crest</span><br>"
            f"<b style='color: #00E676; font-size: 16px;'>{metrics.get('papr_crest_factor', 0):.1f} dB</b>"
            f"</div>",
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"<div style='background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 10px; text-align: center;'>"
            f"<span style='color: #8B949E; font-size: 11px;'>Pause Ratio</span><br>"
            f"<b style='color: #E040FB; font-size: 16px;'>{metrics.get('pause_ratio', 0) * 100:.1f}%</b>"
            f"</div>",
            unsafe_allow_html=True
        )
