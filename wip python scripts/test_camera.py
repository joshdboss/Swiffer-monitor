from picamera import PiCamera
import io
import itertools
import datetime as dt

def outputs():
    for i in itertools.count(1):
        yield io.open('/home/pi/Desktop/film2/vid%02d.h264' % i, 'wb')

camera = PiCamera()

camera.resolution = (640, 360)
camera.framerate = 10
camera.annotate_text_size = 20

loop = True
for output in camera.record_sequence(
     outputs(), quality=20, bitrate=500000):
         loopStartTime = dt.datetime.now()
         while ((dt.datetime.now() - loopStartTime).seconds < 10):
             camera.annotate_text = dt.datetime.now().strftime('%A %d %b %Y %H:%M:%S.%f')[:-3]
             camera.wait_recording(0.1)
         if (not loop):
             break
                                     


# for filename in camera.record_sequence([
#     '/home/pi/Desktop/film2/%02d.h264' % (h +1)
#     for h in range (60)
#     ], quality=20, bitrate=500000):
#         start = dt.datetime.now()
#         while ((dt.datetime.now() - start).seconds < 10):
#             camera.annotate_text = dt.datetime.now().strftime('%A %d %b %Y %H:%M:%S.%f')[:-3]
#             camera.wait_recording(0.1)
# camera.start_recording('/home/pi/Desktop/640-10.h264')
# camera.start_preview()
# sleep(30)
# camera.stop_preview()
# camera.stop_recording()