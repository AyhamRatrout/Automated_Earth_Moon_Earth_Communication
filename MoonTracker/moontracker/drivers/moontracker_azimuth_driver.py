import pigpio
import time


class MoonTrackerAzimuthDriver(object):

    def __init__(self):
        self.pi = pigpio.pi()

    def set_azimuth_position(self, delta_azimuth):
        print('received an azimuth delta of: ' + str(delta_azimuth))
