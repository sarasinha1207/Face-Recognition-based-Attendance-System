# 3-Manual_attendance.py (Final Version with Bounding Box)
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import csv
import os
import face_recognition # <-- Import face_recognition library

# --- Configuration ---
try:
    background_img = cv2.imread('Manual_Attendance_UI.png')
    if background_img is None: raise FileNotFoundError
except FileNotFoundError:
    print("Error: Manual_Attendance_UI.png not found.")
    background_img = np.zeros((720, 1280, 3), np.uint8)

# --- File Paths ---
path = 'Manual_Images'
attendance_file_path = 'manual_attendance.csv'
schedule_file_path = 'CourseSchedule.csv'

# --- State Management ---
fields = ["Student ID", "Name", "Semester", "Batch"]
db_keys = ['ID', 'Name', 'Semester', 'Batch']
field_types = ['S_integer', 'alpha_space', 'semester', 'batch']
field_index, input_text, student_details = 0, "", {}
error_message = ""
error_end_time = None

# --- Helper Functions (Unchanged) ---
def draw_text(image, text, position, font_path, font_size, color):
    try: font = ImageFont.truetype(font_path, font_size)
    except IOError: font = ImageFont.load_default()
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def load_course_schedule():
    schedule = []
    try:
        with open(schedule_file_path, 'r') as f:
            reader = csv.DictReader(f);
            for row in reader: schedule.append(row)
    except: pass
    return schedule

def get_active_course(schedule):
    now = datetime.now(); current_day = now.strftime('%A'); current_time = now.time()
    for course in schedule:
        if course['Day'] == current_day:
            try:
                start_time = datetime.strptime(course['StartTime'], '%H:%M').time()
                end_time = datetime.strptime(course['EndTime'], '%H:%M').time()
                if start_time <= current_time <= end_time: return course
            except: continue
    return None

def is_valid_input(text, data_type):
    if not text: return False
    if data_type == 'S_integer': return len(text) == 4 and text[0].upper() == 'S' and text[1:].isdigit()
    if data_type == 'alpha_space': return all(char.isalpha() or char.isspace() for char in text)
    if data_type == 'semester':
        valid_roman = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'};
        return text.upper() in valid_roman or (text.isdigit() and 1 <= int(text) <= 8)
    if data_type == 'batch': return len(text) == 1 and text.isalpha()
    return True

# --- Initialize Manual Database ---
if not os.path.exists(path): os.makedirs(path)

# --- Main Program ---
course_schedule = load_course_schedule()
cap = cv2.VideoCapture(0); cap.set(3, 640); cap.set(4, 480)

while True:
    success, img = cap.read()
    if not success: break
    
    ui_frame = background_img.copy()
    now = datetime.now()
    
    # --- Face Detection and Box Drawing (NEW) ---
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    faces_cur_frame = face_recognition.face_locations(img_small)
    # Since this is just for capture, we draw a green box on any face found.
    for face_loc in faces_cur_frame:
        y1, x2, y2, x1 = face_loc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3) # Green box

    # --- Draw Static & Dynamic Info (Unchanged) ---
    ui_frame = draw_text(ui_frame, "Manual Attendance", (190, 50), "arialbd.ttf", 36, (255, 255, 255))
    active_course_info = get_active_course(course_schedule)
    course_text = active_course_info['CourseCode'] if active_course_info else "No Active Class"
    ui_frame = draw_text(ui_frame, f"Course ID: {course_text}", (820, 170), "arialbd.ttf", 24, (255, 255, 255))
    ui_frame = draw_text(ui_frame, "Instruction:", (710, 240), "arialbd.ttf", 20, (255, 255, 255))
    if field_index < len(fields):
        ui_frame = draw_text(ui_frame, "Enter details then press 'Enter'.", (710, 270), "arial.ttf", 18, (255, 255, 255))
    else:
        ui_frame = draw_text(ui_frame, "1. Press 's' to mark attendance.\n2. Press 'q' to quit.", (710, 270), "arial.ttf", 18, (255, 255, 255))
    ui_frame = draw_text(ui_frame, f"Time: {now.strftime('%I:%M:%S %p')}", (820, 625), "arialbd.ttf", 20, (255, 255, 255))
    date_day_str = f"Date: {now.strftime('%d-%b-%Y')} ({now.strftime('%A')})"
    ui_frame = draw_text(ui_frame, date_day_str, (820, 650), "arialbd.ttf", 20, (255, 255, 255))

    y_pos = 370
    for i, key in enumerate(db_keys):
        if key in student_details:
            detail_text = f"{fields[i]}: {student_details[key]}"
            ui_frame = draw_text(ui_frame, detail_text, (710, y_pos), "arial.ttf", 22, (255, 255, 255)); y_pos += 35
    if field_index < len(fields):
        prompt = f"Enter {fields[field_index]}: {input_text}"
        ui_frame = draw_text(ui_frame, prompt, (710, y_pos), "arialbd.ttf", 24, (255, 255, 0))

    if error_message and now < error_end_time:
        ui_frame = draw_text(ui_frame, error_message, (710, y_pos + 40), "arialbd.ttf", 20, (0, 0, 255))
    else: error_message = ""

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    
    if field_index < len(fields):
        if key == 13:
            current_field_type = field_types[field_index]
            if is_valid_input(input_text, current_field_type):
                student_details[db_keys[field_index]] = input_text.upper()
                field_index += 1; input_text = ""
                error_message = ""
            else:
                if current_field_type == 'S_integer': error_message = "Invalid. Format: S### (e.g., S001)."
                elif current_field_type == 'semester': error_message = "Invalid. Use Roman (I, II) or numbers."
                elif current_field_type == 'batch': error_message = "Invalid. Must be a single letter."
                else: error_message = "Invalid input for this field."
                error_end_time = now + timedelta(seconds=3)
        elif key == 8: input_text = input_text[:-1]
        elif 32 <= key <= 126: input_text += chr(key)
    else:
        if key == ord('s'):
            if active_course_info:
                # --- NEW: Check if a face is detected before saving ---
                if not faces_cur_frame:
                    ui_frame = draw_text(ui_frame, "No face detected!", (710, y_pos + 40), "arialbd.ttf", 24, (0, 0, 255))
                    cv2.imshow("Manual Attendance", ui_frame)
                    cv2.waitKey(2000)
                    continue # Go to next loop iteration without saving

                img_name = f"{student_details.get('ID', 'unknown')}_{now.strftime('%Y%m%d%H%M%S')}.png"
                cv2.imwrite(os.path.join(path, img_name), img)
                
                today_str_header = now.strftime('%d-%B-%Y')
                full_course_id = active_course_info['CourseCode']
                start_time = datetime.strptime(active_course_info['StartTime'], '%H:%M').strftime('%I:%M %p')
                end_time = datetime.strptime(active_course_info['EndTime'], '%H:%M').strftime('%I:%M %p')
                session_header = f"-----{today_str_header}-----{full_course_id}------{start_time} - {end_time}---(manual entry)----"
                
                header_exists = False
                try:
                    with open(attendance_file_path, 'r', newline='') as f:
                        for line in f:
                            if line.strip() == session_header: header_exists = True; break
                except FileNotFoundError: pass

                with open(attendance_file_path, 'a', newline='') as f:
                    if not header_exists: f.write(f"\n{session_header}\n")
                    record = f"{student_details['ID']},{student_details['Name']},{student_details['Semester']},{student_details['Batch']},{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f.write(record)

                success_prompt_pos = (710, y_pos + 40)
                ui_frame = draw_text(ui_frame, "Successfully marked attendance", success_prompt_pos, "arialbd.ttf", 24, (0, 255, 0))
                cv2.imshow("Manual Attendance", ui_frame)
                cv2.waitKey(2000); break
            else:
                ui_frame = draw_text(ui_frame, "No active class to mark for!", (710, y_pos + 40), "arialbd.ttf", 22, (255, 0, 0))
                cv2.imshow("Manual Attendance", ui_frame)
                cv2.waitKey(2000)

    # Place live camera feed (with box already drawn on it)
    img_resized = cv2.resize(img, (580, 520))
    ui_frame[150:670, 60:640] = img_resized
    
    cv2.imshow("Manual Attendance", ui_frame)

cap.release()
cv2.destroyAllWindows()