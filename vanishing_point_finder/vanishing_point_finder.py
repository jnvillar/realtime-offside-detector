from vanishing_point_finder.imp_by_hough import *
from domain.video import *
from timer.timer import *


class VanishingPointFinder:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Logger(self, LoggingPackage.vanishing_point)

        methods = {
            'hough': ByHough(**kwargs['hough']),
        }

        self.method = methods[kwargs['method']]

    def find_vanishing_point(self, frame: Video):
        self.log.log("finding vanishing point")
        Timer.start('finding vanishing point')
        vanishing_point, vanishing_point_segments = self.method.find_vanishing_point(frame)
        elapsed_time = Timer.stop('finding vanishing point')
        self.log.log("vanishing point found", {'cost': elapsed_time, 'vanishing_point': vanishing_point})
        return vanishing_point, vanishing_point_segments, elapsed_time
