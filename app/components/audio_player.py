"""
Audio Player Component: Full HTML5 Playback Engine
Provides Play, Pause, Rewind (-5s), Fast-Forward (+5s), Scrubbable Timebar,
Speed Selector, and Millisecond Seeking Synchronization on Raw Audio.
"""

import os
import mimetypes
import base64
import streamlit as st

def render_interactive_audio_player(audio_path: str, seek_timestamp: float | None = None):
    """
    Renders an HTML5 audio player using the raw audio source with reliable seeking.
    """
    if not os.path.exists(audio_path):
        st.error(f"Audio file not found: {audio_path}")
        return

    ext = os.path.splitext(audio_path)[-1].lower()
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".webm": "audio/webm",
        ".aac": "audio/aac",
    }
    mime_type = mime_map.get(ext) or mimetypes.guess_type(audio_path)[0] or "audio/wav"

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    
    seek_script = ""
    seek_badge = ""
    if seek_timestamp is not None:
        target_s = round(float(seek_timestamp), 2)
        seek_badge = f"""<span style="background: rgba(0, 229, 255, 0.2); color: #00E5FF; border: 1px solid #00E5FF; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">⚡ Jumped to {target_s}s</span>"""
        seek_script = f"""
        <script>
            (function() {{
                const target = {target_s};
                function doSeek() {{
                    const p = document.getElementById('audio_player_el');
                    if (p) {{
                        try {{
                            p.currentTime = target;
                            p.play().catch(function(e) {{ console.log('Autoplay handled:', e); }});
                        }} catch (err) {{
                            console.error('Seek execution error:', err);
                        }}
                    }}
                }}
                const p = document.getElementById('audio_player_el');
                if (p) {{
                    if (p.readyState >= 1) {{
                        doSeek();
                    }} else {{
                        p.addEventListener('loadedmetadata', doSeek, {{ once: true }});
                        p.addEventListener('canplay', doSeek, {{ once: true }});
                    }}
                }}
            }})();
        </script>
        """

    player_html = f"""
    <div style="background: #1E232A; padding: 16px 20px; border-radius: 12px; border: 1px solid #30363D; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="font-weight: 600; font-size: 14px; color: #E6EDF3; display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 10px; height: 10px; background: #00E5FF; border-radius: 50%; box-shadow: 0 0 8px #00E5FF;"></span>
                Raw Audio Track {seek_badge}
            </div>
            <div id="player_status" style="font-size: 13px; color: #8B949E; font-family: monospace;">
                00:00 / --:--
            </div>
        </div>

        <audio id="audio_player_el" style="width: 100%; height: 42px; border-radius: 8px;" controls preload="auto">
            <source src="data:{mime_type};base64,{b64_audio}" type="{mime_type}">
            Your browser does not support the audio element.
        </audio>

        <div style="display: flex; gap: 10px; margin-top: 12px; align-items: center; justify-content: center;">
            <button onclick="skipTime(-5)" style="background: #21262D; color: #C9D1D9; border: 1px solid #363B42; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                ⏪ -5s
            </button>
            <button onclick="togglePlay()" id="play_btn" style="background: #00E5FF; color: #000000; border: none; padding: 6px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 700;">
                ⏯ Play / Pause
            </button>
            <button onclick="skipTime(5)" style="background: #21262D; color: #C9D1D9; border: 1px solid #363B42; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                +5s ⏩
            </button>
            <select onchange="changeSpeed(this.value)" style="background: #21262D; color: #C9D1D9; border: 1px solid #363B42; padding: 6px 10px; border-radius: 6px; font-size: 13px;">
                <option value="0.75">0.75x</option>
                <option value="1.0" selected>1.0x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
            </select>
        </div>
    </div>

    <script>
        const audio = document.getElementById('audio_player_el');
        const status = document.getElementById('player_status');

        function formatTime(sec) {{
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
        }}

        if (audio && status) {{
            audio.addEventListener('timeupdate', () => {{
                status.innerText = formatTime(audio.currentTime) + ' / ' + formatTime(audio.duration || 0);
            }});
        }}

        function togglePlay() {{
            if (audio.paused) {{
                audio.play();
            }} else {{
                audio.pause();
            }}
        }}

        function skipTime(delta) {{
            if (audio) {{
                audio.currentTime = Math.max(0, Math.min(audio.duration || 0, audio.currentTime + delta));
            }}
        }}

        function changeSpeed(rate) {{
            if (audio) {{
                audio.playbackRate = parseFloat(rate);
            }}
        }}
    </script>
    {seek_script}
    """
    st.components.v1.html(player_html, height=140)
