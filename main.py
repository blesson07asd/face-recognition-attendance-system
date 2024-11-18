import pickle
import cv2
import cvzone
import os
import numpy as np
from datetime import datetime
import face_recognition

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK with credentials and environment variables
cred = credentials.Certificate(r"D:\Face Recognition\face-recognition-5c6d6-firebase-adminsdk-7r19p-9cdaff4583.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_URL")
})

# Firebase storage reference
bucket = storage.bucket()

# Initialize webcam capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set video width
cap.set(4, 480)  # Set video height

# Load background image
imgbackground = cv2.imread(r'Resources/background.png')

# Path for modes images
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

studentInfo = None  # Store student information
modetype = 0  # Mode type for different states (idle, attendance, etc.)
counter = -1  # Counter to track frame updates

# Load mode images (idle, attendance, etc.)
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoded images and their corresponding IDs
try:
    with open('EncodedImages.p', 'rb') as f:
        encodedListKnownWithIds = pickle.load(f)
    encodedListKnownWithIds, studentIds = encodedListKnownWithIds
except Exception as e:
    print(f"Error loading encoded images: {e}")
    encodedListKnownWithIds, studentIds = [], []

# Main loop to capture video and process each frame
while True:
    success, img = cap.read()  # Capture a frame
    if not success:
        print("Failed to capture image")
        break

    # Resize and convert to RGB for face recognition
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect face locations and encode them
    face_locations = face_recognition.face_locations(imgS)
    encodings = face_recognition.face_encodings(imgS, face_locations)

    # Update background image with the webcam feed
    imgbackground[162:162 + 480, 55:55 + 640] = img
    imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

    if face_locations:
        for encoding, location in zip(encodings, face_locations):
            try:
                # Compare detected face with known faces
                matches = face_recognition.compare_faces(encodedListKnownWithIds, encoding)
                distance = face_recognition.face_distance(encodedListKnownWithIds, encoding)

                matchIndex = np.argmin(distance)

                if matches[matchIndex]:  # If face matches
                    y1, x2, y2, x1 = location
                    # Scale back to original image size
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgbackground = cvzone.cornerRect(imgbackground, bbox=bbox, rt=0)
                    id = studentIds[matchIndex]

                    # Transition to loading state when a face is recognized
                    if counter == 0:
                        cvzone.putTextRect(imgbackground, 'Loading...', (275, 400))
                        cv2.imshow("Face Attendance", imgbackground)
                        cv2.waitKey(1)
                        counter = 1
                        modetype = 1

            except Exception as e:
                print(f"Error during face recognition processing: {e}")

        # If face recognized, load student data and process attendance
        if counter != 0:
            try:
                if counter == 1:
                    studentInfo = db.reference(f'Students/{id}').get()
                    blob = bucket.get_blob(f'Images/{id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), dtype=np.uint8)
                    studentImage = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    studentImage = cv2.resize(studentImage, (216, 216))

                    # Calculate time elapsed since last attendance
                    attendanceTime = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - attendanceTime).total_seconds()

                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modetype = 3
                        counter = 0
                        imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

                if 10 < counter <= 20:
                    modetype = 2

                imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

                # Display student information on the background
                if modetype != 3:
                    if counter <= 10:
                        if studentInfo:
                            # Display attendance and student details
                            cv2.putText(imgbackground, str(studentInfo['total_attendance']), (861, 125),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                            cv2.putText(imgbackground, str(studentInfo['major']), (1006, 550),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgbackground, str(id), (1006, 493),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgbackground, str(studentInfo['standing']), (910, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgbackground, str(studentInfo['year']), (1025, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgbackground, str(studentInfo['starting_year']), (1125, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                            # Display student name with centering
                            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(imgbackground, str(studentInfo['name']), (808 + offset, 445),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                            # Display student image
                            imgbackground[175:175 + 216, 909:909 + 216] = studentImage

                    counter += 1

                # Reset after processing attendance
                if counter > 20:
                    counter = 0
                    studentInfo = None
                    modetype = 0
                    studentImage = None
                    imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

            except Exception as e:
                print(f"Error processing student data: {e}")

    else:
        # If no face is detected, reset to initial state
        modetype = 0
        counter = 0

    # Display the final image with all overlays
    cv2.imshow("Face Attendance", imgbackground)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break