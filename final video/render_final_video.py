import os
import subprocess

FINAL_VIDEO_DIR = "final video"
SLIDES_DIR = os.path.join(FINAL_VIDEO_DIR, "slides")
AUDIO_DIR = os.path.join(FINAL_VIDEO_DIR, "audio")

CONCAT_FILE = os.path.join(FINAL_VIDEO_DIR, "slides_concat.txt")

# Updated Slide timeline to match natural neural voice cadence (exactly 300.0 seconds)
TIMELINE = [
    ("slide_1a_title.png", 11.0),
    ("slide_1b_crisis.png", 18.0),
    ("slide_2a_flaws.png", 29.0),
    ("slide_3a_dataset.png", 31.0),
    ("slide_4a_pipeline.png", 40.0),
    ("slide_5a_landing.png", 12.0),
    ("slide_5b_presets.png", 12.0),
    ("slide_5c_results_dial.png", 13.0),
    ("slide_5d_waveform.png", 13.0),
    ("slide_5e_botched_freeze.png", 13.0),
    ("slide_5f_coach_tab.png", 12.0),
    ("slide_6a_architecture.png", 39.0),
    ("slide_7a_rubrics.png", 35.0),
    ("slide_8a_conclusion.png", 22.0)
]

print("Writing concat script...")
with open(CONCAT_FILE, "w") as f:
    for fname, dur in TIMELINE:
        abs_path = os.path.abspath(os.path.join(SLIDES_DIR, fname))
        f.write(f"file '{abs_path}'\n")
        f.write(f"duration {dur}\n")
    # Concat demuxer requirement: repeat last file without duration
    last_abs = os.path.abspath(os.path.join(SLIDES_DIR, TIMELINE[-1][0]))
    f.write(f"file '{last_abs}'\n")

total_time = sum(d for _, d in TIMELINE)
print(f"Total video planned timeline: {total_time} seconds (5:00.00).")

AUDIO_MIX = os.path.abspath(os.path.join(AUDIO_DIR, "vocode_audio_mix_master.wav"))
SRT_FILE = os.path.abspath(os.path.join(FINAL_VIDEO_DIR, "vocode_captions.srt"))
OUT_MP4 = os.path.abspath(os.path.join(FINAL_VIDEO_DIR, "vocode_showcase_5min.mp4"))
OUT_FINAL = os.path.abspath(os.path.join(FINAL_VIDEO_DIR, "final_video.mp4"))

sub_filter = f"subtitles='{SRT_FILE}':force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,MarginV=30,Alignment=2'"

cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", CONCAT_FILE,
    "-i", AUDIO_MIX,
    "-vf", f"{sub_filter},format=yuv420p",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-r", "30",
    "-c:a", "aac",
    "-b:a", "192k",
    "-t", "300.0",
    OUT_MP4
]

print("Executing FFmpeg render command:")
print(" ".join(cmd))
subprocess.check_call(cmd)

import shutil
shutil.copyfile(OUT_MP4, OUT_FINAL)
shutil.copyfile(OUT_MP4, "final_video.mp4")

print(f"\nRender Complete! Output saved to:\n  1. {OUT_MP4}\n  2. {OUT_FINAL}\n  3. final_video.mp4")
