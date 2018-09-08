import pyrebase
from flask import Flask, render_template, request
import datetime
import json

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyA6Yb4Yace3myKN3vsqb7kjZd8IE-63_AA",
    "authDomain": "sif-hackathon-2018.firebaseapp.com",
    "databaseURL": "https://sif-hackathon-2018.firebaseio.com",
    "projectId": "sif-hackathon-2018",
    "storageBucket": "sif-hackathon-2018.appspot.com",
    "messagingSenderId": "129621827056"
}

def timeToInt(time):
    (hour, minute) = time.split(':')
    current_time = int(hour+minute)
    return current_time

firebase = pyrebase.initialize_app(config)

db = firebase.database()

new_val = 150
drug = "Paracetamol"

@app.route("/wemos", methods=['POST'])
def get_from_wemos():
    global new_val
    global drug
    if request.method == 'POST':
        new_val = request.form['new_val']
        drug = request.form['drug']
        prev_val = db.child("Elderly").child("John Doe").child(drug).get()
        if new_val<prev_val:
            db.child("Elderly").child("John Doe").child(drug).update({"prev_val":str(new_val)}) #update previous value
            db.child("Elderly").child("John Doe").child(drug).update({"new_val":str(new_val)}) #update new value
            time_array = db.child("Elderly").child("John Doe").child(drug).child("Time").get()
            current_time = str(datetime.datetime.now())[11:16]
            current_time = timeToInt(current_time)
            for time in time_array.each():
                time_boolean_ref = db.child("Elderly").child("John Doe").child(drug).child("didTake").child(time.key())
                if time_boolean_ref.val() == "False":
                    db.child("Elderly").child("John Doe").child(drug).child("didTake").update({time.key():"True"})
                break

    return True

@app.route("/")
def index():
    return "Hello"

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    if request.method=='POST':
        medication = request.form['medication']
        dosage = request.form["dosage"]
        times = request.form["tags"]
        times_list = times.split(",")

        data = {
            medication:{
                "Dosage":dosage,
                "Times":{},
                "hasTaken":{}
            }
        }

        for i in range(0, len(times_list)):
            data[medication]["Times"][i] = times_list[i]
            data[medication]["hasTaken"][i] = "False"

        db.child("Elderly").child("John Doe").update(data) #update medication and dosage