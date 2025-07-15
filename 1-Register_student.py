# 1-Register_student.py (Corrected with Full Message Position Control)
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import face_recognition
from datetime import datetime, timedelta
import csv
import os

# --- Configuration ---
try:
    background_img = cv2.imread('Registration_UI.png')
    if background_img is None: raise FileNotFoundError
except FileNotFoundError:
    print("Error: Registration_UI.png not found.")
    background_img = np.zeros((720, 1280, 3), np.uint8)

# --- File Paths & State Management ---
path = 'Images'
student_database_path = 'StudentDatabase.csv'
fields = ["Student ID", "Admission No.", "Name", "Degree", "Year of studying", "Semester", "Batch"]
db_keys = ['ID', 'AdmissionNo', 'Name', 'Degree', 'Year', 'Semester', 'Batch']
field_types = ['S_integer', 'admission_no', 'alpha_space', 'alpha_space', 'year', 'semester', 'batch']

field_index, input_text, student_details = 0, "", {}
app_is_running = True # Main loop controller

# --- Non-blocking message and button state (CORRECTED INITIALIZATION) ---
ui_message, ui_message_end_time, ui_message_color = "", None, (0,0,0)
ui_message_x_pos = 710      # Default X-position for all messages
ui_message_y_offset = 40    # Default Y-offset for all messages
should_quit_after_message = False
save_button_clicked, quit_button_clicked = False, False

# --- Button Coordinates ---
save_button_coords = [770, 570, 940, 600]
quit_button_coords = [960, 570, 1130, 600]

# --- Mouse Click Handler ---
def handle_mouse_click(event, x, y, flags, param):
    global save_button_clicked, quit_button_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        if save_button_coords[0] <= x <= save_button_coords[2] and save_button_coords[1] <= y <= save_button_coords[3]:
            save_button_clicked = True
        if quit_button_coords[0] <= x <= quit_button_coords[2] and quit_button_coords[1] <= y <= quit_button_coords[3]:
            quit_button_clicked = True

# --- Helper Functions (Unchanged) ---
def draw_text(image, text, position, font_path, font_size, color, wrap_width=0):
    try: font = ImageFont.truetype(font_path, font_size)
    except IOError: font = ImageFont.load_default()
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    if wrap_width > 0:
        y_text = position[1]
        for main_line in text.split('\n'):
            lines, words, line = [], main_line.split(' '), ''
            for word in words:
                if draw.textbbox((0,0), line + word, font=font)[2] <= wrap_width: line += word + ' '
                else: lines.append(line); line = word + ' '
            lines.append(line)
            for line in lines:
                draw.text((position[0], y_text), line.strip(), font=font, fill=color)
                bbox = draw.textbbox((0, 0), line.strip(), font=font); y_text += (bbox[3] - bbox[1]) + 5
    else:
        draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def count_registered_students(db_path):
    try:
        with open(db_path, 'r', newline='') as f: return max(0, sum(1 for row in f) - 1)
    except FileNotFoundError: return 0

def is_valid_input(text, data_type):
    if not text: return False
    if data_type == 'S_integer': return len(text) == 4 and text[0].upper() == 'S' and text[1:].isdigit()
    if data_type == 'admission_no': return len(text) == 6 and text.isdigit()
    if data_type == 'year': return len(text) == 1 and text.isdigit() and text in "1234"
    if data_type == 'semester':
        valid_roman = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'}
        return text.upper() in valid_roman or (text.isdigit() and 1 <= int(text) <= 8)
    if data_type == 'batch': return len(text) == 1 and text.isalpha()
    if data_type == 'alpha_space': return all(char.isalpha() or char.isspace() for char in text) and text.strip()
    return True

# --- Main Program ---
cap = cv2.VideoCapture(0); cap.set(3, 640); cap.set(4, 480)
cv2.namedWindow("Register New Student")
cv2.setMouseCallback("Register New Student", handle_mouse_click)

while app_is_running:
    success, img = cap.read()
    if not success: break
    
    key = cv2.waitKey(1) & 0xFF

    if quit_button_clicked: app_is_running = False
    if cv2.getWindowProperty("Register New Student", cv2.WND_PROP_VISIBLE) < 1: app_is_running = False

    if not should_quit_after_message:
        if field_index < len(fields):
            if key == 13: # Enter
                if is_valid_input(input_text, field_types[field_index]):
                    student_details[db_keys[field_index]] = input_text.upper()
                    field_index += 1; input_text = ""
                else:
                    # Set default style for "Invalid Input" message
                    ui_message, ui_message_color, ui_message_end_time = "Invalid Input!", (0, 0, 255), datetime.now() + timedelta(seconds=3)
                    ui_message_x_pos = 710
                    ui_message_y_offset = 40
            elif key == 8: input_text = input_text[:-1]
            elif 32 <= key <= 126: input_text += chr(key)

        if save_button_clicked:
            save_button_clicked = False # Consume click
            if field_index >= len(fields):
                id_exists = False
                try:
                    with open(student_database_path, 'r') as f:
                        if any(row.get('ID') == student_details['ID'] for row in csv.DictReader(f)):
                            id_exists = True
                except FileNotFoundError: pass

                if id_exists:
                    # Set default style for "ID Exists" message
                    ui_message, ui_message_color, ui_message_end_time = "ERROR: ID already exists!", (0, 0, 255), datetime.now() + timedelta(seconds=3)
                    ui_message_x_pos = 710
                    ui_message_y_offset = 40
                else:
                    if not os.path.exists(path): os.makedirs(path)
                    cv2.imwrite(os.path.join(path, f"{student_details['ID']}.png"), img)
                    
                    file_exists = os.path.exists(student_database_path)
                    with open(student_database_path, 'a', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=db_keys)
                        if not file_exists: writer.writeheader()
                        writer.writerow(student_details)
                    
                    # Set CUSTOM style for "Successful Registration" message
                    ui_message = "Registration Successful! Exiting..."
                    ui_message_color = (0, 255, 0)
                    ui_message_end_time = datetime.now() + timedelta(seconds=3)
                    ui_message_x_pos = 750  # Custom X-position
                    ui_message_y_offset = 5  # Custom Y-position (smaller is higher)
                    should_quit_after_message = True

    now = datetime.now()
    if ui_message_end_time and now > ui_message_end_time:
        ui_message_end_time = None
        if should_quit_after_message:
            app_is_running = False

    # --- DRAW THE UI BASED ON CURRENT STATE ---
    ui_frame = background_img.copy()
    
    faces_to_draw = face_recognition.face_locations(cv2.resize(img, (0, 0), None, 0.25, 0.25))
    for (top, right, bottom, left) in faces_to_draw:
        cv2.rectangle(img, (left * 4, top * 4), (right * 4, bottom * 4), (0, 255, 0), 3)

    ui_frame = draw_text(ui_frame, "Register New Student", (190, 45), "arialbd.ttf", 45, (255, 255, 255))
    date_day_str = f"Date: {now.strftime('%d-%b-%Y')} ({now.strftime('%A')})"
    ui_frame = draw_text(ui_frame, f"Time: {now.strftime('%I:%M:%S %p')}", (815, 630), "arialbd.ttf", 22, (255, 255, 255))
    ui_frame = draw_text(ui_frame, date_day_str, (815, 655), "arialbd.ttf", 22, (255, 255, 255))
    
    ui_frame = draw_text(ui_frame, str(count_registered_students(student_database_path)), (80, 635), "arialbd.ttf", 40, (40, 40, 40))
    ui_frame = draw_text(ui_frame, "Total Students Registered", (140, 645), "arial.ttf", 20, (40, 40, 40))
    ui_frame = draw_text(ui_frame, "Instruction:", (710, 170), "arialbd.ttf", 25, (255, 255, 255))
    ui_frame = draw_text(ui_frame, "1. Type the requested information.\n2. Press 'Enter' to confirm each field." if field_index < len(fields) else "All details entered. Click 'Save & Exit'.", (710, 200), "arial.ttf", 18, (255, 255, 255), wrap_width=480)
    
    y_pos = 280
    for i, key in enumerate(db_keys):
        if key in student_details:
            ui_frame = draw_text(ui_frame, f"{fields[i]}: {student_details[key]}", (710, y_pos), "arial.ttf", 22, (255, 255, 255)); y_pos += 35
    
    if field_index < len(fields):
        ui_frame = draw_text(ui_frame, f"Enter {fields[field_index]}: {input_text}", (710, y_pos), "arialbd.ttf", 24, (255, 255, 0))

    if ui_message_end_time and now < ui_message_end_time:
        # --- (CORRECTED DRAWING COMMAND) ---
        message_position = (ui_message_x_pos, y_pos + ui_message_y_offset)
        ui_frame = draw_text(ui_frame, ui_message, message_position, "arialbd.ttf", 22, ui_message_color)

    # Draw buttons
    cv2.rectangle(ui_frame, (save_button_coords[0], save_button_coords[1]), (save_button_coords[2], save_button_coords[3]), (0, 200, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Save & Exit", (save_button_coords[0] + 20, save_button_coords[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(ui_frame, (quit_button_coords[0], quit_button_coords[1]), (quit_button_coords[2], quit_button_coords[3]), (200, 0, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Quit & Exit", (quit_button_coords[0] + 20, quit_button_coords[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    img_resized = cv2.resize(img, (580, 470))
    ui_frame[150:620, 60:640] = img_resized
    
    cv2.imshow("Register New Student", ui_frame)

# --- 4. CLEANUP ---
print("Closing registration window.")
cap.release()
cv2.destroyAllWindows()
