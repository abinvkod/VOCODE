import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "final video/slides"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080

def get_font(size, bold=False):
    # Try system fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_header(draw, title, subtitle="VOCODE — Contrastive Speech Analytics"):
    # Subtle top header bar
    draw.rectangle([0, 0, WIDTH, 80], fill=(14, 18, 25))
    draw.line([0, 80, WIDTH, 80], fill=(30, 41, 59), width=2)
    
    font_sub = get_font(20, bold=False)
    font_title = get_font(28, bold=True)
    
    draw.text((60, 26), subtitle.upper(), font=font_sub, fill=(56, 189, 248))
    
    # Track badge on top right
    badge_text = "HACKATHON 2026 • TRACK C"
    bbox = font_sub.getbbox(badge_text)
    tw = bbox[2] - bbox[0]
    bx = WIDTH - 60 - tw - 24
    draw.rounded_rectangle([bx, 20, WIDTH - 60, 60], radius=8, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((bx + 12, 28), badge_text, font=font_sub, fill=(241, 245, 249))

def draw_card(draw, box, fill=(22, 27, 34), outline=(48, 54, 61), radius=16, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

print("Slide generator initialized.")
