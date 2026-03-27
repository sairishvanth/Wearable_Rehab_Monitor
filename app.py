from flask import Flask, render_template, jsonify, send_file
import time, math, threading, socket
import matplotlib.pyplot as plt
from collections import deque

from imu import read, BACK_ADDR, KNEE_ADDR
from config import BACK_THRESHOLD, KNEE_THRESHOLD, LED_PIN, SMOOTH
import RPi.GPIO as GPIO
from led import back_led, knee_led, off

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

baseline_back = 0
baseline_knee = 0

smooth_back = 0
smooth_knee = 0

latest = {"back":0,"knee":0}

# ? timeline stored in RAM
timeline_back = deque(maxlen=1000)
timeline_knee = deque(maxlen=1000)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(latest)

@app.route("/report")
def report():

    if len(timeline_back) < 10:
        return "Not enough data yet"

    plt.figure()
    plt.plot(list(timeline_back), label="Back")
    plt.plot(list(timeline_knee), label="Knee")
    plt.legend()
    plt.title("Posture Report")
    plt.savefig("report.png")

    return send_file("report.png", as_attachment=True)

def calibrate():
    global baseline_back, baseline_knee

    print("Calibration Start - Stand Straight")
    GPIO.output(LED_PIN,1)

    bsum = 0
    ksum = 0

    for _ in range(150):

        ax,ay,az,_,_,_ = read(BACK_ADDR)
        bsum += math.degrees(math.acos(az/math.sqrt(ax*ax+ay*ay+az*az)))

        ax2,ay2,az2,_,_,_ = read(KNEE_ADDR)
        ksum += math.degrees(math.acos(az2/math.sqrt(ax2*ax2+ay2*ay2+az2*az2)))

        time.sleep(0.02)

    GPIO.output(LED_PIN,0)

    baseline_back = bsum/150
    baseline_knee = ksum/150

    print("Calibration Done")

def loop():
    global smooth_back, smooth_knee

    calibrate()

    ip = socket.gethostbyname(socket.gethostname())
    print("Open Dashboard -> http://"+ip+":5000")

    while True:

        ax,ay,az,_,_,_ = read(BACK_ADDR)
        raw_back = math.degrees(math.acos(az/math.sqrt(ax*ax+ay*ay+az*az))) - baseline_back

        ax2,ay2,az2,_,_,_ = read(KNEE_ADDR)
        raw_knee = math.degrees(math.acos(az2/math.sqrt(ax2*ax2+ay2*ay2+az2*az2))) - baseline_knee

        smooth_back = SMOOTH*smooth_back + (1-SMOOTH)*raw_back
        smooth_knee = SMOOTH*smooth_knee + (1-SMOOTH)*raw_knee

        latest["back"] = smooth_back
        latest["knee"] = smooth_knee

        timeline_back.append(smooth_back)
        timeline_knee.append(smooth_knee)

        print("Back:",round(smooth_back,1),"Knee:",round(smooth_knee,1))

        if abs(smooth_back) > BACK_THRESHOLD:
            back_led()
        elif abs(smooth_knee) > KNEE_THRESHOLD:
            knee_led()
        else:
            off()

        time.sleep(0.12)

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
