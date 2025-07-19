# Face Recognition based Attendance System
This is an automated attendance system that uses a webcam to recognize students' faces.. It features easy-to-use graphical interfaces for registering new students, taking live attendance, and handling manual entries if needed. The project is designed to be fast, accurate, and a modern replacement for traditional roll-call methods.


## The Face Recognition Model     
The core of this project is the model provided by the face_recognition library, which involves a four-step pipeline:     
1. Face Detection: The system first locates all faces in an image. It uses a pre-trained Histogram of Oriented Gradients (HOG) based model, which is fast and effective for finding the coordinates (bounding box) of faces.
  
- Here's a breakdown of how it works:
   *  Gradient Calculation: The model first calculates the horizontal and vertical gradients of the image using techniques like the Sobel operator. These gradients represent the rate of change of pixel intensities, highlighting edges and texture.
   *  Orientation Binning: The image is divided into small cells (e.g., 8x8 pixels). For each cell, the gradient orientations are binned into a histogram. Each bin in the histogram accumulates the magnitudes of gradients that fall within its orientation range.
   *  lock Normalization: Cells are grouped into larger blocks (e.g., 2x2 cells per block). The histograms from the cells within a block are then normalized together to reduce the impact of lighting variations.
   * Feature Vector: The normalized histograms from all blocks are concatenated to create a long feature vector. This vector represents the HOG descriptor for the image, which can be used as input to a classifier.

<p align="center"><img width="800" height="400" alt="image" src="https://github.com/user-attachments/assets/b2ef1c64-70a3-4948-9724-7dfcb4431edc" /></p>


2. Facial Landmark Detection: After locating a face, the algorithm identifies 68 specific points (landmarks) on the face, such as the corners of the eyes, the tip of the nose, and the edges of the mouth. This step helps in aligning the face correctly before encoding.

<p align="center"><img width="465" height="422" alt="image" src="https://github.com/user-attachments/assets/2a1b849a-a9dd-47bf-964b-e5bddef3e549" /></p>

  
3. Face Encoding: This is the most critical step. The system uses a deep convolutional neural network (CNN) model to generate a unique 128-dimensional vector (a list of 128 numbers) for each face. This vector, also known as a "face embedding" or "faceprint," represents the unique features of that face. Faces of the same person will have very similar 128-d vectors.

<p align="center"><img width="623" height="231" alt="image" src="https://github.com/user-attachments/assets/a2357a57-f750-4b37-b05a-42491f4549f7" />
</p>
  
4. Matching/Comparison: To identify a new face, its 128-d encoding is compared to the encodings of all known faces. The Euclidean distance between the vectors is calculated. If the distance is below a certain tolerance threshold (typically around 0.5-0.6), the face is considered a match. The known face with the smallest distance to the unknown face is chosen as the identity.   

<p align="center"><img width="1359" height="531" alt="image" src="https://github.com/user-attachments/assets/25e629b3-66ca-445f-b6d7-14649bf28c64" /></p> 

<br>
   
## System Architecture  
The system is designed with a modular approach, as shown in the block diagram below. The data flows from camera capture to final output display.

<p align="center"><img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/d7575be3-b053-4020-a448-63550750dd1b" /></p>

<br>

## Project Folder and File Structure  
### Folders:
- Image folder/: This folder stores the official profile pictures of all registered students, which are used to train the face recognition system.  
- Manual_Images/: This folder holds the "proof-of-presence" photos that are captured whenever attendance is marked manually.  


### Program Files (.py)
- 0-Main_launcher.py: The central menu that allows you to easily run any other script in the project.  
-  1-Register_student.py: The graphical application for enrolling new students, validating their data, and saving their photo and details.  
-  2-Attendance.py: The main graphical application that uses the webcam to recognize students in real-time and automatically mark their attendance.    
-  3-Manual_attendance.py: A graphical fallback application for manually entering a student's attendance when face recognition is not possible.  
-  4-Encode_generator.py: An administrative tool that processes all student photos and creates a fast-loading Encodings.p file for the attendance system.    
-  5-Registration_ui.py: A helper script that programmatically draws and creates the background image for the student registration window.  
-  6-Attendance_ui.py: A helper script that draws and creates the background image for the main attendance window.   
-  7-Manual_ui.py: A helper script that draws and creates the background image for the manual attendance window.  


### Databases (.csv)  
-  StudentDatabase.csv: The master database containing the profile information (ID, Name, Batch, etc.) for every registered student.   
-  CourseSchedule.csv: The timetable database that lists all courses, their scheduled days, and their start/end times.  
-  Attendance.csv: The primary log file where all attendance records marked automatically via face recognition are stored.  
-  manual_attendance.csv: A separate log file for storing all attendance records that were entered using the manual attendance application.  


### Picture Files  
-  logo.png: The custom logo image that is embedded into each of the user interface backgrounds.  
-  Registration_UI.png, Attendance_UI.png, Manual_Attendance_UI.png: These are the final background images generated by the UI scripts, which are loaded by the main applications to create the graphical interface.  

<br>
     
## Results and Snapshots  
The system was tested with 50 individuals in the database. It was able to successfully recognize them in real-time under normal lighting conditions.  

<p align="center"><img width="1895" height="1098" alt="image" src="https://github.com/user-attachments/assets/9a4e27be-cd76-40e8-89ab-2b6f6526e666" /></p>    
<p align="center"><em>Figure 1: A screenshot of Main Launcher</em></p>
   
<p align="center"><img width="1895" height="1098" alt="image" src="https://github.com/user-attachments/assets/6972ed7e-838a-4ab5-a4c8-682a5061718d" /></p>   
<p align="center"><em>Figure 2: A screenshot of Register New Student</em></p>

<p align="center"><img width="1895" height="1098" alt="image" src="https://github.com/user-attachments/assets/46809399-1242-4a0d-9edd-f1191fa0e670" /></p>      
<p align="center"><em>Figure 3: A screenshot of Attendance System</em></p 

<div align="center"><img width="1895" height="1098" alt="image" src="https://github.com/user-attachments/assets/a5fd9732-da9f-45d8-868a-49eabd8f7ff4" /></div>

<p align="center"><em>Figure 4: A screenshot of Manual Attendance</em></p>
      
<p align="center"><img width="1895" height="1098" alt="image" src="https://github.com/user-attachments/assets/626a607a-0379-4820-a838-17e8c7678411" /></p>        
<p align="center"><em>Figure 5: A screenshot of Encode Generator</em></p>

---
📌 **Spoofing Detection System**  
This project includes a basic anti-spoofing mechanism designed to prevent fraudulent attendance.    
It attempts to differentiate between a real, live face and a static photo or video by analyzing natural movements such as eye blinks and head motion. These checks help ensure that attendance is marked only for genuine, live participants.  

📸 **Image Usage Disclaimer**  
Celebrity images are used solely for Educational testing; no copyright is claimed or infringement intended.     
   
🔒 The contents of this repository are for viewing and inspiration only. Reuse, reproduction, or redistribution is not allowed without permission.  

   












































