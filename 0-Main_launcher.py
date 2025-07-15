import tkinter as tk
from tkinter import font as tkFont, messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk
from datetime import datetime

# --- Configuration ---
SCRIPT_PATHS = {
    'register': '1-Register_student.py',
    'attendance': '2-Attendance.py',
    'manual': '3-Manual_attendance.py',
    'encode': '4-Encode_generator.py'
}
FACE_ICON_PATH = 'logo.png'

# --- Theme colors and fonts ---
class Theme:
    COLOR_BG_MAIN = "#E6F0F4"     # Very light blue background
    COLOR_BG_PANEL = "#A9D0E0"    # Lighter blue for panels
    COLOR_BORDER_OUTER = "#B0C4DE" # Light steel blue outer border
    COLOR_WIDGET = "#086A87"      # Dark teal for buttons and title
    COLOR_TEXT = "#FFFFFF"         # White text
    FONT_TITLE = ("Arial", 20, "bold")
    FONT_BUTTON = ("Arial", 14)
    FONT_CLOCK = ("Arial", 12)

# --- Main Application Class ---
class AppDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attendance System Dashboard")
        self.geometry("900x600")
        self.resizable(False, False)
        self.configure(bg=Theme.COLOR_BG_MAIN)

        self.create_widgets()
        self.update_clock()

    def create_widgets(self):
        # --- Outer border frame ---
        outer_frame = tk.Frame(self, bg=Theme.COLOR_BORDER_OUTER)
        outer_frame.place(relx=0.01, rely=0.015, relwidth=0.98, relheight=0.97)

        # --- Main content frame (inside the border) ---
        main_frame = tk.Frame(outer_frame, bg=Theme.COLOR_BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # --- Title Label ---
        title_label = tk.Label(main_frame, text="Attendance System Dashboard",
                               font=Theme.FONT_TITLE, bg=Theme.COLOR_WIDGET, fg=Theme.COLOR_TEXT,
                               padx=20, pady=10)
        title_label.place(relx=0.5, y=40, anchor="center")

        # --- Left Panel for Buttons ---
        left_panel = tk.Frame(main_frame, bg=Theme.COLOR_BG_PANEL, bd=2, relief="groove")
        left_panel.place(x=40, y=100, width=380, height=450)

        # --- Buttons inside Left Panel ---
        button_texts = [
            ("Register a new student", 'register'),
            ("Start live Attendance", 'attendance'),
            ("Mark Attendance Manually", 'manual'),
            ("Generate/Update Face encoding", 'encode')
        ]
        
        y_pos = 40
        for text, key in button_texts:
            btn = tk.Button(left_panel, text=text, font=Theme.FONT_BUTTON,
                            bg=Theme.COLOR_WIDGET, fg=Theme.COLOR_TEXT, bd=2, relief="raised",
                            command=lambda k=key: self.run_script(SCRIPT_PATHS[k]))
            btn.place(relx=0.5, y=y_pos, anchor="n", width=320, height=50)
            y_pos += 70

        # Exit Button
        btn_exit = tk.Button(left_panel, text="Exit", font=Theme.FONT_BUTTON,
                             bg=Theme.COLOR_WIDGET, fg=Theme.COLOR_TEXT, bd=2, relief="raised",
                             command=self.destroy)
        btn_exit.place(relx=0.5, y=360, anchor="n", width=320, height=50)

        # --- Right Panel for Image and Clock ---
        right_panel = tk.Frame(main_frame, bg=Theme.COLOR_BG_PANEL, bd=2, relief="groove")
        right_panel.place(x=450, y=100, width=380, height=450)

        # Image Holder
        image_holder = tk.Frame(right_panel, bg=Theme.COLOR_WIDGET, bd=2, relief="solid")
        image_holder.place(relx=0.5, rely=0.4, anchor="center", width=320, height=280)

        try:
            face_icon_pil = Image.open(FACE_ICON_PATH).resize((200, 200), Image.Resampling.LANCZOS)
            self.face_icon_tk = ImageTk.PhotoImage(face_icon_pil)
            image_label = tk.Label(image_holder, image=self.face_icon_tk, bg=Theme.COLOR_BG_PANEL)
            image_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Error loading face icon: {e}")
            error_label = tk.Label(image_holder, text="Image not found", fg="red", bg="white")
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            
        # Time/Date Box
        time_date_box = tk.Frame(right_panel, bg=Theme.COLOR_WIDGET)
        time_date_box.place(relx=0.5, rely=0.85, anchor="center", width=250, height=70)

        self.clock_label = tk.Label(time_date_box, text="", font=Theme.FONT_CLOCK,
                                    bg=Theme.COLOR_WIDGET, fg=Theme.COLOR_TEXT, justify="left")
        self.clock_label.place(relx=0.5, rely=0.5, anchor="center")

    def update_clock(self):
        """Updates the time and date display every second."""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%A, %d %B %Y")
        self.clock_label.config(text=f"Time:  {time_str}\nDate:  {date_str}")
        self.after(1000, self.update_clock)

    def run_script(self, script_name):
        """Hides the dashboard, runs a script, and shows the dashboard again."""
        if not os.path.exists(script_name):
            messagebox.showerror("File Not Found", f"The script '{script_name}' could not be found.")
            return

        print(f"\n---> Launching {script_name}...")
        self.withdraw()
        
        python_exe = sys.executable
        try:
            subprocess.run([python_exe, script_name], check=True)
        except Exception as e:
            messagebox.showerror("Script Error", f"An error occurred while running the script:\n{e}")
        finally:
            print(f"<--- {script_name} closed. Returning to dashboard.")
            self.deiconify()
            self.lift()
            self.focus_force()

# --- Run the application ---
if __name__ == "__main__":
    app = AppDashboard()
    app.mainloop()
