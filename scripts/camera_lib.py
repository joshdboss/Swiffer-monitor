#!/usr/bin/env python
from picamera import PiCamera
import io
import os
import itertools
from datetime import datetime
from time import sleep
import subprocess
import shutil

def outputs(folderName):
    """ Gives the filename to output in
    """
    for i in itertools.count(1):
        yield io.open('%s/%s.h264' %
                      (folderName,
                       datetime.now().strftime('%Y_%m_%d_%H_%M_%S')),
                      'wb')
        
def yieldFolder(rootFolderName):
    directory = os.path.join(
        rootFolderName,
        datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    try:
        os.makedirs(directory)
        return directory
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise # This was not a "directory exists" error

def startCameraRecord(rootFolderName='/home/pi/Logging/UnprocessedVideo', resolutionX=640, resolutionY=360,
                 cam_framerate=10, cam_quality=20, cam_bitrate=500000, saveFrequency=10):
    """ Starts recording with the camera in a given folder
    """
    global cameraRecordLoop
    cameraRecordLoop = True
    with PiCamera() as camera:
        camera.resolution = (resolutionX, resolutionY)
        camera.framerate = cam_framerate
        camera.annotate_text_size = 20
        
        folderName = yieldFolder(rootFolderName)
        print('Recording video to %s/' % folderName)

        for output in camera.record_sequence(
            outputs(folderName), quality=cam_quality, bitrate=cam_bitrate):
            loopStartTime = datetime.now()
            while ((datetime.now() - loopStartTime).seconds < saveFrequency):
                camera.annotate_text = datetime.now().strftime('%A %Y %b %d %H:%M:%S.%f')[:-3]
                camera.wait_recording(0.1)
                if not(cameraRecordLoop):
                    return #stop filming once loop flag has been set to false
            
def stopCameraRecord():
    global cameraRecordLoop
    cameraRecordLoop = False

def processVideo(inputRootFolder='/home/pi/Logging/UnprocessedVideo',
                 outputFolder='/home/pi/Logging/Unsent',
                 cam_framerate=10,
                 delay=15):
    """ Processes any unprocessed video in the inputRootFolder
        and outputs them in the outputFolder
    """
    print('Processing videos')
    sleep(delay) # hardcoded sleep function to ensure that the video has finished saving
    # Create directories if necessary
    try:
        os.makedirs(inputRootFolder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise # This was not a "directory exists" error
    try:
        os.makedirs(outputFolder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise # This was not a "directory exists" error
    # Get the list of subdirectories
    f = []
    for (dirpath, dirnames, filenames) in os.walk(inputRootFolder):
        f.extend(dirnames)
    # Go through each subdirectory
    for folder in f:
        folderName = os.path.join(inputRootFolder,folder)
        videoListName = '%s/videoList.txt' % folderName #file that will contain list of videos
        videoList = io.open(videoListName, 'w')
        for fileName in sorted(os.listdir(folderName)): #add each video in the folder to the file
            if (fileName.endswith('.h264')):
                videoString = ("file '%s/%s'\n" % (folderName, fileName))
                videoList.write(videoString)
        videoList.close()
        outputFile = '%s/%s.mp4' % (outputFolder, folder)
        #concatenate the videos
        subprocess.call(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i',
                         videoListName, '-c', 'copy', outputFile], shell=False)
        shutil.rmtree(folderName, ignore_errors=True) #delete the folder
    print('Processed videos')
    
cameraRecordLoop = False