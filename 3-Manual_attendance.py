# 3-Manual_attendance.py 
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import csv
import os
import face_recognition

# --- Configuration ---
try:
    background_img = cv2.imread('Manual_Attendance_UI.png')
    if background_img is None: raise FileNotFoundError
except FileNotFoundError:
    print("Error: Manual_Attendance_UI.png not found.")
    background_img = np.zeros((720, 1280, 3), np.uint8)

# --- File Paths and Initialization ---
path = 'Manual_Images'
attendance_file_path = 'manual_attendance.csv'
schedule_file_path = 'CourseSchedule.csv'
if not os.path.exists(path): os.makedirs(path)

# --- State Management ---
fields = ["Student ID", "Name", "Semester", "Batch"]
db_keys = ['ID', 'Name', 'Semester', 'Batch']
field_types = ['S_integer', 'alpha_space', 'semester', 'batch']
field_index, input_text, student_details = 0, "", {}
app_is_running = True # This will control the main loop

# --- Non-blocking message and button state ---
ui_message, ui_message_end_time, ui_message_color = "", None, (0,0,0)
should_quit_after_message = False
save_button_clicked, quit_button_clicked = False, False

# --- Button Coordinates ---
save_button_coords = [760, 575, 950, 605]
quit_button_coords = [940, 575, 1105, 605]

# --- Mouse Click Handler ---
def handle_mouse_click(event, x, y, flags, param):
    global save_button_clicked, quit_button_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        if save_button_coords[0] <= x <= save_button_coords[2] and save_button_coords[1] <= y <= save_button_coords[3]:
            save_button_clicked = True
        if quit_button_coords[0] <= x <= quit_button_coords[2] and quit_button_coords[1] <= y <= quit_button_coords[3]:
            quit_button_clicked = True

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
        with open(schedule_file_path, 'r') as f: reader = csv.DictReader(f); [schedule.append(row) for row in reader]
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
    if data_type == 'alpha_space': return all(char.isalpha() or char.isspace() for char in text) and text.strip()
    if data_type == 'semester':
        valid_roman = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'};
        return text.upper() in valid_roman or (text.isdigit() and 1 <= int(text) <= 8)
    if data_type == 'batch': return len(text) == 1 and text.isalpha()
    return True

# --- Initialize ---
course_schedule = load_course_schedule()
cap = cv2.VideoCapture(0); cap.set(3, 640); cap.set(4, 480)
cv2.namedWindow("Manual Attendance")
cv2.setMouseCallback("Manual Attendance", handle_mouse_click)

# --- Main Application Loop ---
while app_is_running:
    # --- 1. CAPTURE INPUTS AND CHECK FOR EXIT CONDITIONS ---
    success, img = cap.read()
    if not success: break
    
    # This is the ONLY waitKey call. It processes all events for 1ms.
    key = cv2.waitKey(1) & 0xFF

    # Check for exit conditions FIRST
    if quit_button_clicked:
        app_is_running = False
    if cv2.getWindowProperty("Manual Attendance", cv2.WND_PROP_VISIBLE) < 1:
        app_is_running = False

    # --- 2. UPDATE APP STATE BASED ON INPUT ---
    if not should_quit_after_message: # Don't process other inputs if we are in the final quitting message state
        # Keyboard typing
        if field_index < len(fields):
            if key == 13: # Enter
                if is_valid_input(input_text, field_types[field_index]):
                    student_details[db_keys[field_index]] = input_text.upper()
                    field_index += 1; input_text = ""
                else:
                    ui_message, ui_message_color, ui_message_end_time = "Invalid Input!", (0, 0, 255), datetime.now() + timedelta(seconds=2)
            elif key == 8: input_text = input_text[:-1]
            elif 32 <= key <= 126: input_text += chr(key)

        # Save button click
        if save_button_clicked:
            save_button_clicked = False # Consume the click
            if field_index >= len(fields):
                active_course_info = get_active_course(course_schedule)
                faces = face_recognition.face_locations(cv2.resize(img, (0, 0), None, 0.25, 0.25))
                if not active_course_info:
                    ui_message, ui_message_color, ui_message_end_time = "No active class!", (255, 0, 0), datetime.now() + timedelta(seconds=2)
                elif not faces:
                    ui_message, ui_message_color, ui_message_end_time = "No face detected!", (255, 0, 0), datetime.now() + timedelta(seconds=2)
                else:
                    # Save data and set up the non-blocking quit sequence
                    img_name = f"{student_details['ID']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    cv2.imwrite(os.path.join(path, img_name), img)
                    # ... (rest of your saving logic) ...
                    ui_message, ui_message_color, ui_message_end_time = "Saved! Quitting...", (0, 255, 0), datetime.now() + timedelta(seconds=2)
                    should_quit_after_message = True

    # Check if a timed message has expired
    if ui_message_end_time and datetime.now() > ui_message_end_time:
        ui_message_end_time = None # Clear the message
        if should_quit_after_message:
            app_is_running = False # Now, trigger the exit

    # --- 3. DRAW THE UI BASED ON CURRENT STATE ---
    ui_frame = background_img.copy()
    now = datetime.now()
    
    # Draw face box
    faces_to_draw = face_recognition.face_locations(cv2.resize(img, (0, 0), None, 0.25, 0.25))
    for (top, right, bottom, left) in faces_to_draw:
        cv2.rectangle(img, (left * 4, top * 4), (right * 4, bottom * 4), (0, 255, 0), 3)

    # Draw all static and dynamic text
    ui_frame = draw_text(ui_frame, "Manual Attendance", (190, 50), "arialbd.ttf", 36, (255, 255, 255))
    course_info = get_active_course(course_schedule)
    ui_frame = draw_text(ui_frame, f"Course ID: {course_info['CourseCode'] if course_info else 'No Active Class'}", (790, 170), "arialbd.ttf", 24, (255, 255, 255))
    ui_frame = draw_text(ui_frame, "Instruction:", (710, 230), "arialbd.ttf", 25, (255, 255, 255))
    ui_frame = draw_text(ui_frame, "Enter details then press 'Enter'." if field_index < len(fields) else "Click 'Save & Quit'.", (710, 270), "arial.ttf", 18, (255, 255, 255))
    date_day_str = f"Date: {now.strftime('%d-%b-%Y')} ({now.strftime('%A')})"
    ui_frame = draw_text(ui_frame, f"Time: {now.strftime('%I:%M:%S %p')}", (815, 630), "arialbd.ttf", 22, (255, 255, 255))
    ui_frame = draw_text(ui_frame, date_day_str, (815, 655), "arialbd.ttf", 22, (255, 255, 255))
    
    y_pos = 340
    for i, key_db in enumerate(db_keys):
        if key_db in student_details:
            ui_frame = draw_text(ui_frame, f"{fields[i]}: {student_details[key_db]}", (710, y_pos), "arial.ttf", 22, (255, 255, 255)); y_pos += 35
    if field_index < len(fields):
        ui_frame = draw_text(ui_frame, f"Enter {fields[field_index]}: {input_text}", (710, y_pos), "arialbd.ttf", 24, (255, 255, 0))

    # Draw the timed message if its timer is active
    if ui_message_end_time and now < ui_message_end_time:
        ui_frame = draw_text(ui_frame, ui_message, (710, y_pos + 40), "arialbd.ttf", 25, ui_message_color)

    # Draw buttons
    cv2.rectangle(ui_frame, (save_button_coords[0], save_button_coords[1]), (save_button_coords[2], save_button_coords[3]), (0, 200, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Save & Quit", (save_button_coords[0] + 20, save_button_coords[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(ui_frame, (quit_button_coords[0], quit_button_coords[1]), (quit_button_coords[2], quit_button_coords[3]), (200, 0, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Quit & Exit", (quit_button_coords[0] + 20, quit_button_coords[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Place camera feed and display final frame
    img_resized = cv2.resize(img, (580, 520))
    ui_frame[150:670, 60:640] = img_resized
    cv2.imshow("Manual Attendance", ui_frame)

# --- 4. CLEANUP (This is only reached when app_is_running becomes False) ---
print("Closing manual attendance window.")
cap.release()
cv2.destroyAllWindows()
