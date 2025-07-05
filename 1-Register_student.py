# 1-Register_student.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
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

# --- Data types for each field ---
# These are the new, specific data types for validation
field_types = ['S_integer', 'admission_no', 'alpha_space', 'alpha_space', 'year', 'semester', 'batch']

field_index, input_text, student_details = 0, "", {}
error_message = ""
error_end_time = None

# --- Helper Functions ---
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
                if draw.textbbox((0,0), line + word, font=font)[2] <= wrap_width:
                    line += word + ' '
                else:
                    lines.append(line); line = word + ' '
            lines.append(line)
            for line in lines:
                draw.text((position[0], y_text), line.strip(), font=font, fill=color)
                bbox = draw.textbbox((0, 0), line.strip(), font=font)
                y_text += (bbox[3] - bbox[1]) + 5
    else:
        draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def count_registered_students(db_path):
    try:
        with open(db_path, 'r', newline='') as f:
            return max(0, sum(1 for row in f) - 1)
    except FileNotFoundError:
        return 0

# --- UPDATED: Data Validation Helper Function with all new rules ---
def is_valid_input(text, data_type):
    if not text: return False
    
    if data_type == 'S_integer':
        return len(text) == 4 and text[0].upper() == 'S' and text[1:].isdigit()
    
    if data_type == 'admission_no':
        return len(text) == 6 and text.isdigit()
        
    if data_type == 'year':
        return len(text) == 1 and text.isdigit() and text in "1234"
        
    if data_type == 'semester':
        valid_roman = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'}
        return text.upper() in valid_roman or (text.isdigit() and 1 <= int(text) <= 8)
        
    if data_type == 'batch':
        return len(text) == 1 and text.isalpha()

    if data_type == 'alpha_space':
        return all(char.isalpha() or char.isspace() for char in text)
        
    return True # Default case

# --- Main Program ---
cap = cv2.VideoCapture(0); cap.set(3, 640); cap.set(4, 480)

while True:
    success, img = cap.read()
    if not success: break
    
    ui_frame = background_img.copy()
    now = datetime.now()
    
    # --- Drawing Logic ---
    ui_frame = draw_text(ui_frame, "Registering new student", (190, 50), "arialbd.ttf", 36, (255, 255, 255))
    ui_frame = draw_text(ui_frame, f"Time: {now.strftime('%I:%M:%S %p')}", (830, 625), "arialbd.ttf", 20, (255, 255, 255))
    date_day_str = f"Date: {now.strftime('%d-%b-%Y')} ({now.strftime('%A')})"
    ui_frame = draw_text(ui_frame, date_day_str, (830, 650), "arialbd.ttf", 20, (255, 255, 255))
    total_students = count_registered_students(student_database_path)
    ui_frame = draw_text(ui_frame, str(total_students), (80, 635), "arialbd.ttf", 40, (40, 40, 40))
    ui_frame = draw_text(ui_frame, "Total Students Registered", (140, 645), "arial.ttf", 20, (40, 40, 40))
    ui_frame = draw_text(ui_frame, "Instruction:", (710, 170), "arialbd.ttf", 25, (255, 255, 255))
    if field_index < len(fields):
        ui_frame = draw_text(ui_frame, "1. Type the requested information.\n2. Press 'Enter' to confirm each field.", (710, 200), "arial.ttf", 18, (255, 255, 255), wrap_width=480)
    else:
        ui_frame = draw_text(ui_frame, "1. Press 's' to register and save the image.\n2. Press 'q' to quit without saving.", (710, 200), "arial.ttf", 18, (255, 255, 255), wrap_width=480)
    
    y_pos = 280
    for i, key in enumerate(db_keys):
        if key in student_details:
            detail_text = f"{fields[i]}: {student_details[key]}"
            ui_frame = draw_text(ui_frame, detail_text, (710, y_pos), "arial.ttf", 22, (255, 255, 255))
            y_pos += 35
    
    if field_index < len(fields):
        prompt = f"Enter {fields[field_index]}: {input_text}"
        ui_frame = draw_text(ui_frame, prompt, (710, y_pos), "arialbd.ttf", 24, (255, 255, 0))

    # Display validation errors
    if error_message and now < error_end_time:
        ui_frame = draw_text(ui_frame, error_message, (710, y_pos + 40), "arialbd.ttf", 20, (0, 0, 255))
    else:
        error_message = ""

    # --- Input Handling ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    
    if field_index < len(fields):
        if key == 13: # ENTER key
            current_field_type = field_types[field_index]
            if is_valid_input(input_text, current_field_type):
                student_details[db_keys[field_index]] = input_text.upper()
                field_index += 1
                input_text = ""
                error_message = ""
            else:
                # --- UPDATED: Custom error messages for each type ---
                if current_field_type == 'S_integer':
                    error_message = "Invalid ID. Format: S--- (e.g., S001)."
                elif current_field_type == 'admission_no':
                    error_message = "Invalid. Must be exactly 6 digits."
                elif current_field_type == 'year':
                    error_message = "Invalid. Must be a single digit (e.g., 1, 2)."
                elif current_field_type == 'semester':
                    error_message = "Invalid. Use Roman (I, II...) or numbers (1, 2...)."
                elif current_field_type == 'batch':
                    error_message = "Invalid. Must be a single letter (e.g., A)."
                else:
                    error_message = f"Invalid input for this field."
                error_end_time = now + timedelta(seconds=4)
        elif key == 8: # BACKSPACE
            input_text = input_text[:-1]
        elif 32 <= key <= 126: # Any printable character
            input_text += chr(key)
    else: # All fields entered, waiting for 's' to save
        if key == ord('s'):
            id_to_check = student_details.get('ID', '')
            id_exists = False
            try:
                with open(student_database_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('ID') == id_to_check:
                            id_exists = True
                            break
            except FileNotFoundError:
                pass

            if id_exists:
                ui_frame = draw_text(ui_frame, "ERROR: ID already exists!", (750, 400), "arialbd.ttf", 30, (255, 0, 0))
            else:
                if not os.path.exists(path): os.makedirs(path)
                img_name = f"{student_details['ID']}.png"
                cv2.imwrite(os.path.join(path, img_name), img)
                
                file_exists = os.path.exists(student_database_path)
                with open(student_database_path, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=db_keys)
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(student_details)
                
                ui_frame = draw_text(ui_frame, "Registration Successful!", (744, 530), "arialbd.ttf", 35, (0, 255, 0))
                ui_frame = draw_text(ui_frame, "Run encode_generator.py to update.", (710, 570), "arial.ttf", 20, (255, 255, 0))
            
            cv2.imshow("Register New Student", ui_frame)
            cv2.waitKey(3000)
            break

    # Place live camera feed
    img_resized = cv2.resize(img, (580, 470))
    ui_frame[150:620, 60:640] = img_resized
    
    cv2.imshow("Register New Student", ui_frame)

cap.release()
cv2.destroyAllWindows()