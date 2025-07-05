# 0-Main_launcher.py (Without screen clearing)
import os
import subprocess
import sys
import time

# --- Script Filenames ---
REGISTER_SCRIPT = '1-Register_student.py'
ATTENDANCE_SCRIPT = '2-Attendance.py'
MANUAL_ATTENDANCE_SCRIPT = '3-Manual_attendance.py'
ENCODE_SCRIPT = '4-Encode_generator.py'

def get_python_executable():
    """Returns the path to the python executable running this script."""
    return sys.executable

def main_menu():
    """Displays a menu and runs the selected script."""
    python_exe = get_python_executable()
    
    while True:
        # os.system('cls' if os.name == 'nt' else 'clear')

        print("\n=============================================================")
        print("          Face Recognition Attendance Project Menu             ")
        print("===============================================================")
        print(f"  1. Register a New Student")
        print(f"  2. Start Live Attendance System")
        print(f"  3. Mark Attendance Manually")
        print(f"  4. Generate/Update Face Encodings")
        print("  5. Exit")
        print("---------------------------------------------------------------")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            print(f"\n-------------> Starting Student Registration GUI ({REGISTER_SCRIPT})...")
            subprocess.run([python_exe, REGISTER_SCRIPT])
            print(f"\n<------------- Student Registration closed.")

        elif choice == '2':
            print(f"\n-------------> Starting Live Attendance System ({ATTENDANCE_SCRIPT})...")
            subprocess.run([python_exe, ATTENDANCE_SCRIPT])
            print(f"\n<------------ Live Attendance System closed.")
            
        elif choice == '3':
            print(f"\n-------------> Starting Manual Attendance GUI ({MANUAL_ATTENDANCE_SCRIPT})...")
            subprocess.run([python_exe, MANUAL_ATTENDANCE_SCRIPT])
            print(f"\n<------------ Manual Attendance closed.")
            
            
        elif choice == '4':
            print(f"\n-------------> Running Face Encoding Generator ({ENCODE_SCRIPT})...")
            subprocess.run([python_exe, ENCODE_SCRIPT])
            print(f"\n<------------ Encoding process complete.")
            
        elif choice == '5':
            print("\nExiting program. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(4) # brief pause for invalid input message

if __name__ == "__main__":
    main_menu()