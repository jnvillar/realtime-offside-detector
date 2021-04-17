from vanishing_point_finder.imp_by_hough import *
from timer.timer import *


class VanishingPointFinder:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.vanishing_point)

        methods = {
            'hough': ByHough(**kwargs['hough']),
        }

        self.method = methods[kwargs['method']]

    def find_vanishing_point(self, frame, frame_number):
        self.log.log("finding vanishing point")
        Timer.start()
        vanishing_point = self.method.find_vanishing_point(frame, frame_number)
        elapsed_time = Timer.stop()
        self.log.log("vanishing point found", {'cost': elapsed_time, 'vanishing_point': vanishing_point})
        return vanishing_point
