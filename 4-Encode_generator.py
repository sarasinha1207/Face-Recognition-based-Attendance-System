# 4-Encode_generator.py (Hybrid Sync Version with Exit Option)
import cv2
import face_recognition
import pickle
import os
import csv

# --- Configuration ---
IMAGES_FOLDER = 'Images'
DATABASE_FILE = 'StudentDatabase.csv'
ENCODING_FILE = 'Encodings.p'

def get_registered_students():
    """Loads the set of all student IDs from the database CSV."""
    try:
        with open(DATABASE_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            return {row['ID'] for row in reader}
    except FileNotFoundError:
        print(f"[ERROR] Student database '{DATABASE_FILE}' not found. Cannot proceed.")
        return None

def encode_faces(student_ids_to_encode):
    """Encodes faces for a given set of student IDs."""
    encodings = []
    processed_ids = []
    for student_id in student_ids_to_encode:
        image_path = os.path.join(IMAGES_FOLDER, f"{student_id}.png")
        if os.path.exists(image_path):
            try:
                img = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(img)
                if not face_locations:
                    print(f"[Warning] No face found in {image_path} for ID {student_id}. Skipping.")
                    continue
                
                encoding = face_recognition.face_encodings(img, [face_locations[0]])[0]
                encodings.append(encoding)
                processed_ids.append(student_id)
                print(f"  - Encoded face for student ID: {student_id}")
            except Exception as e:
                print(f"[ERROR] Could not process image for student {student_id}: {e}")
        else:
            print(f"[Warning] Image not found for student ID: {student_id}. Skipping.")
    return encodings, processed_ids

def run_full_rebuild(all_student_ids):
    """Wipes and re-encodes all students from scratch."""
    print("\n--- Starting Full Re-build ---")
    print("This will re-encode all students. This is recommended if you have changed existing photos.")
    known_encodings, student_ids_for_pickle = encode_faces(all_student_ids)
    print(f"\nSuccessfully re-encoded {len(known_encodings)} faces.")
    return known_encodings, student_ids_for_pickle

def run_quick_sync(all_student_ids):
    """Loads existing encodings and only encodes new students."""
    print("\n--- Starting Quick Sync ---")
    print("This will only encode new students not already in the encodings file.")
    try:
        with open(ENCODING_FILE, 'rb') as f:
            known_encodings, existing_ids = pickle.load(f)
        print(f"Loaded {len(existing_ids)} existing encodings.")
    except FileNotFoundError:
        print("No existing encoding file found. Performing a full build instead.")
        return run_full_rebuild(all_student_ids)
        
    new_student_ids = all_student_ids - set(existing_ids)
    if not new_student_ids:
        print("No new students found to encode. Encodings are already up-to-date.")
        return None, None
    print(f"Found {len(new_student_ids)} new students to encode: {', '.join(new_student_ids)}")
    new_encodings, new_processed_ids = encode_faces(new_student_ids)
    final_encodings = known_encodings + new_encodings
    final_ids = existing_ids + new_processed_ids
    print(f"\nSuccessfully encoded {len(new_encodings)} new faces.")
    return final_encodings, final_ids

# --- Main Execution ---
if __name__ == "__main__":
    print("==============================")
    print(" Face Encoding Utility")
    print("==============================")
    
    registered_ids = get_registered_students()
    if registered_ids is None: exit()
    if not registered_ids: print("Student database is empty. Exiting."); exit()
        
    print(f"\nFound a total of {len(registered_ids)} students in your database.")
    
    # --- Interactive Menu ---
    final_encodings, final_ids = None, None # Initialize variables
    
    while True:
        print("\nChoose an encoding mode:")
        print("  1. Quick Sync (Fast: Only encodes new students)")
        print("  2. Full Re-build (Slow: Re-encodes ALL students - use if you changed photos)")
        print("  3. Exit") # <-- NEW OPTION
        print("----------------------------------------------")

        choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            final_encodings, final_ids = run_quick_sync(registered_ids)
            break # Exit the menu loop after performing the action
        elif choice == '2':
            final_encodings, final_ids = run_full_rebuild(registered_ids)
            break # Exit the menu loop
        elif choice == '3': # <-- NEW LOGIC
            print("Exiting without making changes.")
            break # Exit the menu loop
        else:
            print("Invalid choice. Please try again.")

    # --- Save the results (only if a change was made) ---
    if final_encodings is not None and final_ids is not None:
        data_to_save = [final_encodings, final_ids]
        with open(ENCODING_FILE, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"\nAll changes have been saved to '{ENCODING_FILE}'. Your system is ready.")
    else:
        print("\nNo changes were made to the encoding file.")