import io
import itertools
import picamera

def outputs():
    for i in itertools.count(1):
        yield io.open('file%01d.h264' % i, 'wb')

with picamera.PiCamera() as camera:
    camera.resolution = (640, 360)
    camera.framerate = 24
    for output in camera.record_sequence(
            outputs(), quality=20, bitrate=750000):
        while output.tell() < 1000:
            camera.wait_recording(0.1)
        if output.name == 'file9.h264':
            break