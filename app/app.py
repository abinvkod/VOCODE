"""
Vocode: Contrastive Speech Analytics & Temporal Flaw Grounding
Main Web Dashboard — Tape Recorder Reel Landing & Rubric Analytics Dashboard
"""

import os
import sys
import tempfile
import streamlit as st

# Add workspace root and app directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
for p in [ROOT_DIR, CURRENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Load .env file if present
env_file = os.path.join(ROOT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

try:
    from services.ingestion_service import normalize_uploaded_audio
    from services.alignment_service import resolve_and_align_transcript
    from services.evaluation_service import evaluate_audio
    from services.move_classifier import classify_speech_moves
    from services.explanation_service import generate_speech_explanation

    from components.audio_player import render_interactive_audio_player
    from components.score_dial import render_score_dial
    from components.move_waveform import render_move_waveform_inspector
    from components.rubrics_tab import render_rubrics_tab, PILLAR_METADATA
    from components.explanation_view import (
        render_dual_explanation_view,
        render_executive_verdict_banner,
        render_technical_breakdown,
        render_qualitative_breakdown
    )
    from components.telemetry_view import render_telemetry_view
    from components.coach_tab import render_coach_tab
except ImportError:
    from app.services.ingestion_service import normalize_uploaded_audio
    from app.services.alignment_service import resolve_and_align_transcript
    from app.services.evaluation_service import evaluate_audio
    from app.services.move_classifier import classify_speech_moves
    from app.services.explanation_service import generate_speech_explanation

    from app.components.audio_player import render_interactive_audio_player
    from app.components.score_dial import render_score_dial
    from app.components.move_waveform import render_move_waveform_inspector
    from app.components.rubrics_tab import render_rubrics_tab, PILLAR_METADATA
    from app.components.explanation_view import (
        render_dual_explanation_view,
        render_executive_verdict_banner,
        render_technical_breakdown,
        render_qualitative_breakdown
    )
    from app.components.telemetry_view import render_telemetry_view
    from app.components.coach_tab import render_coach_tab


# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VOCODE",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_default_benchmark_data():
    candidates = [
        os.path.join(ROOT_DIR, "dataset", "testing videos", "01_Admiral_William_McRaven"),
        os.path.join(ROOT_DIR, "testing videos", "01_Admiral_William_McRaven"),
    ]
    sample_dir = next((c for c in candidates if os.path.exists(c)), candidates[0])
    inf_path = os.path.join(sample_dir, "inference_report.json")
    clean_wav = os.path.join(sample_dir, "preprocessed_clean.wav")
    raw_wav = os.path.join(sample_dir, "raw_audio.wav")
    txt_path = os.path.join(sample_dir, "canonical_transcript.txt")
    if os.path.exists(inf_path):
        import json
        with open(inf_path, "r") as f:
            inf = json.load(f)
        trans = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r") as f:
                trans = f.read()
        grade_report = {
            "total_grade": inf["grades"]["strict_leniency_0"],
            "grade_band": inf["performance_band_strict"],
            "pillar_scores": inf["pillar_breakdown_strict"],
            "deductions": inf.get("deductions_strict", []),
            "gating_diagnostics": {"gate_cap": 10.0, "psi_impairment_index": 0.0}
        }
        explanation = {
            "executive_verdict": "Masterclass oratorical delivery with commanding dynamic energy and near-flawless articulation pacing.",
            "pillar_critiques": {
                "pitch_modulation": "Pitch modulation is well-controlled at 11.38 semitones, showing mild restraint suitable for formal commencement cadence.",
                "cadence_and_tempo": "Cadence is exceptionally steady at 5.83 syllables per second with smooth rhythmic prosody.",
                "rhetorical_pausing": "Rhetorical pause ratio of 21.1% demonstrates masterclass breath control and deliberate emphasis punctuation.",
                "dynamic_energy": "Dynamic energy range of 51.35 dB delivers commanding vocal presence without clipping.",
                "spectral_clarity": "Formant definition and harmonic clarity are pristine across the 1-4 kHz speech band."
            }
        }
        moves = [
            {
                "index": 1,
                "t_start": 3.0,
                "t_end": 12.0,
                "duration": 9.0,
                "text": "Thank you very much. Well, thank you.",
                "move_type": "BRILLIANT",
                "label": "Brilliant Move",
                "icon": "✨",
                "color": "#00E5FF",
                "bg_color": "rgba(0, 229, 255, 0.25)",
                "reason": "Masterclass rhetorical delivery: Dynamic pitch peak combined with emphatic vocal punchiness.",
                "metrics": {"wpm": 145.0, "f0_semitones": 14.5, "papr": 32.0}
            },
            {
                "index": 2,
                "t_start": 12.0,
                "t_end": 20.0,
                "duration": 8.0,
                "text": "President Powers, Provost Fendes, Deans...",
                "move_type": "GREAT",
                "label": "Great Move",
                "icon": "🎯",
                "color": "#00E676",
                "bg_color": "rgba(0, 230, 118, 0.20)",
                "reason": "Fluid cadence, resonant pitch inflection, and well-balanced rhetorical phrasing.",
                "metrics": {"wpm": 152.0, "f0_semitones": 12.2, "papr": 24.0}
            },
            {
                "index": 3,
                "t_start": 20.0,
                "t_end": 35.0,
                "duration": 15.0,
                "text": "It is indeed an honor for me to be here tonight.",
                "move_type": "GOOD",
                "label": "Good Move",
                "icon": "👍",
                "color": "#76FF03",
                "bg_color": "rgba(118, 255, 3, 0.15)",
                "reason": "Standard, clear delivery meeting baseline oratorical expectations.",
                "metrics": {"wpm": 148.0, "f0_semitones": 10.5, "papr": 20.0}
            }
        ]
        preview_audio = os.path.join(sample_dir, "preview_audio.mp3")
        audio_to_use = preview_audio if os.path.exists(preview_audio) else clean_wav
        return {
            "clean_wav": audio_to_use,
            "raw_audio_path": audio_to_use,
            "filename": "Admiral_William_McRaven_Commencement.mp3",
            "metrics": inf.get("metrics", {}),
            "grade_report": grade_report,
            "moves": moves,
            "explanation": explanation,
            "canonical_transcript": trans
        }
    return None

# ─── Session State & Route Normalization ──────────────────────────────────────
query_page = st.query_params.get("page", None)
if query_page == "results":
    if st.session_state.get("processed_data") is None:
        st.session_state["processed_data"] = load_default_benchmark_data()
    st.session_state["current_page"] = "results"
else:
    st.session_state["current_page"] = "upload"
    if query_page != "upload":
        st.query_params["page"] = "upload"

st.session_state.setdefault("processed_data", None)
st.session_state.setdefault("seek_timestamp", None)
st.session_state.setdefault("show_transcript_input", False)
st.session_state.setdefault("transcript_text", "")

# Per-pillar explanation panel open/closed state
for _p in ["pitch_modulation", "cadence_and_tempo", "rhetorical_pausing", "dynamic_energy", "spectral_clarity"]:
    st.session_state.setdefault(f"expl_open_{_p}", False)

# ─── Global Font & Streamlit Header Reset ────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800;900&display=swap');
  html, body, [class*="css"], .stApp {
      font-family: 'Space Grotesk', -apple-system, sans-serif !important;
  }
  header[data-testid="stHeader"] { display: none !important; }
  footer { display: none !important; }
  [data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# =============================================================
# PAGE 1: UPLOAD & LANDING PAGE (Atmospheric Tape Reel Ambience)
# =============================================================
if st.session_state["current_page"] == "upload":

    st.markdown("""
    <style>
      /* ── TRANSPARENT STREAMLIT CONTAINERS (Allow fixed background canvas to shine through) ── */
      html, body {
          background-color: #060709 !important;
          margin: 0 !important;
          padding: 0 !important;
          overflow-x: hidden !important;
      }
      #root, .stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"],
      [data-testid="stMainBlockContainer"],
      .block-container {
          background: transparent !important;
          background-color: transparent !important;
      }

      /* ── HIDE IFRAME COMPONENT IN FLOW (The script attaches fixed canvas to body) ── */
      div[data-testid="stElementContainer"]:has(iframe[data-testid="stIFrame"]),
      div[data-testid="stElementContainer"]:has(iframe) {
          position: absolute !important;
          top: 0 !important;
          left: 0 !important;
          width: 0 !important;
          height: 0 !important;
          overflow: hidden !important;
          margin: 0 !important;
          padding: 0 !important;
          pointer-events: none !important;
          opacity: 0 !important;
      }

      /* ── CENTERED PAGE CONTAINER (Exact middle-center of viewport) ── */
      [data-testid="stMain"] {
          display: flex !important;
          flex-direction: column !important;
          justify-content: center !important;
          align-items: center !important;
          min-height: 100vh !important;
          padding: 0 !important;
          position: relative !important;
          z-index: 5 !important;
      }
      [data-testid="stMainBlockContainer"],
      .block-container {
          width: 100% !important;
          max-width: 620px !important;
          margin: auto !important;
          padding: 24px 20px 30px 20px !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: center !important;
          position: relative !important;
          z-index: 10 !important;
          gap: 0 !important;
      }
      div[data-testid="stElementContainer"] {
          width: 100% !important;
          display: flex !important;
          justify-content: center !important;
      }

      /* ── VOCODE TITLE IN TOP CENTER (Atmospheric Glitch) ── */
      .vocode-header-block {
          text-align: center !important;
          margin-bottom: 24px !important;
          width: 100% !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          pointer-events: none !important;
      }
      .vocode-glitch-title {
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: clamp(48px, 6vw, 76px) !important;
          font-weight: 900 !important;
          letter-spacing: 16px !important;
          color: #FFFFFF !important;
          text-transform: uppercase !important;
          position: relative !important;
          line-height: 1.0 !important;
          margin: 0 !important;
          text-shadow: 0 0 35px rgba(0, 229, 255, 0.45);
      }
      .vocode-glitch-title::before,
      .vocode-glitch-title::after {
          content: attr(data-text) !important;
          position: absolute !important;
          top: 0 !important;
          left: 0 !important;
          width: 100% !important;
          height: 100% !important;
      }
      .vocode-glitch-title::after {
          color: #00E5FF !important;
          z-index: -2 !important;
          clip-path: inset(45% 0 40% 0) !important;
          animation: v-glitch-1 3.2s infinite linear alternate-reverse !important;
      }
      .vocode-glitch-title::before {
          color: #FF1744 !important;
          z-index: -1 !important;
          clip-path: inset(60% 0 25% 0) !important;
          animation: v-glitch-2 2.7s infinite linear alternate-reverse !important;
      }
      @keyframes v-glitch-1 {
          0% { clip-path: inset(20% 0 60% 0); transform: translate(-3px, 1px); }
          25% { clip-path: inset(55% 0 15% 0); transform: translate(3px, -1px); }
          50% { clip-path: inset(40% 0 40% 0); transform: translate(-2px, 2px); }
          75% { clip-path: inset(80% 0 5% 0); transform: translate(2px, -2px); }
          100% { clip-path: inset(10% 0 75% 0); transform: translate(-1px, 1px); }
      }
      @keyframes v-glitch-2 {
          0% { clip-path: inset(10% 0 80% 0); transform: translate(3px, -1px); }
          30% { clip-path: inset(70% 0 15% 0); transform: translate(-3px, 1px); }
          60% { clip-path: inset(30% 0 50% 0); transform: translate(2px, -2px); }
          100% { clip-path: inset(50% 0 30% 0); transform: translate(-2px, 2px); }
      }
      .vocode-subtitle {
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 11px !important;
          font-weight: 600 !important;
          letter-spacing: 4px !important;
          color: rgba(190, 160, 110, 0.8) !important;
          text-transform: uppercase !important;
          margin-top: 8px !important;
      }

      /* ── LARGE DRAG & DROP BOX (CLICKABLE ANYWHERE, NO SEPARATE UPLOAD BUTTON) ── */
      div[data-testid="stFileUploader"] {
          width: 100% !important;
          max-width: 620px !important;
          margin: 0 auto !important;
          padding: 0 !important;
      }
      div[data-testid="stFileUploader"] label {
          display: none !important;
      }
      section[data-testid="stFileUploaderDropzone"] {
          background: rgba(14, 12, 9, 0.82) !important;
          border: 2px dashed rgba(160, 130, 80, 0.6) !important;
          border-radius: 20px !important;
          min-height: 230px !important;
          width: 100% !important;
          cursor: pointer !important;
          position: relative !important;
          backdrop-filter: blur(16px) !important;
          -webkit-backdrop-filter: blur(16px) !important;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(0, 0, 0, 0.5) !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: center !important;
          padding: 38px 24px !important;
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
      }
      section[data-testid="stFileUploaderDropzone"]:hover {
          border-color: #00E5FF !important;
          box-shadow: 0 0 45px rgba(0, 229, 255, 0.25), inset 0 0 30px rgba(0, 0, 0, 0.5) !important;
          transform: translateY(-2px) !important;
      }

      /* Native file input covers the ENTIRE dropzone so clicking anywhere triggers folder open */
      section[data-testid="stFileUploaderDropzone"] input[type="file"] {
          position: absolute !important;
          inset: 0 !important;
          width: 100% !important;
          height: 100% !important;
          opacity: 0 !important;
          cursor: pointer !important;
          z-index: 20 !important;
          display: block !important;
      }

      /* REMOVE the auxiliary upload / browse button completely from dropzone */
      section[data-testid="stFileUploaderDropzone"] button,
      section[data-testid="stFileUploaderDropzone"] span:has(button) {
          display: none !important;
      }

      /* Visual instructions inside dropzone */
      div[data-testid="stFileUploaderDropzoneInstructions"] {
          pointer-events: none !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: center !important;
          text-align: center !important;
      }
      div[data-testid="stFileUploaderDropzoneInstructions"]::before {
          content: "🎙️" !important;
          font-size: 52px !important;
          display: block !important;
          margin-bottom: 12px !important;
          filter: drop-shadow(0 0 14px rgba(0, 229, 255, 0.5)) !important;
          line-height: 1 !important;
      }
      div[data-testid="stFileUploaderDropzoneInstructions"]::after {
          content: "Drop your audio here or click to browse" !important;
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 16px !important;
          font-weight: 700 !important;
          color: #FFFFFF !important;
          letter-spacing: 0.5px !important;
          display: block !important;
          margin-bottom: 6px !important;
      }
      div[data-testid="stFileUploaderDropzoneInstructions"] span,
      div[data-testid="stFileUploaderDropzoneInstructions"] div {
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 12px !important;
          color: rgba(190, 160, 110, 0.75) !important;
          letter-spacing: 1.5px !important;
      }

      /* Uploaded file badge pill */
      div[data-testid="stFileUploaderFile"] {
          background: rgba(18, 15, 10, 0.95) !important;
          border: 1px solid rgba(0, 229, 255, 0.4) !important;
          border-radius: 12px !important;
          padding: 12px 18px !important;
          color: #00E5FF !important;
          font-weight: 600 !important;
          font-size: 14px !important;
          margin-top: 10px !important;
          width: 100% !important;
          max-width: 620px !important;
          box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5) !important;
      }
      div[data-testid="stFileUploaderFile"] button {
          display: inline-flex !important;
          background: transparent !important;
          border: none !important;
          color: #8B949E !important;
          cursor: pointer !important;
      }
      div[data-testid="stFileUploaderFile"] button:hover {
          color: #FF1744 !important;
      }

      /* ── TRANSCRIPT BUTTON (SAME EXACT WIDTH AS UPLOAD BOX) ── */
      div.st-key-transcript_toggle {
          width: 100% !important;
          max-width: 620px !important;
          margin-top: 12px !important;
      }
      div.st-key-transcript_toggle button {
          width: 100% !important;
          background: rgba(20, 16, 11, 0.92) !important;
          border: 1.5px solid rgba(160, 130, 80, 0.55) !important;
          color: rgba(210, 180, 120, 0.9) !important;
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 14px !important;
          font-weight: 700 !important;
          letter-spacing: 1px !important;
          border-radius: 12px !important;
          padding: 13px 20px !important;
          transition: all 0.25s ease !important;
      }
      div.st-key-transcript_toggle button:hover {
          border-color: #00E5FF !important;
          color: #00E5FF !important;
          box-shadow: 0 0 20px rgba(0, 229, 255, 0.25) !important;
      }

      /* Transcript Text Area (Same exact width as upload box) */
      div.st-key-transcript_area {
          width: 100% !important;
          max-width: 620px !important;
          margin-top: 8px !important;
      }
      div.st-key-transcript_area textarea {
          background: rgba(10, 8, 5, 0.95) !important;
          border: 1.5px solid rgba(140, 115, 70, 0.6) !important;
          border-radius: 12px !important;
          color: #E6EDF3 !important;
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 13px !important;
          width: 100% !important;
          backdrop-filter: blur(14px) !important;
      }

      /* ── NEON GREEN "Lets Go !" BUTTON (SAME EXACT WIDTH AS UPLOAD BOX) ── */
      div.st-key-lets_go_btn {
          width: 100% !important;
          max-width: 620px !important;
          margin-top: 14px !important;
      }
      div.st-key-lets_go_btn button {
          width: 100% !important;
          background: linear-gradient(135deg, #00FF88 0%, #00E676 50%, #00C853 100%) !important;
          border: none !important;
          color: #050608 !important;
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 20px !important;
          font-weight: 900 !important;
          letter-spacing: 2px !important;
          text-transform: uppercase !important;
          border-radius: 14px !important;
          padding: 18px 30px !important;
          box-shadow: 0 0 40px rgba(0, 230, 118, 0.7), 0 0 80px rgba(0, 230, 118, 0.3) !important;
          transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
          cursor: pointer !important;
      }
      div.st-key-lets_go_btn button:hover {
          transform: scale(1.02) !important;
          box-shadow: 0 0 60px rgba(0, 230, 118, 0.9), 0 0 110px rgba(0, 230, 118, 0.4) !important;
      }
      div.st-key-lets_go_btn button:active {
          transform: scale(0.98) !important;
      }
      div.st-key-lets_go_btn button p {
          font-size: 20px !important;
          font-weight: 900 !important;
          letter-spacing: 2px !important;
          color: #050608 !important;
          margin: 0 !important;
      }
    </style>
    """, unsafe_allow_html=True)

    # ── Tape Recorder Background Canvas (Both reels rotate in SAME direction) ──
    tape_reel_html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
(function() {
  let doc = document;
  let win = window;
  try {
    if (window.parent && window.parent.document && window.parent.document.body) {
      doc = window.parent.document;
      win = window.parent;
    }
  } catch (e) {
    // fallback to current window
  }

  let canvas = doc.getElementById('vocode-tape-canvas');
  if (!canvas) {
    canvas = doc.createElement('canvas');
    canvas.id = 'vocode-tape-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    doc.body.prepend(canvas);
  }

  const ctx = canvas.getContext('2d');
  let W, H;
  function resize() {
    W = canvas.width = win.innerWidth || 1920;
    H = canvas.height = win.innerHeight || 1080;
  }
  win.removeEventListener('resize', resize);
  win.addEventListener('resize', resize);
  resize();

  const PARTICLES = 90;
  const particles = Array.from({ length: PARTICLES }, () => ({
    x: Math.random() * (win.innerWidth || 1920),
    y: Math.random() * (win.innerHeight || 1080),
    r: Math.random() * 1.3 + 0.3,
    alpha: Math.random() * 0.35 + 0.05,
    vx: (Math.random() - 0.5) * 0.25,
    vy: (Math.random() - 0.5) * 0.25
  }));

  let angle = win.__vocode_reel_angle || 0;

  function drawReel(cx, cy, radius, rot) {
    ctx.save();
    ctx.translate(cx, cy);

    // Outer ambient golden glow
    const glow = ctx.createRadialGradient(0, 0, radius * 0.65, 0, 0, radius + 22);
    glow.addColorStop(0, 'rgba(0, 0, 0, 0)');
    glow.addColorStop(1, 'rgba(140, 100, 45, 0.16)');
    ctx.beginPath();
    ctx.arc(0, 0, radius + 22, 0, Math.PI * 2);
    ctx.fillStyle = glow;
    ctx.fill();

    // Dark brushed metal reel flange
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    const bodyGrad = ctx.createRadialGradient(-radius * 0.25, -radius * 0.25, radius * 0.1, 0, 0, radius);
    bodyGrad.addColorStop(0, '#262017');
    bodyGrad.addColorStop(0.5, '#16130e');
    bodyGrad.addColorStop(1, '#0a0907');
    ctx.fillStyle = bodyGrad;
    ctx.fill();

    // Outer rim bevel
    ctx.lineWidth = 3.5;
    const edgeGrad = ctx.createLinearGradient(-radius, -radius, radius, radius);
    edgeGrad.addColorStop(0, '#55432d');
    edgeGrad.addColorStop(0.5, '#2c2217');
    edgeGrad.addColorStop(1, '#15110c');
    ctx.strokeStyle = edgeGrad;
    ctx.stroke();

    // Rotating assembly
    ctx.save();
    ctx.rotate(rot);

    // Concentric tape pack windings
    for (let i = 0; i < 8; i++) {
      const r = radius * (0.33 + i * 0.08);
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.lineWidth = 1;
      ctx.strokeStyle = `rgba(110, 85, 50, ${0.08 + i * 0.025})`;
      ctx.stroke();
    }

    // 3 Classic NAB circular cutouts
    for (let s = 0; s < 3; s++) {
      const a = (Math.PI * 2 / 3) * s;
      const holeDist = radius * 0.58;
      const holeR = radius * 0.21;
      ctx.save();
      ctx.rotate(a);
      ctx.beginPath();
      ctx.arc(0, holeDist, holeR, 0, Math.PI * 2);
      ctx.fillStyle = '#060709';
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#382b1c';
      ctx.stroke();
      ctx.restore();
    }

    // 3 structural spokes
    for (let s = 0; s < 3; s++) {
      const a = (Math.PI * 2 / 3) * s + Math.PI / 3;
      const armLen = radius * 0.55;
      const armW = radius * 0.13;
      ctx.save();
      ctx.rotate(a);
      ctx.beginPath();
      if (ctx.roundRect) {
        ctx.roundRect(-armW / 2, radius * 0.15, armW, armLen - radius * 0.15, 3);
      } else {
        ctx.rect(-armW / 2, radius * 0.15, armW, armLen - radius * 0.15);
      }
      ctx.fillStyle = '#1e1811';
      ctx.fill();
      ctx.strokeStyle = 'rgba(95, 75, 45, 0.45)';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();
    }

    ctx.restore(); // end rot

    // Center hub clamp
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.16, 0, Math.PI * 2);
    const hubGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, radius * 0.16);
    hubGrad.addColorStop(0, '#5a4630');
    hubGrad.addColorStop(0.7, '#2b2216');
    hubGrad.addColorStop(1, '#15110c');
    ctx.fillStyle = hubGrad;
    ctx.fill();
    ctx.strokeStyle = '#8c7049';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Center spindle pin
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.05, 0, Math.PI * 2);
    ctx.fillStyle = '#bfa16f';
    ctx.fill();

    ctx.restore();
  }

  function drawTapeBridge(x1, y1, x2, y2) {
    const slack = Math.abs(x2 - x1) * 0.035;
    ctx.beginPath();
    ctx.moveTo(x1, y1 - 4);
    ctx.bezierCurveTo(x1 + slack, y1 - 4 - slack * 0.2, x2 - slack, y2 - 4 - slack * 0.2, x2, y2 - 4);
    ctx.lineTo(x2, y2 + 4);
    ctx.bezierCurveTo(x2 - slack, y2 + 4 - slack * 0.2, x1 + slack, y1 + 4 - slack * 0.2, x1, y1 + 4);
    ctx.closePath();
    const tg = ctx.createLinearGradient(x1, y1 - 4, x1, y1 + 4);
    tg.addColorStop(0, 'rgba(110, 88, 55, 0.85)');
    tg.addColorStop(0.5, 'rgba(60, 48, 30, 0.95)');
    tg.addColorStop(1, 'rgba(35, 28, 18, 0.85)');
    ctx.fillStyle = tg;
    ctx.fill();

    // subtle sheen line along tape
    ctx.beginPath();
    ctx.moveTo(x1, y1 - 1);
    ctx.bezierCurveTo(x1 + slack, y1 - 1 - slack * 0.2, x2 - slack, y2 - 1 - slack * 0.2, x2, y2 - 1);
    ctx.strokeStyle = 'rgba(180, 150, 100, 0.22)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function drawVignette() {
    const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 0.9);
    vg.addColorStop(0, 'rgba(0, 0, 0, 0)');
    vg.addColorStop(1, 'rgba(6, 7, 9, 0.82)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, W, H);
  }

  if (win.__vocode_anim_id) {
    win.cancelAnimationFrame(win.__vocode_anim_id);
  }

  function render() {
    angle += 0.012;
    win.__vocode_reel_angle = angle;

    ctx.fillStyle = '#060709';
    ctx.fillRect(0, 0, W, H);

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = W;
      if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H;
      if (p.y > H) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(180, 145, 90, ${p.alpha})`;
      ctx.fill();
    });

    // Dual reels on left and right sides of viewport
    const R = Math.min(W * 0.22, H * 0.36);
    const rL = { x: W * 0.18, y: H * 0.44 };
    const rR = { x: W * 0.82, y: H * 0.44 };

    drawTapeBridge(rL.x, rL.y - R, rR.x, rR.y - R);

    // BOTH REELS ROTATE IN THE EXACT SAME DIRECTION (angle, angle)
    drawReel(rL.x, rL.y, R, angle);
    drawReel(rR.x, rR.y, R, angle);

    drawVignette();
    win.__vocode_anim_id = win.requestAnimationFrame(render);
  }
  win.__vocode_anim_id = win.requestAnimationFrame(render);
})();
</script>
</body>
</html>"""

    import streamlit.components.v1 as components
    components.html(tape_reel_html, height=0, scrolling=False)

    # ── VOCODE Header Block (At Top Center) ──
    st.markdown("""
    <div class="vocode-header-block">
      <div class="vocode-glitch-title" data-text="VOCODE">VOCODE</div>
      <div class="vocode-subtitle">Contrastive Speech Analytics Engine</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Large Drag & Drop Box (Centered in Middle) ──
    uploaded_file = st.file_uploader(
        "audio_upload",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        label_visibility="collapsed",
        key="audio_uploader"
    )

    # ── Post-Upload Controls: ONLY shown once file is uploaded ──
    if uploaded_file is not None:
        btn_label = "📄 Hide Reference Transcript" if st.session_state["show_transcript_input"] else "📄 Add Reference Transcript (Optional)"
        if st.button(btn_label, key="transcript_toggle", use_container_width=True):
            st.session_state["show_transcript_input"] = not st.session_state["show_transcript_input"]
            st.rerun()

        if st.session_state["show_transcript_input"]:
            transcript_val = st.text_area(
                "Reference Transcript",
                value=st.session_state["transcript_text"],
                placeholder="Paste reference transcript here... If empty, autonomous Whisper ASR will transcribe.",
                height=90,
                key="transcript_area",
                label_visibility="collapsed"
            )
            st.session_state["transcript_text"] = transcript_val
        else:
            transcript_val = st.session_state.get("transcript_text", "")

        lets_go = st.button("⚡ Lets Go !", key="lets_go_btn", use_container_width=True)
    else:
        transcript_val = ""
        lets_go = False

    # ── Speech Evaluation Pipeline ──
    if lets_go and uploaded_file is not None:
        with st.spinner("🎛️ Routing audio through VOCODE forensic signal chain..."):
            raw_bytes = uploaded_file.read()
            filename = uploaded_file.name

            norm_res = normalize_uploaded_audio(raw_bytes, filename)
            clean_wav = norm_res["clean_wav_path"]
            raw_audio_path = norm_res.get("raw_path") or clean_wav

            align_res = resolve_and_align_transcript(clean_wav, transcript_val)
            speech_events = align_res.get("speech_events", [])

            eval_res = evaluate_audio(
                clean_wav_path=clean_wav,
                speech_events=speech_events,
                leniency=0.0,
                external_flaws=[]
            )
            metrics = eval_res["metrics"]
            grade_report = eval_res["grade_report"]

            moves = classify_speech_moves(clean_wav, speech_events, grade_report.get("deductions", []))

            explanation = generate_speech_explanation(
                grade_report=grade_report,
                moves=moves,
                metrics=metrics,
                api_key=os.getenv("GROQ_API_KEY")
            )

            st.session_state["processed_data"] = {
                "clean_wav": clean_wav,
                "raw_audio_path": raw_audio_path,
                "filename": filename,
                "metrics": metrics,
                "grade_report": grade_report,
                "moves": moves,
                "explanation": explanation,
                "canonical_transcript": align_res.get("canonical_text", "")
            }
            st.session_state["current_page"] = "results"
            st.query_params["page"] = "results"
            st.rerun()


# =============================================================
# PAGE 2: RESULTS WEBPAGE (Swipe Animation + Rubrics Dashboard)
# =============================================================
elif st.session_state["current_page"] == "results":
    data = st.session_state.get("processed_data")
    if not data:
        st.session_state["current_page"] = "upload"
        st.query_params["page"] = "upload"
        st.rerun()

    grade_report = data["grade_report"]
    metrics = data["metrics"]
    moves = data["moves"]
    explanation = data["explanation"]
    clean_wav = data["clean_wav"]
    raw_audio_path = data.get("raw_audio_path") or clean_wav
    if not os.path.exists(raw_audio_path):
        raw_audio_path = clean_wav

    total_grade = grade_report.get("total_grade", 7.0)
    grade_band = grade_report.get("grade_band", "Proficient")
    gating = grade_report.get("gating_diagnostics", {})
    gate_ceiling = gating.get("gate_cap", 10.0)
    psi_index = gating.get("psi_impairment_index", 0.0)
    pillar_scores = grade_report.get("pillar_scores", {})

    import streamlit.components.v1 as components
    components.html("""<script>
      (function() {
        try {
          const doc = window.parent.document;
          const win = window.parent;
          const c = doc.getElementById('vocode-tape-canvas');
          if (c) c.remove();
          if (win.__vocode_anim_id) {
            win.cancelAnimationFrame(win.__vocode_anim_id);
          }
        } catch(e) {}
      })();
    </script>""", height=0)

    st.markdown("""
    <style>
      .stApp {
          background-color: #0A0D14 !important;
          overflow-x: hidden !important;
      }
      [data-testid="stMain"] {
          display: block !important;
          min-height: auto !important;
      }
      [data-testid="stAppViewContainer"],
      [data-testid="stMainBlockContainer"],
      .block-container {
          position: relative !important;
          width: 100% !important;
          max-width: 100% !important;
          padding: 18px 28px !important;
          margin: 0 !important;
      }

      /* Swipe Animation onto Web Page */
      @keyframes swipeInPage {
          0% {
              transform: translateX(100vw);
              opacity: 0;
          }
          100% {
              transform: translateX(0);
              opacity: 1;
          }
      }
      .rubrics-swipe-container {
          animation: swipeInPage 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
      }

      /* Top navigation back button */
      div.st-key-results_back_btn button {
          background: #161B22 !important;
          border: 1px solid #30363D !important;
          color: #8B949E !important;
          font-family: 'Space Grotesk', sans-serif !important;
          font-size: 13px !important;
          font-weight: 700 !important;
          border-radius: 8px !important;
          padding: 8px 18px !important;
          transition: all 0.2s ease !important;
      }
      div.st-key-results_back_btn button:hover {
          border-color: #00E5FF !important;
          color: #00E5FF !important;
      }

      /* Dial container */
      .dial-hero-card {
          background: #141822;
          border: 1px solid #232B3A;
          border-radius: 16px;
          padding: 16px;
          box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      }

      /* Rubric item cards alongside dial */
      .rubric-score-row {
          background: #141822;
          border: 1px solid #232B3A;
          border-radius: 10px;
          padding: 10px 14px;
          margin-bottom: 8px;
          transition: border-color 0.2s;
      }
      .rubric-score-row:hover {
          border-color: rgba(0, 229, 255, 0.35);
      }

      /* Explanation textbox */
      .rubric-expl-textbox {
          background: #0E121A;
          border: 1px solid rgba(0, 229, 255, 0.35);
          border-left: 4px solid #00E5FF;
          border-radius: 10px;
          padding: 14px 16px;
          margin-top: 6px;
          margin-bottom: 12px;
          animation: fadeInText 0.25s ease both;
      }
      @keyframes fadeInText {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
      }

      /* Audio Visualizer Hero Box */
      .visualizer-hero-box {
          background: #121620;
          border: 1px solid #232B3A;
          border-radius: 16px;
          padding: 6px 14px 16px;
          margin: 18px 0;
          width: 100%;
          box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      }

      /* Tabs styling */
      .stTabs [data-baseweb="tab-list"] {
          gap: 8px;
          background-color: #141822;
          padding: 6px;
          border-radius: 12px;
          border: 1px solid #232B3A;
      }
      .stTabs [data-baseweb="tab"] {
          border-radius: 8px;
          color: #8B949E;
          font-weight: 700;
          font-size: 14px;
          padding: 10px 24px;
      }
      .stTabs [aria-selected="true"] {
          background-color: #1F2736 !important;
          color: #00E5FF !important;
          box-shadow: 0 0 16px rgba(0, 229, 255, 0.2);
      }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="rubrics-swipe-container">', unsafe_allow_html=True)

    # ── Top Bar: Back Button & Header ──
    t_col1, t_col2, t_col3 = st.columns([0.15, 0.70, 0.15])
    with t_col1:
        if st.button("← New Audio", key="results_back_btn"):
            st.session_state["current_page"] = "upload"
            st.session_state["processed_data"] = None
            st.query_params["page"] = "upload"
            st.rerun()
    with t_col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 8px;">
          <span style="font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 900; letter-spacing: 8px; color: #FFFFFF;">
            VOCODE
          </span>
          <span style="color: #8B949E; font-size: 12px; letter-spacing: 2px; display: block; text-transform: uppercase;">
            Contrastive Oratorical Performance Evaluation
          </span>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # ROW 1: DIAL (TOP RIGHT) WITH RUBRIC SCORES ALONGSIDE IT
    # ─────────────────────────────────────────────────────────
    rubrics_col, dial_col = st.columns([1.35, 1.0])

    with dial_col:
        st.markdown('<div class="dial-hero-card">', unsafe_allow_html=True)
        render_score_dial(total_grade, grade_band, gate_ceiling, psi_index)
        st.markdown('</div>', unsafe_allow_html=True)

    with rubrics_col:
        st.markdown("""
        <div style="font-size: 14px; font-weight: 800; color: #8B949E; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;">
          📊 Rubric Scores & Diagnostics
        </div>
        """, unsafe_allow_html=True)

        PILLARS = [
            {"key": "pitch_modulation_out_of_2_5", "slug": "pitch_modulation", "name": "Pitch Modulation", "max": 2.5, "color": "#00E5FF"},
            {"key": "cadence_and_tempo_out_of_2_5", "slug": "cadence_and_tempo", "name": "Cadence & Tempo", "max": 2.5, "color": "#00E676"},
            {"key": "rhetorical_pausing_out_of_2_0", "slug": "rhetorical_pausing", "name": "Rhetorical Pausing", "max": 2.0, "color": "#FFD600"},
            {"key": "dynamic_energy_out_of_1_5", "slug": "dynamic_energy", "name": "Dynamic Energy", "max": 1.5, "color": "#FF9100"},
            {"key": "spectral_clarity_out_of_1_5", "slug": "spectral_clarity", "name": "Spectral Clarity", "max": 1.5, "color": "#E040FB"},
        ]

        critiques = explanation.get("pillar_critiques", {})

        for p in PILLARS:
            val = float(pillar_scores.get(p["key"], p["max"]))
            pct = min(1.0, max(0.0, val / p["max"]))
            slug = p["slug"]
            is_open = st.session_state.get(f"expl_open_{slug}", False)

            col_row, col_btn = st.columns([0.84, 0.16])
            with col_row:
                st.markdown(
                    f"""<div class="rubric-score-row">
                      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: #E6EDF3; font-weight: 700; font-size: 13px;">{p['name']}</span>
                        <span style="color: {p['color']}; font-weight: 800; font-size: 13px;">{val:.2f} / {p['max']:.1f}</span>
                      </div>
                      <div style="background: #1B212D; height: 7px; border-radius: 4px; overflow: hidden;">
                        <div style="background: {p['color']}; height: 100%; width: {pct * 100:.1f}%; border-radius: 4px; box-shadow: 0 0 8px {p['color']}66;"></div>
                      </div>
                    </div>""",
                    unsafe_allow_html=True
                )
            with col_btn:
                toggle_txt = "✕ Close" if is_open else "▼ Explain"
                if st.button(toggle_txt, key=f"expl_toggle_{slug}", use_container_width=True):
                    st.session_state[f"expl_open_{slug}"] = not is_open
                    st.rerun()

            # LLM-Generated Semantic Explanation Text Box (Closeable)
            if is_open:
                critique_text = critiques.get(slug, explanation.get("executive_verdict", "Semantic critique computed by dual-layer reasoning engine."))
                box_c1, box_c2 = st.columns([0.90, 0.10])
                with box_c1:
                    st.markdown(
                        f"""<div class="rubric-expl-textbox">
                          <div style="color: {p['color']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px;">
                            🤖 LLM Semantic Explanation • {p['name']}
                          </div>
                          <div style="color: #D2DAE4; font-size: 13px; line-height: 1.6;">
                            {critique_text}
                          </div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                with box_c2:
                    if st.button("✕", key=f"expl_close_{slug}", help="Close explanation"):
                        st.session_state[f"expl_open_{slug}"] = False
                        st.rerun()

    # ─────────────────────────────────────────────────────────
    # ROW 2: AUDIO VISUALIZER & PLAYBACK (COVERING ENTIRETY OF LENGTH)
    # ─────────────────────────────────────────────────────────
    st.markdown('<div class="visualizer-hero-box">', unsafe_allow_html=True)

    # Move Waveform Timeline Inspector (Full width)
    render_move_waveform_inspector(raw_audio_path, moves)

    # HTML5 Audio Player with Play/Pause (single button) and ahead/behind jump buttons
    import base64
    audio_for_player = raw_audio_path
    if os.path.exists(raw_audio_path) and os.path.getsize(raw_audio_path) > 15 * 1024 * 1024:
        if os.path.exists(clean_wav) and os.path.getsize(clean_wav) < os.path.getsize(raw_audio_path):
            audio_for_player = clean_wav

    ext = os.path.splitext(audio_for_player)[-1].lower()
    _mime_map = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".ogg": "audio/ogg", ".flac": "audio/flac"}
    mime_type = _mime_map.get(ext, "audio/wav")
    try:
        with open(audio_for_player, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
    except Exception:
        _b64 = ""

    seek_target = st.session_state.get("seek_timestamp")
    seek_js = ""
    if seek_target is not None:
        seek_js = f"""
        (function(){{
          const t = {float(seek_target)};
          const a = document.getElementById('voc_audio');
          if(a){{
            const do_seek = () => {{ a.currentTime = t; a.play().catch(() => {{}}); }};
            if (a.readyState >= 1) do_seek();
            else a.addEventListener('canplay', do_seek, {{ once: true }});
          }}
        }})();"""

    player_html = f"""
    <div style="padding: 12px 16px 14px; background: #0D1017; border-radius: 12px; border: 1px solid #232B3A; margin-top: 10px;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 700; color: #8B949E; letter-spacing: 2px; text-transform: uppercase;">
          🎧 Raw Audio Signal • {data['filename']}
        </div>
        <div id="voc_time" style="font-size: 13px; color: #8B949E; font-family: monospace;">00:00 / --:--</div>
      </div>

      <audio id="voc_audio" preload="auto" style="width: 100%; height: 38px; border-radius: 8px; display: block; margin-bottom: 12px;">
        <source src="data:{mime_type};base64,{_b64}" type="{mime_type}">
      </audio>

      <div style="display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap;">
        <button onclick="voc_skip(-10)"
          style="background: #161B22; color: #8B949E; border: 1px solid #30363D; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'Space Grotesk', sans-serif; transition: all 0.2s;"
          onmouseover="this.style.color='#FFFFFF'" onmouseout="this.style.color='#8B949E'">
          ⏮ -10s
        </button>
        <button onclick="voc_skip(-5)"
          style="background: #161B22; color: #8B949E; border: 1px solid #30363D; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'Space Grotesk', sans-serif; transition: all 0.2s;"
          onmouseover="this.style.color='#FFFFFF'" onmouseout="this.style.color='#8B949E'">
          ◀ -5s
        </button>
        <button id="voc_playbtn" onclick="voc_toggle()"
          style="background: linear-gradient(135deg, #00FF88 0%, #00E676 100%); color: #050608; border: none; padding: 9px 32px; border-radius: 50px; cursor: pointer; font-size: 14px; font-weight: 900; font-family: 'Space Grotesk', sans-serif; letter-spacing: 1px; box-shadow: 0 0 20px rgba(0, 230, 118, 0.45); transition: all 0.25s;">
          ▶ Play
        </button>
        <button onclick="voc_skip(5)"
          style="background: #161B22; color: #8B949E; border: 1px solid #30363D; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'Space Grotesk', sans-serif; transition: all 0.2s;"
          onmouseover="this.style.color='#FFFFFF'" onmouseout="this.style.color='#8B949E'">
          +5s ▶
        </button>
        <button onclick="voc_skip(10)"
          style="background: #161B22; color: #8B949E; border: 1px solid #30363D; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'Space Grotesk', sans-serif; transition: all 0.2s;"
          onmouseover="this.style.color='#FFFFFF'" onmouseout="this.style.color='#8B949E'">
          +10s ⏭
        </button>
        <select onchange="voc_speed(this.value)"
          style="background: #161B22; color: #8B949E; border: 1px solid #30363D; padding: 7px 12px; border-radius: 8px; font-size: 13px; font-family: 'Space Grotesk', sans-serif;">
          <option value="0.5">0.5x</option>
          <option value="0.75">0.75x</option>
          <option value="1.0" selected>1.0x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2.0">2.0x</option>
        </select>
      </div>
    </div>
    <script>
    const voc_a = document.getElementById('voc_audio');
    const voc_t = document.getElementById('voc_time');
    const voc_pb = document.getElementById('voc_playbtn');
    function fmt(s) {{
      const m = Math.floor(s / 60);
      const sec = Math.floor(s % 60);
      return (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
    }}
    if (voc_a) {{
      voc_a.addEventListener('timeupdate', () => {{
        if (voc_t) voc_t.innerText = fmt(voc_a.currentTime) + ' / ' + fmt(voc_a.duration || 0);
      }});
      voc_a.addEventListener('play', () => {{ if (voc_pb) voc_pb.innerText = '⏸ Pause'; }});
      voc_a.addEventListener('pause', () => {{ if (voc_pb) voc_pb.innerText = '▶ Play'; }});
    }}
    function voc_toggle() {{
      if (voc_a.paused) voc_a.play();
      else voc_a.pause();
    }}
    function voc_skip(d) {{
      if (voc_a) voc_a.currentTime = Math.max(0, Math.min(voc_a.duration || 0, voc_a.currentTime + d));
    }}
    function voc_speed(r) {{
      if (voc_a) voc_a.playbackRate = parseFloat(r);
    }}
    {seek_js}
    </script>"""

    import streamlit.components.v1 as _comp
    _comp.html(player_html, height=170)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # ROW 3: DESIGNATED TABS — COACH | BREAKDOWN | TECHNICALS
    # ─────────────────────────────────────────────────────────
    tab_coach, tab_breakdown, tab_tech = st.tabs([
        "🧑‍🏫 coach",
        "🎯 breakdown",
        "🔬 technicals"
    ])

    with tab_coach:
        render_coach_tab(explanation, grade_report, moves, metrics, raw_audio_path)

    with tab_breakdown:
        st.markdown("#### 🎯 Chronological Rhetorical Move Breakdown")
        filter_type = st.radio(
            "Filter Move Types:",
            ["All Moves", "Only Blunders (❌)", "Only Brilliant (✨)", "Imperfections (Blunders, Mistakes, Inaccuracies)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        filtered_moves = moves
        if filter_type == "Only Blunders (❌)":
            filtered_moves = [m for m in moves if m["move_type"] == "BLUNDER"]
        elif filter_type == "Only Brilliant (✨)":
            filtered_moves = [m for m in moves if m["move_type"] == "BRILLIANT"]
        elif filter_type == "Imperfections (Blunders, Mistakes, Inaccuracies)":
            filtered_moves = [m for m in moves if m["move_type"] in ["BLUNDER", "MISTAKE", "INACCURACY"]]

        if not filtered_moves:
            st.info("No moves match the selected filter.")
        else:
            for m in filtered_moves:
                mc1, mc2 = st.columns([0.88, 0.12])
                with mc1:
                    st.markdown(
                        f"<div style='background: #141822; border-left: 5px solid {m['color']}; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;'>"
                        f"<div style='display: flex; justify-content: space-between;'>"
                        f"<span style='color: {m['color']}; font-weight: 700; font-size: 13px;'>{m['icon']} {m['label']} • [{m['t_start']}s – {m['t_end']}s]</span>"
                        f"<span style='color: #8B949E; font-size: 12px;'>{m['duration']}s duration</span>"
                        f"</div>"
                        f"<div style='color: #E6EDF3; font-size: 13px; font-weight: 500; margin: 4px 0;'>\"{m['text']}\"</div>"
                        f"<div style='color: #8B949E; font-size: 12px;'><b>Rationale:</b> {m['reason']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with mc2:
                    if st.button("▶ Jump", key=f"jump_{m['index']}", help=f"Seek player to {m['t_start']}s"):
                        st.session_state["seek_timestamp"] = m["t_start"]
                        st.rerun()

        st.markdown("---")
        render_rubrics_tab(grade_report, metrics)

    with tab_tech:
        render_technical_breakdown(explanation, metrics=metrics, grade_report=grade_report)
        st.markdown("---")
        render_qualitative_breakdown(explanation)
        st.markdown("---")
        render_telemetry_view(clean_wav, metrics)

    st.markdown('</div>', unsafe_allow_html=True)
