#!/usr/bin/env python
from datetime import datetime
import time
import http.client as httplib

import RPi.GPIO as gpio
import subprocess

import camera_lib
import IMU_lib
import sync_lib

import concurrent.futures
import threading
from functools import partial

import sys
sys.path.append('/usr/lib/raspiwifi/reset_device')
import reset_lib as reset_lib

def internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
    

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
    subprocess.call(['shutdown', '-h', 'now'], shell=False)    
        
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
    camera_lib.stopCameraRecord()
    IMU_lib.stopIMURecord()
    if process:
        executor.submit(IMU_lib.processIMU)
        processVidTask =  executor.submit(camera_lib.processVideo)
        processVidTask.add_done_callback(doneProcess)
            
def doneProcess(result):
    global recordLEDPin
    gpio.output(recordLEDPin,gpio.LOW)
    print("Stopped processing")
    
def syncButtonEvent(channel):
    """ Manually syncs the Pi/Resets the wifi
    """
    global syncRiseTime
    
    if gpio.input(channel):
        print("rising")
        if ((datetime.now()-syncRiseTime).seconds >= 10):
            # reset the device only if button was pressed for 10 seconds
            print("success")
            for i in range(3):
                gpio.output(syncLEDPin,gpio.HIGH)
                time.sleep(0.2)
                gpio.output(syncLEDPin,gpio.LOW)
                time.sleep(0.2)
            cleanup()
            time.sleep(5)
            reset_lib.reset_to_host_mode()
        else:
            print("Syncing")
            executor.submit(sync)
    else:
        print("falling")
        syncRiseTime = datetime.now() #time when button was pressed

def sync():
    global syncLEDPin, syncMode
    
    if not syncMode:
        if internet():
            print("Started syncing")
            gpio.output(syncLEDPin,gpio.HIGH)
            sync_lib.syncGDrive()
            gpio.output(syncLEDPin,gpio.LOW)
            print("Stopped syncing")
        else:
            print("Could not sync, no internet")
            for i in range(3):
                gpio.output(channel,gpio.HIGH)
                time.sleep(0.2)
                gpio.output(channel,gpio.LOW)
                time.sleep(0.2)

def cleanup():
    """ Function that is called whenever exiting the script
        to clean things up properly
    """
    with executor:
        if recordMode:
            stopRecord(False)
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
    
    # Set all LEDs low just in case
    gpio.output(powerLEDPin,gpio.HIGH)
    gpio.output(syncLEDPin,gpio.LOW)
    gpio.output(recordLEDPin,gpio.LOW)
    
    # Variables to put the Pi in the right mode
    powerRiseTime = datetime.now()
    syncRiseTime = datetime.now()
    recordMode = False
    syncMode = False
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    executor.submit(sync)
    
    gpio.add_event_detect(powerButtonPin, gpio.BOTH, callback=powerButtonEvent, bouncetime=300)
    gpio.add_event_detect(syncButtonPin, gpio.BOTH, callback=syncButtonEvent, bouncetime=300)
    gpio.add_event_detect(recordButtonPin, gpio.FALLING, callback=recordButtonEvent, bouncetime=5000)
    
    
    try:
        while True : pass
    except:
        cleanup()