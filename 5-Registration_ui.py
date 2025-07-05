# 5-Registration_ui.py
import numpy as np
import cv2
from PIL import Image, ImageDraw

print("Generating Final Registration UI Background...")

# --- Color Palette ---
BG_COLOR, PANEL_COLOR_LIGHT_BLUE = (248, 249, 250), (233, 244, 248)
HEADER_COLOR_DARK_BLUE = (8, 94, 125)

# --- Dimensions ---
IMG_WIDTH, IMG_HEIGHT = 1280, 720

image = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(image)

def paste_transparent(bg, fg, box):
    if fg.mode == 'RGBA': bg.paste(fg, box, fg.split()[3])
    else: bg.paste(fg, box)

# --- Draw Header & Panels ---
try:
    logo = Image.open('logo.png').resize((100, 100)); paste_transparent(image, logo, (50, 20))
except FileNotFoundError: print("Warning: logo.png not found.")
draw.rounded_rectangle((170, 30, 700, 110), radius=20, fill=HEADER_COLOR_DARK_BLUE) # Topmost Attendance System header box
draw.rounded_rectangle((50, 140, 650, 700), radius=20, fill=PANEL_COLOR_LIGHT_BLUE) # Left large Background box
draw.rounded_rectangle((670, 140, 1230, 700), radius=20, fill=PANEL_COLOR_LIGHT_BLUE) # Right large Background box

# --- NEW: Three-box layout on the right panel ---
draw.rounded_rectangle((690, 160, 1210, 250), radius=15, fill=HEADER_COLOR_DARK_BLUE) # Top instruction box
draw.rounded_rectangle((690, 270, 1210, 600), radius=15, fill=HEADER_COLOR_DARK_BLUE) # Middle data entry box
draw.rounded_rectangle((800, 615, 1120, 685), radius=15, fill=HEADER_COLOR_DARK_BLUE) # Bottom time box

# *** ADD THIS NEW LINE TO CREATE THE STUDENT COUNT BOX ***
draw.rounded_rectangle((60, 630, 640, 690), radius=15, fill=BG_COLOR, outline=HEADER_COLOR_DARK_BLUE, width=2)

cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
filename = "Registration_UI.png"
cv2.imwrite(filename, cv_image)
print(f"'{filename}' created successfully!")