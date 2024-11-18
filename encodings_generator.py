import cv2
import numpy as np
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"D:\Face Recognition\face-recognition-5c6d6-firebase-adminsdk-7r19p-9cdaff4583.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_URL")
})

folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []

# Upload images to Firebase Storage and prepare the list of images and student IDs
for path in pathList:
    try:
        # Read image and append to list
        img = cv2.imread(os.path.join(folderPath, path))
        imgList.append(img)

        # Extract student ID from the image filename
        student_id = int(os.path.splitext(path)[0])
        studentIds.append(student_id)

        # Upload the image to Firebase Storage
        fileName = f'{folderPath}/{path}'
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
    except Exception as e:
        print(f"Error processing {path}: {e}")


def findEncodings(imagesList):
    """
    Function to encode images using face recognition.

    Args:
        imagesList (list): List of images to encode.

    Returns:
        list: List of face encodings for the input images.
    """
    encodings = []

    for img in imagesList:
        try:
            # Convert the image to RGB (required by face_recognition)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get the encoding of the face (assuming one face per image)
            encoded_img = face_recognition.face_encodings(img_rgb)[0]
            encodings.append(encoded_img)
        except Exception as e:
            print(f"Error encoding image: {e}")

    return encodings


print("Encoding Started...")

try:
    # Generate encodings for the images
    encodedListKnown = findEncodings(imgList)
    encodedListKnownWithIds = [encodedListKnown, studentIds]
    print("Encoding Completed...")

    # Save the encodings to a file
    with open("EncodedImages.p", "wb") as f:
        pickle.dump(encodedListKnownWithIds, f)
    print("File Saved!")
    print(encodedListKnown)
except Exception as e:
    print(f"Error during encoding or file saving: {e}")