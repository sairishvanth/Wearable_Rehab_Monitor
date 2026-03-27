from smbus2 import SMBus
import math
import time
import csv
from config import *
from led import *

bus = SMBus(1)

PWR = 0x6B
ACCEL = 0x3B
GYRO = 0x43

bus.write_byte_data(BACK_ADDR, PWR, 0)
bus.write_byte_data(KNEE_ADDR, PWR, 0)

prev = time.time()

def rw(addr, reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg+1)
    v = (h << 8) + l
    if v > 32767:
        v = v - 65536
    return v

def read(addr):
    ax = rw(addr, ACCEL) / 16384
    ay = rw(addr, ACCEL+2) / 16384
    az = rw(addr, ACCEL+4) / 16384
    gx = rw(addr, GYRO) / 131
    gy = rw(addr, GYRO+2) / 131
    gz = rw(addr, GYRO+4) / 131
    return ax, ay, az, gx, gy, gz

def get_angles():
    global prev

    t = time.time()
    dt = t - prev
    prev = t

    ax, ay, az, gx, gy, gz = read(BACK_ADDR)
    mag = math.sqrt(ax*ax + ay*ay + az*az)
    angle_back = math.degrees(math.acos(az / mag))

    ax2, ay2, az2, gx2, gy2, gz2 = read(KNEE_ADDR)
    mag2 = math.sqrt(ax2*ax2 + ay2*ay2 + az2*az2)
    angle_knee = math.degrees(math.acos(az2 / mag2))

    if angle_back > BACK_THRESHOLD:
        back_led()
    elif angle_knee > KNEE_THRESHOLD:
        knee_led()
    else:
        off()

    print("Back Angle:", round(angle_back,1),
          "Knee Angle:", round(angle_knee,1))

    with open("data/timeline.csv","a") as f:
        csv.writer(f).writerow([t, angle_back, angle_knee])

    return angle_back, angle_knee
