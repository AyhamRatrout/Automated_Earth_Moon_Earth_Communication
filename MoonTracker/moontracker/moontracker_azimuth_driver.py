import pigpio
import time


class MoonTrackerAzimuthDriver(object):

    def __init__(self):
        self.pi = pigpio.pi()

    def set_azimuth_position(self, azimuth, is_on):
        if is_on:
            pass