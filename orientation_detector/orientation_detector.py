from orientation_detector.imp_by_parameter import *
from orientation_detector.imp_by_vanishing_point import *
from domain.orientation import *
from timer.timer import *
from log.log import *


class OrientationDetector:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Log(self, LoggingPackage.orientation_detector)

        methods = {
            'by_parameter': ByParameter(**kwargs['by_parameter']),
            'by_vanishing_point': ByVanishingPoint(),
        }

        self.method = methods[kwargs['method']]

    def detect_orientation(self, frame, vanishing_point) -> Orientation:
        self.log.log("detecting orientation")
        Timer.start()
        orientation = self.method.detect_orientation(frame, vanishing_point)
        elapsed_time = Timer.stop()
        self.log.log("orientation detected", {"cost": elapsed_time, "orientation": str(orientation)})
        return orientation
