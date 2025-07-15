# 2-Attendance.py 
import cv2
import numpy as np
import face_recognition
import os
import subprocess
from datetime import datetime, timedelta
import csv
from PIL import Image, ImageDraw, ImageFont
import pickle

# --- Configuration & Setup (Unchanged) ---
try:
    background_img = cv2.imread('Attendance_UI.png') 
    if background_img is None: raise FileNotFoundError
except FileNotFoundError:
    print("Error: Attendance_UI.png not found. Please run '6-Attendance_ui.py' first.")
    background_img = np.zeros((720, 1280, 3), np.uint8)

path, student_database_path, attendance_file_path, manual_attendance_file_path, schedule_file_path, ENCODING_FILE = 'Images', 'StudentDatabase.csv', 'Attendance.csv', 'manual_attendance.csv', 'CourseSchedule.csv', 'Encodings.p'
current_mode, status_message, status_color = "SEARCHING", "", (40, 40, 40)
status_display_end_time, active_student_info = None, None

# --- Button Coordinates and State Flags ---
manual_button_coords = [795, 575, 965, 610]
quit_button_coords = [980, 575, 1130, 610]

manual_button_clicked = False
quit_button_clicked = False

# --- Mouse Click Handler ---
def handle_mouse_click(event, x, y, flags, param):
    global manual_button_clicked, quit_button_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        if manual_button_coords[0] <= x <= manual_button_coords[2] and manual_button_coords[1] <= y <= manual_button_coords[3]:
            print("Manual Attendance button clicked.")
            manual_button_clicked = True
        
        if quit_button_coords[0] <= x <= quit_button_coords[2] and quit_button_coords[1] <= y <= quit_button_coords[3]:
            print("Quit button clicked.")
            quit_button_clicked = True

# --- All Helper Functions are unchanged and correct ---
def draw_text(image, text, position, font_path, font_size, color):
    try: font = ImageFont.truetype(font_path, font_size)
    except IOError: font = ImageFont.load_default()
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def load_student_data():
    student_info = {};
    try:
        with open(student_database_path, 'r') as f: reader = csv.DictReader(f); [student_info.update({row['ID']: row}) for row in reader]
    except: pass
    return student_info

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

def count_present_students(course_info):
    if not course_info: return 0
    now = datetime.now(); today_str_check = now.strftime('%Y-%m-%d')
    code_only = course_info['CourseCode'].split(':')[0]
    present_ids = set()
    try:
        with open(attendance_file_path, 'r') as f:
            for line in f:
                if line.startswith('-----'): continue
                parts = line.strip().split(',')
                if len(parts) == 4 and parts[2] == code_only:
                    if datetime.strptime(parts[3], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') == today_str_check:
                        present_ids.add(parts[0])
    except FileNotFoundError: pass
    try:
        with open(manual_attendance_file_path, 'r') as f:
            today_str_header = now.strftime('%d-%B-%Y')
            start_time = datetime.strptime(course_info['StartTime'], '%H:%M').strftime('%I:%M %p')
            end_time = datetime.strptime(course_info['EndTime'], '%H:%M').strftime('%I:%M %p')
            session_header = f"-----" + today_str_header + f"-----{course_info['CourseCode']}------{start_time} - {end_time}---(manual entry)----"
            in_correct_session = False
            for line in f:
                stripped_line = line.strip()
                if stripped_line == session_header: in_correct_session = True; continue
                if stripped_line.startswith('-----'): in_correct_session = False; continue
                if in_correct_session:
                    parts = stripped_line.split(',');
                    if len(parts) >= 1: present_ids.add(parts[0])
    except FileNotFoundError: pass
    return len(present_ids)

def mark_attendance(student_id, name, course_info):
    if not course_info: return "No Active Class"
    now = datetime.now(); today_str_header = now.strftime('%d-%B-%Y'); today_str_check = now.strftime('%Y-%m-%d')
    full_course_id = course_info['CourseCode']; code_only = full_course_id.split(':')[0]
    start_time = datetime.strptime(course_info['StartTime'], '%H:%M').strftime('%I:%M %p')
    end_time = datetime.strptime(course_info['EndTime'], '%H:%M').strftime('%I:%M %p')
    session_header = f"----------" + today_str_header + f"-----------{full_course_id}-----------{start_time} - {end_time}-----------"
    header_exists, already_marked_today = False, False
    try:
        with open(attendance_file_path, 'r', newline='') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line == session_header: header_exists = True
                if stripped_line.startswith(student_id + ','):
                    parts = stripped_line.split(',')
                    if len(parts) == 4 and parts[2] == code_only:
                        if datetime.strptime(parts[3], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') == today_str_check:
                            already_marked_today = True; break
    except FileNotFoundError: pass
    if already_marked_today: return "Already Marked"
    else:
        with open(attendance_file_path, 'a', newline='') as f:
            if not header_exists: f.write(f"\n{session_header}\n")
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{student_id},{name},{code_only},{dt_string}\n")
        return "Marked"

# --- Main Program Initialization ---
print("Loading data..."); student_data = load_student_data()
course_schedule = load_course_schedule()
print("Loading face encodings...");
try:
    with open(ENCODING_FILE, 'rb') as f: known_encodings, student_ids = pickle.load(f)
    print(f"Encodings for {len(student_ids)} students loaded successfully.")
except FileNotFoundError:
    print(f"\n[ERROR] Encoding file '{ENCODING_FILE}' not found. Please run 'encode_generator.py' first."); exit()

print("System ready.")
cap = cv2.VideoCapture(0); cap.set(3, 640); cap.set(4, 480)

frame_counter = 0
face_locations = []
face_matches = [] 

cv2.namedWindow("Attendance System")
cv2.setMouseCallback("Attendance System", handle_mouse_click)

# --- Main Application Loop ---
while True:
    success, img = cap.read()
    if not success: 
        print("Failed to grab frame from camera. Exiting.")
        break
    
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    
    if frame_counter % 5 == 0:
        face_locations = face_recognition.face_locations(img_small)
        face_encodings = face_recognition.face_encodings(img_small, face_locations)
        face_matches = [face_recognition.compare_faces(known_encodings, encode, tolerance=0.5) for encode in face_encodings]

        if current_mode == "SEARCHING" and face_locations:
            first_match_found = False
            for i, matches in enumerate(face_matches):
                if True in matches:
                    student_id = student_ids[matches.index(True)]
                    info = student_data.get(student_id)
                    if info:
                        active_course_info = get_active_course(course_schedule)
                        status_message = mark_attendance(info['ID'], info['Name'], active_course_info)
                        active_student_info = info
                        current_mode = "SHOW_STATUS"
                        status_display_end_time = datetime.now() + timedelta(seconds=5)
                        first_match_found = True
                        break 
            
            if not first_match_found:
                status_message = "Not Recognized"
                active_student_info = None
                current_mode = "SHOW_STATUS"
                status_display_end_time = datetime.now() + timedelta(seconds=5)
                
    frame_counter += 1

    ui_frame = background_img.copy()
    now = datetime.now()
    active_course_info = get_active_course(course_schedule)
    
    course_text = active_course_info['CourseCode'] if active_course_info else "---"
    total_present = count_present_students(active_course_info)
    ui_frame = draw_text(ui_frame, "ATTENDANCE SYSTEM", (160, 42), "arialbd.ttf", 32, (40,40,40))
    ui_frame = draw_text(ui_frame, f"Course ID: {course_text}", (770, 100), "arialbd.ttf", 24, (255, 255, 255))
    ui_frame = draw_text(ui_frame, str(total_present), (70, 605), "arialbd.ttf", 60, (40, 40, 40))
    ui_frame = draw_text(ui_frame, "Total students present\ntoday for this course", (130, 615), "arial.ttf", 20, (40, 40, 40))
    date_day_str = f"Date: {now.strftime('%d-%b-%Y')} ({now.strftime('%A')})"
    ui_frame = draw_text(ui_frame, f"Time: {now.strftime('%I:%M:%S %p')}", (815, 630), "arialbd.ttf", 22, (255, 255, 255))
    ui_frame = draw_text(ui_frame, date_day_str, (815, 655), "arialbd.ttf", 22, (255, 255, 255))

    cv2.rectangle(ui_frame, (manual_button_coords[0], manual_button_coords[1]), (manual_button_coords[2], manual_button_coords[3]), (255, 195, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Manual Entry", (manual_button_coords[0] + 10, manual_button_coords[1] + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.rectangle(ui_frame, (quit_button_coords[0], quit_button_coords[1]), (quit_button_coords[2], quit_button_coords[3]), (200, 0, 0), cv2.FILLED)
    cv2.putText(ui_frame, "Quit", (quit_button_coords[0] + 50, quit_button_coords[1] + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    for face_loc, matches in zip(face_locations, face_matches):
        box_color = (0, 0, 255) 
        if True in matches:
            box_color = (0, 255, 0)
        y1, x2, y2, x1 = face_loc; y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 3)

    if current_mode == "SHOW_STATUS":
        if active_student_info:
            info = active_student_info
            profile_pic_path = os.path.join(path, f"{info['ID']}.png")
            if os.path.exists(profile_pic_path):
                profile_pic = cv2.resize(cv2.imread(profile_pic_path), (300, 300))
                ui_frame[170:470, 790:1090] = profile_pic
            
            ui_frame = draw_text(ui_frame, f"Student ID: {info['ID']}", (700, 480), "arial.ttf", 20, (40,40,40))
            ui_frame = draw_text(ui_frame, f"Name: {info['Name']}", (700, 500), "arial.ttf", 20, (40,40,40))
            ui_frame = draw_text(ui_frame, f"Semester: {info.get('Semester', 'N/A')}", (700, 520), "arial.ttf", 20, (40,40,40))
            ui_frame = draw_text(ui_frame, f"Batch: {info.get('Batch', 'N/A')}", (700, 540), "arial.ttf", 20, (40,40,40))

        if status_message == "Marked": status_color = (0, 150, 0)
        elif status_message == "Already Marked": status_color = (200, 150, 0)
        else: status_color = (200, 0, 0)

        ui_frame = draw_text(ui_frame, "Status:", (370, 605), "arialbd.ttf", 20, (40,40,40))
        ui_frame = draw_text(ui_frame, status_message, (370, 635), "arialbd.ttf", 24, status_color)
        
        if status_display_end_time and now > status_display_end_time:
            current_mode = "SEARCHING"; active_student_info = None

    img_resized = cv2.resize(img, (560, 420))
    ui_frame[130:550, 60:620] = img_resized
    
    cv2.imshow("Attendance System", ui_frame)

    cv2.waitKey(1)

    # --- UPDATED GRACEFUL EXIT LOGIC ---
    # Check if the 'Quit' button was clicked
    if quit_button_clicked:
        break
    
    # Check if the 'Manual Attendance' button was clicked
    if manual_button_clicked:
        break

    # Check if the window's 'X' button was clicked
    # This is the standard way to check for a closed window in OpenCV
    if cv2.getWindowProperty("Attendance System", cv2.WND_PROP_VISIBLE) < 1:
        # If the window is closed, ensure the manual attendance script is NOT triggered
        manual_button_clicked = False 
        break

# --- Final Actions ---
print("Closing application...")
cap.release()
cv2.destroyAllWindows()

# Only open manual attendance if that specific button was the reason for exiting
if manual_button_clicked:
    print("Opening manual attendance entry...")
    subprocess.run(["python", "3-Manual_attendance.py"])
    print("Exiting.")
