import pigpio
import time


class MoonTrackerElevationDriver(object):

    def __init__(self):
        self.pi = pigpio.pi()

    def set_elevation_position(self, elevation):
        pass
