#!/usr/bin/env python
from datetime import datetime
import time

import RPi.GPIO as gpio
import subprocess

import camera_lib
import IMU_lib


import concurrent.futures
import threading
from functools import partial

def powerButtonEvent(channel):
    """ Power off the raspberry Pi if the button was pressed down for long enough
    """
    global powerRiseTime
    if gpio.input(channel):
        print("rising")
        if ((datetime.now()-powerRiseTime).seconds >= 3):
            #turn off the device only if power button was pressed for 3 seconds
            print("success")
            powerOff()
    else:
        print("falling")
        powerRiseTime = datetime.now() #time when button was pressed

def powerOff():
    """ Shutdown sequence
    """
    cleanup()
    time.sleep(5)
    print('shutting down')
    #subprocess.call(['shutdown', '-h', 'now'], shell=False)    
        
def recordButtonEvent(channel):
    """ Stops/starts recording accordingly
        when button is pressed
    """ 
    global recordMode
    if recordMode:
        stopRecord(True)
    else:
        startRecord()

def startRecord():
    """ Start recording sequence
        Starts the camera and the IMU
    """
    global recordMode
    global executor
    recordMode = True
    print("Started recording")
    gpio.output(recordLEDPin,gpio.HIGH)
    executor.submit(camera_lib.startCameraRecord)
    executor.submit(IMU_lib.startIMURecord)
    
def stopRecord(process):
    """ Stops recording sequence
        Stops the camera and the IMU
    """
    global recordMode
    recordMode = False
    print("Stopped recording")
    gpio.output(recordLEDPin,gpio.LOW)
    camera_lib.stopCameraRecord()
    IMU_lib.stopIMURecord
    if process:
        executor.submit(camera_lib.processVideo)
        executor.submit(IMU_lib.processIMU)
#     x = threading.Thread(target=camera_lib.processVideo, kwargs={'delay':processDelay,})
#     x.start()
    
def syncButtonEvent(channel):
    """ Puts the Pi in sync mode (change to match with RaspiWifi eventually)
    """
    global syncMode
    if syncMode:
        stopSync()
    else:
        startSync()

def startSync():
    global syncMode
    syncMode = True
    gpio.output(syncLEDPin,gpio.HIGH)
    print("Started syncing")
    
def stopSync():
    global syncMode
    syncMode = False
    gpio.output(syncLEDPin,gpio.LOW)
    print("Stopped syncing")
    
def cleanup():
    """ Function that is called whenever exiting the script
        to clean things up properly
    """
    with executor:
        if recordMode:
            stopRecord(False)
        if syncMode:   
            stopSync()
    gpio.cleanup()

if __name__ == "__main__":
    """ Main script of the swiffer monitor.
        Runs record/sync functions according to button presses
    """
    
    # Setup all of the GPIO pins
    print('Setting up GPIO pins')
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
    print('Setup complete')
    
    # Variables to put the Pi in the right mode
    powerRiseTime = datetime.now()
    recordMode = False
    syncMode = False
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    gpio.add_event_detect(powerButtonPin, gpio.BOTH, callback=powerButtonEvent, bouncetime=300)
    gpio.add_event_detect(syncButtonPin, gpio.FALLING, callback=syncButtonEvent, bouncetime=300)
    gpio.add_event_detect(recordButtonPin, gpio.FALLING, callback=recordButtonEvent, bouncetime=5000)
    
    
    try:
        while True : pass
    except:
        cleanup()