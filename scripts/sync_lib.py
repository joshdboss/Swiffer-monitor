#!/usr/bin/env python
import os
import shutil
import subprocess
import logging

def syncGDrive(skipFile='',
               inputRootFolder='/home/pi/Logging/Unsent',
               outputFolder='gdmedia:/Logging',
               sentFolder='/home/pi/Logging/Sent'):
    
    for f in sorted(os.listdir(inputRootFolder)):
        fileName = os.path.join(inputRootFolder,f)
        logging.info('Syncing %s', fileName)
        # copy the files to the google Drive
        subprocess.call(['rclone', 'copy', fileName, outputFolder], shell=False)
        # move the files to the sent directory
        if fileName != skipFile:
            try:
                shutil.move(fileName, sentFolder)
            except:
                # file already exists in sent folder for some reason
                os.remove(fileName)


if __name__ == "__main__":
    syncGDrive()