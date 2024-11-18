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
load_dotenv()

cred = credentials.Certificate(r"D:\Face Recognition\face-recognition-5c6d6-firebase-adminsdk-7r19p-9cdaff4583.json")
firebase_admin.initialize_app(cred,{
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_URL")
})

folderPath='Images'
pathList=os.listdir(folderPath)
imgList=[]
studentIds=[]

for path in pathList:

    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    id=int(os.path.splitext(path)[0])
    studentIds.append(id)

    fileName=f'{folderPath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagesList):

    encodings=[]

    for img in imagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encoded_img=face_recognition.face_encodings(img)[0]
        encodings.append(encoded_img)

    return encodings

print("Encoding Started...")
encodedListKnown=findEncodings(imgList)
encodedListKnownWithIds=[encodedListKnown,studentIds]
print("Encoding Completed...")

with open("EncodedImages.p","wb") as f:
    pickle.dump(encodedListKnownWithIds,f)
    f.close()
print("File Saved!")
print(encodedListKnown)