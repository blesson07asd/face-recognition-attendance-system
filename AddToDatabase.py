import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate(r"D:\Face Recognition\face-recognition-5c6d6-firebase-adminsdk-7r19p-9cdaff4583.json")
firebase_admin.initialize_app(cred,{
    "databaseURL": os.getenv("DATABASE_URL")
})

ref=db.reference('Students')

data={
    '1':
        {
            "name":"Elon Musk",
            "major":"robotics",
            "starting_year":2017,
            "total_attendance":6,
            "standing":"G",
            "year":4,
            "last_attendance_time":"2022-12-11 00:54:34"
        },
    '2':
        {
            "name":"Lionel Messi",
            "major":"football",
            "starting_year":2007,
            "total_attendance":10,
            "standing":"G",
            "year":10,
            "last_attendance_time":"2021-06-02 20:00:31"
        },
    '3':
        {
            "name":"Tom Cruise",
            "major":"action",
            "starting_year":1990,
            "total_attendance":10,
            "standing":"G",
            "year":6,
            "last_attendance_time":"2022-12-9 08:00:00"
        },
    '4':
        {
            "name":"Soham Mukherjee",
            "major":"AI",
            "starting_year":2020,
            "total_attendance":2,
            "standing":"G",
            "year":3,
            "last_attendance_time":"2022-12-12 00:54:34"
        }
}

for key,value in data.items():
    ref.child(key).set(value)