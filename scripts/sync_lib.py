#!/usr/bin/env python
import os
import shutil
import subprocess


def syncGDrive(inputRootFolder='/home/pi/Logging/Unsent',
               outputFolder='gdmedia:/Logging',
               sentFolder='/home/pi/Logging/Sent'):
    
    files = os.listdir(inputRootFolder)
    for f in files:
        fileName = os.path.join(inputRootFolder,f)
        print("Syncing", fileName)
        # copy the files to the google Drive
        subprocess.call(['rclone', 'copy', fileName, outputFolder], shell=False)
        # move the files to the sent directory
        try:
            shutil.move(fileName, sentFolder)
        except:
            # file already exists in sent folder for some reason
            os.remove(fileName)


if __name__ == "__main__":
    syncGDrive()