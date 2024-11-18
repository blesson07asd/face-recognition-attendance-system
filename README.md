# Face Recognition Attendance System

This project is an implementation of a **Face Recognition Attendance System** using Python, OpenCV, Firebase, and other libraries. It uses facial recognition to track and manage student attendance, storing data in a Firebase Realtime Database and using Firebase Storage to manage student images.

## Project Overview

The system:
- Captures a student's face through a webcam using OpenCV.
- Matches the captured face with pre-encoded images stored in Firebase.
- Updates the student's attendance in real-time based on face recognition.
- Uploads student images to Firebase Storage.
- Displays student information on a GUI, including their attendance count, name, major, and other details.

## Key Features
- **Face Recognition**: Identifies and matches student faces using the `face_recognition` library.
- **Firebase Integration**: Uses Firebase Realtime Database to store and update student data, including their attendance and personal details.
- **Real-time Attendance**: Updates attendance count every time a student's face is detected.
- **Student Info Display**: Displays the student’s major, year, attendance count, and other details on a GUI.
- **Image Upload to Firebase**: Uploads student images to Firebase Storage for easy retrieval.

## Technologies Used

- **Python**: Main programming language.
- **OpenCV**: For image processing and face detection.
- **face_recognition**: For facial feature recognition and comparison.
- **Firebase**: Firebase Realtime Database for storing student data and Firebase Storage for managing student images.
- **dotenv**: For loading sensitive environment variables such as Firebase credentials and database URL.
- **Pickle**: For saving and loading face encodings for fast matching.
  
## Project Setup

### Prerequisites

- Python 3.7+
- Required Python libraries (listed in requirements.txt)
- Firebase Project with Realtime Database and Storage enabled
- A service account JSON file for Firebase Admin SDK

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sohamfcb/face-recognition-attendance-system.git
   cd face-recognition-attendance-system

2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt

3. **Setup Firebase:**

  - Create a Firebase project if you haven’t already.
  - Enable Realtime Database and Firebase Storage in the Firebase console.
  - Generate a service account key from the Firebase console.
  - Save the JSON file to the project folder.

4. **Create a `.env` file: Add the following content to your `.env` file:**
   ```bash
   DATABASE_URL=<Your Firebase Realtime Database URL>
   STORAGE_URL=<Your Firebase Storage URL>

5. **Run the project:**
   ```bash
    python main.py

### File Structure
    ```bash
    ├── Images/                    # Folder containing student images
    ├── Resources/                 # Folder containing background and mode images
    │   ├── background.png         # Background image for the GUI
    │   ├── modes/                 # Folder containing mode images
    ├── EncodedImages.p            # Pickle file containing the pre-encoded student face data
    ├── main.py                    # Main script to run the system
    ├── requirements.txt           # List of required Python libraries
    ├── .env                       # Environment variables for Firebase credentials
    └── README.md                  # Project documentation

### How It Works

- **Capturing Faces:** When the system detects a student's face, it compares it with pre-encoded face data stored in `EncodedImages.p`.

- **Attendance Update:** If a match is found, the system updates the student's attendance in Firebase Realtime Database and displays their information on the GUI.

- **Firebase Database:** The student's details (name, major, year, etc.) and attendance records are stored in Firebase Realtime Database.

- **Image Storage:** Student images are uploaded to Firebase Storage for easy access and retrieval.
