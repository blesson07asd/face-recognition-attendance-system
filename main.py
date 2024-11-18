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
load_dotenv()

cred = credentials.Certificate(r"D:\Face Recognition\face-recognition-5c6d6-firebase-adminsdk-7r19p-9cdaff4583.json")
firebase_admin.initialize_app(cred,{
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_URL")
})

bucket = storage.bucket()

cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgbackground=cv2.imread(r'Resources/background.png')

folderModePath='Resources/modes'
modePathList=os.listdir(folderModePath)
imgModeList=[]

studentInfo=None

modetype=0
counter=-1

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

with open('EncodedImages.p','rb') as f:
    encodedListKnownWithIds=pickle.load(f)

encodedListKnownWithIds, studentIds=encodedListKnownWithIds

while True:
    success,img=cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(imgS)
    encodings = face_recognition.face_encodings(imgS, face_locations)

    # imgbackground[162:162 + 480, 55:55 + 640] = img_resized
    imgbackground[162:162 + 480, 55:55 + 640] = img
    imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

    if face_locations:
        for encoding, location in zip(encodings, face_locations):

            matches=face_recognition.compare_faces(encodedListKnownWithIds,encoding)
            distance=face_recognition.face_distance(encodedListKnownWithIds,encoding)

            matchIndex=np.argmin(distance)

            if matches[matchIndex]:

                y1, x2, y2, x1 = location
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                bbox=55+x1,162+y1,x2-x1,y2-y1
                imgbackground=cvzone.cornerRect(imgbackground,bbox=bbox,rt=0)
                id=studentIds[matchIndex]

                if counter==0:
                    cvzone.putTextRect(imgbackground,'Loading...',(275,400))
                    cv2.imshow("Face Attendance",imgbackground)
                    cv2.waitKey(1)
                    counter=1
                    modetype=1

        if counter!=0:
            if counter==1:
                studentInfo=db.reference(f'Students/{id}').get()
                blob=bucket.get_blob(f'Images/{id}.jpg')
                array=np.frombuffer(blob.download_as_string(),dtype=np.uint8)
                studentImage=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                studentImage=cv2.resize(studentImage,(216,216))

                attendanceTime=datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                secondsElapsed=(datetime.now()-attendanceTime).total_seconds()

                if secondsElapsed>30:
                    ref=db.reference(f'Students/{id}')
                    studentInfo['total_attendance']+=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modetype=3
                    counter=0
                    imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]


            if 10<counter<=20:
                modetype=2

            imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

            if modetype!=3:
                if counter<=10:
                    if studentInfo:
                        cv2.putText(imgbackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgbackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgbackground, str(id), (1006,493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgbackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgbackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgbackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w,h),_=cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset=(414-w)//2

                        cv2.putText(imgbackground, str(studentInfo['name']), (808+offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        imgbackground[175:175+216,909:909+216]=studentImage

                counter+=1

                if counter>20:
                    counter=0
                    studentInfo=None
                    modetype=0
                    studentImage=None
                    imgbackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

    else:
        modetype=0
        counter=0

    cv2.imshow("Face Attendance",imgbackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
