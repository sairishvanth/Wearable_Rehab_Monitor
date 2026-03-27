import RPi.GPIO as GPIO
import time
from config import LED_PIN

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def back_led():
    GPIO.output(LED_PIN,1)
    time.sleep(0.3)
    GPIO.output(LED_PIN,0)
    time.sleep(0.3)

def knee_led():
    for i in range(2):
        GPIO.output(LED_PIN,1)
        time.sleep(0.2)
        GPIO.output(LED_PIN,0)
        time.sleep(0.2)
    time.sleep(0.5)

def off():
    GPIO.output(LED_PIN,0)