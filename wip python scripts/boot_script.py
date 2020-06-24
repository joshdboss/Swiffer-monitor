#!/usr/bin/env python

from datetime import datetime
import RPi.GPIO as gpio
import subprocess
from picamera import PiCamera

powerLEDPin = 5
syncLEDPin = 6
recordLEDPin = 13
powerButtonPin = 17
syncButtonPin = 27
recordButtonPin = 22
gpio.setmode(gpio.BCM)
gpio.setup(powerLEDPin,gpio.OUT) # power LED
gpio.setup(syncLEDPin,gpio.OUT) #sync LED
gpio.setup(recordLEDPin,gpio.OUT) #record LED
gpio.setup(powerButtonPin, gpio.IN, pull_up_down=gpio.PUD_UP) #power button
gpio.setup(syncButtonPin, gpio.IN, pull_up_down=gpio.PUD_UP) #sync button
gpio.setup(recordButtonPin, gpio.IN, pull_up_down=gpio.PUD_UP) #record button

powerRiseTime = datetime.now()
recordMode = False
camera = PiCamera()
syncMode = False

def powerOff(channel):
    """Power off the raspberry Pi if the button was pressed down for long enough
    """
    global powerRiseTime
    if gpio.input(channel):
        print("rising")
        if ((datetime.now()-powerRiseTime).seconds >= 3):
            #turn off the device only if power button was pressed for 3 seconds
            print("success")
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
    else:
        print("falling")
        powerRiseTime = datetime.now() #time when button was pressed

def record(channel):
    global recordMode
    if recordMode:
        recordMode = False
        print("Stopped recording")
        gpio.output(recordLEDPin,gpio.LOW)
        camera.stop_preview()
    else:
        recordMode = True
        print("Started recording")
        gpio.output(recordLEDPin,gpio.HIGH)
        camera.start_preview()
       
   
def sync(channel):
    global syncMode
    if syncMode:
        syncMode = False
        gpio.output(syncLEDPin,gpio.LOW)
        print("Stopped syncing")
    else:
        syncMode = True
        gpio.output(syncLEDPin,gpio.HIGH)
        print("Started syncing")
   
   
# ---------- listening events
gpio.add_event_detect(powerButtonPin, gpio.BOTH, callback=powerOff, bouncetime=300)
gpio.add_event_detect(syncButtonPin, gpio.FALLING, callback=sync, bouncetime=300)
gpio.add_event_detect(recordButtonPin, gpio.FALLING, callback=record, bouncetime=300)


try:
    while True : pass
except:
    gpio.cleanup()