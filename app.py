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

medication_slot_dict = {}
value_medication_dict = {}

@app.route("/wemos", methods=['POST'])
def get_from_wemos():
    global value_medication_dict
    global medication_slot_dict
    if request.method == 'POST':
        data = request.data
        data_list = data.split(" ")
        # i = 0
        # for val in data:
        #     value_medication_dict[medication_slot_dict[i]] = val
        #     i+=1

        elderly_user = db.child("Elderly").child("John Doe").get()

        for drug in elderly_user.each():
            slot_no = drug.val().["slot_no"]
            prev_val = drug.val().["new_val"]
            new_val = data_list[int(slot_no)]
            drug.update({"prev_val":str(prev_val), "new_val": new_val}) #updates new and prev val values

            if new_val<prev_val:
                time_array = drug.val()["Time"]
                current_time = str(datetime.datetime.now())[11:16]
                current_time = timeToInt(current_time)
                for time in time_array:
                    if time_array[time] == "False":
                        db.child("Elderly").child("John Doe").child(drug).child("didTake").update({time.key():"True"})
                    break

    return "Success"

@app.route("/")
def index():
    return "Hi"

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    if request.method=='POST':
        slot = request.form["slot"]
        medication = request.form['medication']
        #medication_slot_dict[slot] = medication
        dosage = request.form["dosage"]
        times = request.form["tags"]
        times_list = times.split(",")

        print medication
        print dosage
        print times_list

        data = {
            medication:{
                "Dosage":dosage,
                "Time":{},
                "hasTaken":{},
                "new_val": 50,
                "prev_val": 50,
                "slot_no": slot
            }
        }

        for i in range(0, len(times_list)):
            data[medication]["Time"][i] = times_list[i]
            data[medication]["hasTaken"][i] = "False"

        print data
        db.child("Elderly").child("John Doe").update(data) #update medication and dosage

    return "Success"

@app.route("/doctorprof")
def profile():
    return render_template("doctor.html")

@app.route("/success")
def success():
    return render_template("success.html")

