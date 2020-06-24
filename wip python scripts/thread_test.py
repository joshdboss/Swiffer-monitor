import logging
import threading
import time
from picamera import PiCamera
import io
import itertools
import datetime as dt
import concurrent.futures

def outputs():
    for i in itertools.count(1):
        yield io.open('/home/pi/Desktop/film2/vid%02d.h264' % i, 'wb')

def thread_function(name):
    global loop
    with PiCamera() as camera:
        camera.resolution = (640, 360)
        camera.framerate = 10
        camera.annotate_text_size = 20

        for output in camera.record_sequence(
             outputs(), quality=20, bitrate=500000):
                 loopStartTime = dt.datetime.now()
                 while ((dt.datetime.now() - loopStartTime).seconds < 10):
                     camera.annotate_text = dt.datetime.now().strftime('%A %d %b %Y %H:%M:%S.%f')[:-3]
                     camera.wait_recording(0.1)
                 print(loop)
                 if output.name == '/home/pi/Desktop/film2/vid02.h264':
                     break

        print('broke')

if __name__ == "__main__":
    loop = True
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    logging.info("Main    : before running thread")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(thread_function, 1)
        a = 1
        print(a)
    logging.info("Main    : wait for the thread to finish")
    logging.info("Main    : all done")