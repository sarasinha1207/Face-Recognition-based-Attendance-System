# 7-Manual_ui.py
import numpy as np
import cv2
from PIL import Image, ImageDraw

print("Generating New Manual Attendance UI Background...")

# --- Color Palette & Dimensions ---
BG_COLOR, PANEL_COLOR_LIGHT_BLUE = (248, 249, 250), (233, 244, 248)
HEADER_COLOR_DARK_BLUE, ACCENT_COLOR_BLUE = (8, 94, 125), (8, 94, 125)
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
draw.rounded_rectangle((170, 30, 650, 110), radius=10, fill=HEADER_COLOR_DARK_BLUE)
draw.rounded_rectangle((50, 140, 650, 700), radius=10, fill=PANEL_COLOR_LIGHT_BLUE)
draw.rounded_rectangle((670, 140, 1230, 700), radius=10, fill=PANEL_COLOR_LIGHT_BLUE)

# --- Draw boxes inside the right panel (New Layout) ---
draw.rounded_rectangle((770, 160, 1110, 210), radius=10, fill=ACCENT_COLOR_BLUE) # Top Course ID box
draw.rounded_rectangle((690, 220, 1210, 310), radius=10, fill=HEADER_COLOR_DARK_BLUE) # Instruction box
draw.rounded_rectangle((690, 320, 1210, 610), radius=10, fill=HEADER_COLOR_DARK_BLUE) # Data entry box
draw.rounded_rectangle((790, 620, 1110, 690), radius=10, fill=HEADER_COLOR_DARK_BLUE) # Time/Date box

cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
filename = "Manual_Attendance_UI.png"
cv2.imwrite(filename, cv_image)
print(f"'{filename}' created successfully!")
