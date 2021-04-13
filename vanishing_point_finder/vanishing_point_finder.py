from vanishing_point_finder.imp_by_hough import *


class VanishingPointFinder:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.vanishing_point)
        self.debug = debug
        methods = {
            'hough': ByHough(**kwargs['hough']),
        }
        self.method = methods[kwargs['method']]

    def find_vanishing_point(self, frame, frame_number):
        self.log.log("finding vanishing point")
        vanishing_point = self.method.find_vanishing_point(frame, frame_number)
        self.log.log("vanishing point found", {'vanishing_point': vanishing_point})
        return vanishing_point
