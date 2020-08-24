# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:37:23 2020

@author: Joshua Cayetano-Emond
"""
import os
import math
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
import time

def analyze_file(filepath):
    """

    Parameters
    ----------
    filepath : STRING
        PATH TO THE FILE ANALYZED.

    Returns
    -------
    A dictionary of the analyzed data.

    """
    data = {}
    data["filename"] = filepath
    
    # open file and count number of lines to initialize the array
    inFile = open(filepath, 'r')
    lineCount = len(inFile.readlines())
    data["linecount"] = lineCount
    fileContents = np.empty([lineCount,10])
    inFile.seek(0)
    
    # read the file data into a numpy array
    i = 0
    for line in inFile.readlines():
        lineTimeRaw = line.split(' ')[0].split('_')
        seconds, milli = lineTimeRaw[-1].split('.')
        lineTimeRaw[-1] = seconds
        lineTimeRaw.append(milli)
        lineTime = list(map(int, lineTimeRaw))
        lineDateTime = datetime(
            lineTime[0], lineTime[1], lineTime[2], lineTime[3], lineTime[4],
            lineTime[5], lineTime[6])
        fileContents[i,:] = [lineDateTime.timestamp()] + line.split()[1:]
        i += 1
        
    # raw data
    data["rawDateTime"] = np.array(fileContents[:,0], dtype=np.datetime64)
    data["rawIMU_mag_yaw"] = fileContents[:,1]
    data["rawIMU_mag_pitch"] = fileContents[:,2]
    data["rawIMU_mag_roll"] = fileContents[:,3]
    data["rawIMU_accel_yaw"] = fileContents[:,4]
    data["rawIMU_accel_pitch"] = fileContents[:,5]
    data["rawIMU_accel_roll"] = fileContents[:,6]
    data["rawIMU_gyro_yaw"] = fileContents[:,7]
    data["rawIMU_gyro_pitch"] = fileContents[:,8]
    data["rawIMU_gyro_roll"] = fileContents[:,9]
    
    # get time parameters for the session
    data["datetime_start"] = datetime.utcfromtimestamp(fileContents[0,0])
    data["datetime_end"] = datetime.utcfromtimestamp(fileContents[-1,0])
    data["datetime_middle"] = datetime.utcfromtimestamp(
        fileContents[math.ceil(data["linecount"]/2),0]) # for middle of session
    data["weekday"] = datetime.weekday(data["datetime_middle"]) 
    data["duration"] = fileContents[-1,0] - fileContents[0,0]
    
    
    
    return(data)


if __name__ == "__main__":
    folderName = os.path.join('c:', os.sep,'Users','newbi','OneDrive','Documents','p&g','Logging')
    fileInfo = []
    t = time.time()
    for fileName in sorted(os.listdir(folderName)): #go through each file and get its data
        if str.startswith(fileName,'IMULog'):
            fileInfo.append(analyze_file(os.path.join(folderName,fileName)))
   # print(fileInfo)
    elapsed = time.time() - t
    print(elapsed)
    
    print(fileInfo[0]["datetime_start"])
    plt.figure(0)
    plt.title('mag')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_mag_roll"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_mag_yaw"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_mag_pitch"])
    plt.legend(["pitch","roll","yaw"])
    
    plt.figure(1)
    plt.title('accel')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_roll"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_yaw"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_pitch"])
    plt.legend(["pitch","roll","yaw"])
    
    plt.figure(2)
    plt.title('gyro')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_roll"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_yaw"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_pitch"])
    plt.legend(["pitch","roll","yaw"])
    
    plt.figure(3)
    plt.title('yaw')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_yaw"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_yaw"])
    plt.legend(["accel","gyro"])
    
    plt.figure(4)
    plt.title('pitch')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_pitch"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_pitch"])
    plt.legend(["accel","gyro"])
    
    plt.figure(5)
    plt.title('roll')
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_accel_roll"])
    plt.plot(fileInfo[2]["rawDateTime"],fileInfo[2]["rawIMU_gyro_roll"])
    plt.legend(["accel","gyro"])