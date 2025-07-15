# Face-Recognition-based-Attendance-System
This is an automated attendance system that uses a webcam to recognize students' faces.. It features easy-to-use graphical interfaces for registering new students, taking live attendance, and handling manual entries if needed. The project is designed to be fast, accurate, and a modern replacement for traditional roll-call methods.


## The Face Recognition Model  
The core of this project is the model provided by the face_recognition library, which involves a four-step pipeline:  
1. Face Detection: The system first locates all faces in an image. It uses a pre-trained Histogram of Oriented Gradients (HOG) based model, which is fast and effective for finding the coordinates (bounding box) of faces.
  
Here's a breakdown of how it works:
    *  Gradient Calculation: The model first calculates the horizontal and vertical gradients of the image using techniques like the Sobel operator. These gradients represent the rate of change of pixel intensities, highlighting edges and texture.
    *  Orientation Binning: The image is divided into small cells (e.g., 8x8 pixels). For each cell, the gradient orientations are binned into a histogram. Each bin in the histogram accumulates the magnitudes of gradients that fall within its orientation range.
    *   lock Normalization: Cells are grouped into larger blocks (e.g., 2x2 cells per block). The histograms from the cells within a block are then normalized together to reduce the impact of lighting variations.
    * Feature Vector: The normalized histograms from all blocks are concatenated to create a long feature vector. This vector represents the HOG descriptor for the image, which can be used as input to a classifier.
   

2. Facial Landmark Detection: After locating a face, the algorithm identifies 68 specific points (landmarks) on the face, such as the corners of the eyes, the tip of the nose, and the edges of the mouth. This step helps in aligning the face correctly before encoding.
  
3. Face Encoding: This is the most critical step. The system uses a deep convolutional neural network (CNN) model to generate a unique 128-dimensional vector (a list of 128 numbers) for each face. This vector, also known as a "face embedding" or "faceprint," represents the unique features of that face. Faces of the same person will have very similar 128-d vectors.
  
4. Matching/Comparison: To identify a new face, its 128-d encoding is compared to the encodings of all known faces. The Euclidean distance between the vectors is calculated. If the distance is below a certain tolerance threshold (typically around 0.5-0.6), the face is considered a match. The known face with the smallest distance to the unknown face is chosen as the identity.   





















































