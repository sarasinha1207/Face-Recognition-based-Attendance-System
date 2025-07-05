# 6-Attendance_ui.py
import numpy as np
import cv2
from PIL import Image, ImageDraw

print("Generating the Final UI Background...")

# --- Color Palette & Dimensions ---
BG_COLOR, PANEL_COLOR_LIGHT_BLUE = (248, 249, 250), (233, 244, 248)
HEADER_COLOR_DARK_BLUE, ACCENT_COLOR_BLUE = (8, 94, 125), (66, 110, 180)
IMG_WIDTH, IMG_HEIGHT = 1280, 720

image = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(image)

def paste_transparent(bg, fg, box):
    if fg.mode == 'RGBA': bg.paste(fg, box, fg.split()[3])
    else: bg.paste(fg, box)

# --- Draw Header & Panels ---
try:
    logo = Image.open('logo.png').resize((70, 70)); paste_transparent(image, logo, (50, 25))
except FileNotFoundError: print("Warning: logo.png not found.")
draw.rounded_rectangle((140, 30, 630, 90), radius=10, fill=BG_COLOR, outline=HEADER_COLOR_DARK_BLUE, width=2)
draw.rounded_rectangle((50, 120, 630, 560), radius=20, fill=PANEL_COLOR_LIGHT_BLUE) # Large Left Panel
draw.rounded_rectangle((650, 120, 1230, 700), radius=20, fill=PANEL_COLOR_LIGHT_BLUE) # Right Panel
draw.rounded_rectangle((750, 130, 1130, 180), radius=15, fill=HEADER_COLOR_DARK_BLUE) # Course ID Box

# --- Draw Bottom Boxes (Final Layout from your screenshot) ---
draw.rounded_rectangle((60, 580, 340, 690), radius=15, fill=BG_COLOR, outline=HEADER_COLOR_DARK_BLUE, width=2) # Left "Total Present" box
draw.rounded_rectangle((350, 580, 620, 690), radius=15, fill=BG_COLOR, outline=HEADER_COLOR_DARK_BLUE, width=2) # Left "Status" box
# NEW: Centrally located Time/Date box
draw.rounded_rectangle((770, 622, 1130, 690), radius=15, fill=HEADER_COLOR_DARK_BLUE)

cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
filename = "Attendance_UI.png"
cv2.imwrite(filename, cv_image)
print(f"'{filename}' created successfully!")