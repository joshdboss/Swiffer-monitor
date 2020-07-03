#!/usr/bin/env python
from datetime import datetime
from time import sleep

import io
import os
import errno
import logging
import subprocess
import itertools
import shutil

def outputs(folderName):
    """ Gives the filename to output in
    """
    for i in itertools.count(1):
        yield io.open('%s/%s.txt' %
                      (folderName,
                       datetime.now().strftime('%Y_%m_%d_%H_%M_%S')),
                      'w')

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
        
def startIMURecord(rootFolderName='/home/pi/Logging/UnprocessedIMU', saveFrequency=10):
    """ Records the data from the IMU into a new file every saveFrequency seconds
    """
    global IMURecordLoop
    IMURecordLoop = True 
    logging.info('Logging IMU data')
    folderName = yieldFolder(rootFolderName)
    for outputFile in outputs(folderName): #get name of the file and iterate forever
        sensorStream = subprocess.Popen(['timeout', '12', 'minimu9-ahrs', '--output', 'euler'], shell=False,
                                        stdout=subprocess.PIPE)
        timeStream = subprocess.Popen(['ts', '%Y_%m_%d_%H_%M_%.S'], shell=False,
                                      stdin=sensorStream.stdout, stdout=outputFile)
        loopStartTime = datetime.now()
        while ((datetime.now() - loopStartTime).seconds < saveFrequency):
            # keep writing to the file until 30 seconds have passed
            sleep(0.1)
            if not(IMURecordLoop):
                #stop recording once loop flag has been set to false
                timeStream.terminate()    
                sensorStream.terminate()
                return
        outputFile.close()
        
def stopIMURecord():
    global IMURecordLoop
    IMURecordLoop = False
    
    
def processIMU(inputRootFolder='/home/pi/Logging/UnprocessedIMU',
                 outputFolder='/home/pi/Logging/Unsent',
                 delay=5):
    """ Processes any unprocessed IMU logs in the inputRootFolder
        and outputs them in the outputFolder
    """
    logging.info('Processing IMU logs')
    sleep(delay) # hardcoded sleep function to ensure that the log has finished saving
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
        lastFileEndTime = datetime(1900,1,1,0,0,0) #variable tracking the end time of the previous file
        truncated = False #variable tracking if current file has been truncated yet
        outputFile = '%s/IMULog_%s.txt' % (outputFolder, folder)
        IMULog = io.open(outputFile, 'w')
        for fileName in sorted(os.listdir(folderName)): #add each file's content to outputFile
            if (fileName.endswith('.txt')):
                inFile = open('%s/%s' %(folderName, fileName), 'r')
                for line in inFile.readlines():
                    lineTimeRaw = line.split(' ')[0].split('_')
                    seconds, milli = lineTimeRaw[-1].split('.')
                    lineTimeRaw[-1] = seconds
                    lineTimeRaw.append(milli)
                    lineTime = list(map(int, lineTimeRaw))
                    lineDateTime = datetime(
                        lineTime[0], lineTime[1], lineTime[2], lineTime[3], lineTime[4],
                        lineTime[5], lineTime[6])
                    if (lineDateTime - lastFileEndTime).seconds > 0:
                        IMULog.write(line)
                    else:
                        break #reached part of file that overlaps previous
                    lastTimeRaw = line.split(' ')[0].split('_')
                    seconds, milli = lastTimeRaw[-1].split('.')
                    lastTimeRaw[-1] = seconds
                    lastTimeRaw.append(milli)
                    lastTime = list(map(int, lastTimeRaw))
                    lastFileEndTime = datetime(
                        lastTime[0], lastTime[1], lastTime[2], lastTime[3], lastTime[4],
                        lastTime[5], lastTime[6])
                inFile.close()
        IMULog.close()
        shutil.rmtree(folderName, ignore_errors=True) #delete the folder
    logging.info('Processed IMU logs')

IMURecordLoop = False    
#startIMURecord()
#processIMU()