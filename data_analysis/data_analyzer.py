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

class session:
    _registry = []
    _durations = []
    _weekdays = []
    _hours = []
    
    def __init__(self, filepath):
        self._registry.append(self)
        
        # open file and count number of lines to initialize the array
        inFile = open(filepath, 'r')
        self.lineCount = len(inFile.readlines())
        fileContents = np.empty([self.lineCount,10])
        inFile.seek(0)
        
        # read the file data into a numpy array
        i = 0
        for line in inFile.readlines():
            lineTimeRaw = line.split()[0].split('_')
            seconds, milli = lineTimeRaw[-1].split('.')
            lineTimeRaw[-1] = seconds
            lineTimeRaw.append(milli)
            lineTime = list(map(int, lineTimeRaw))
            lineDateTime = datetime(
                lineTime[0], lineTime[1], lineTime[2], lineTime[3], lineTime[4],
                lineTime[5], lineTime[6])
            fileContents[i,:] = [lineDateTime.timestamp()] + line.split()[1:]
            i += 1
        inFile.close()
        
            # raw data
        self.rawDateTime = np.array(fileContents[:,0], dtype=np.datetime64)
        self.rawIMU_mag_yaw = fileContents[:,1]
        self.rawIMU_mag_pitch = fileContents[:,2]
        self.rawIMU_mag_roll = fileContents[:,3]
        self.rawIMU_accel_yaw = fileContents[:,4]
        self.rawIMU_accel_pitch = fileContents[:,5]
        self.rawIMU_accel_roll = fileContents[:,6]
        self.rawIMU_gyro_yaw = fileContents[:,7]
        self.rawIMU_gyro_pitch = fileContents[:,8]
        self.rawIMU_gyro_roll = fileContents[:,9]
        
        # get time parameters for the session
        self.datetime_start = datetime.utcfromtimestamp(fileContents[0,0])
        self.datetime_end = datetime.utcfromtimestamp(fileContents[-1,0])
        self.datetime_middle = datetime.utcfromtimestamp(
            fileContents[math.ceil(self.lineCount/2),0]) # for middle of session
        self._hours.append(self.datetime_middle.hour)
        self.weekday = datetime.weekday(self.datetime_middle) 
        self._weekdays.append(self.weekday)
        self.duration = fileContents[-1,0] - fileContents[0,0]
        self._durations.append(self.duration)
        

if __name__ == "__main__":
    folderName = os.path.join('c:', os.sep,'Users','newbi','OneDrive','Documents','p&g','Logging')
    t = time.time()
    for fileName in sorted(os.listdir(folderName)): #go through each file and get its data
        if str.startswith(fileName,'IMULog'):
            session(os.path.join(folderName,fileName))
    elapsed = time.time() - t
    print('Took %ss to load all files' % elapsed)
    
    fig1, ax1 = plt.subplots()
    plt.title('Day of the week histogram')
    ax1.hist(session._weekdays, bins = [i for i in range(8)], align='left', ec="k")
    xticks = [i for i in range(7)]
    xtick_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xtick_labels)
    plt.xlabel('Day of the week')
    plt.ylabel('Number of cleaning sessions')
    
    fig2, ax2 = plt.subplots()
    plt.title('Duration histogram')
    ax2.hist(session._durations, bins = 25, align='left', ec="k")
    plt.xlabel('Duration (s)')
    plt.ylabel('Number of cleaning sessions')
    
    fig3, ax3 = plt.subplots()
    plt.title('Time of day histogram')
    ax3.hist(session._hours, bins = [i for i in range(25)], align='left', ec="k")
    xticks = [2*i for i in range(12)]
    ax3.set_xticks(xticks)
    plt.xlabel('Time of day (UTC)')
    plt.ylabel('Number of cleaning sessions')
    
    
    chosen_session = session._registry[0]
    plt.figure(4)
    plt.title('Magnetometer readings')
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_mag_pitch)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_mag_roll)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_mag_yaw)
    plt.legend(["Pitch","Roll","Yaw"])
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    
    plt.figure(5)
    plt.title('Accelerometer readings')
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_accel_pitch)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_accel_roll)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_accel_yaw)
    plt.legend(["Pitch","Roll","Yaw"])
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    
    plt.figure(6)
    plt.title('Gyroscope readings')
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_gyro_pitch)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_gyro_roll)
    plt.plot(chosen_session.rawDateTime,chosen_session.rawIMU_gyro_yaw)
    plt.legend(["Pitch","Roll","Yaw"])
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    
