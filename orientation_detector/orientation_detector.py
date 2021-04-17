from orientation_detector.imp_by_parameter import *
from domain.orientation import *
from timer.timer import *
from log.log import *


class OrientationDetector:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.orientation_detector)

        methods = {
            'by_parameter': ByParameter(**kwargs['by_parameter']),
        }

        self.method = methods[kwargs['method']]

    def detect_orientation(self, frame, players: [Player]) -> Orientation:
        self.log.log("detecting orientation")
        Timer.start()
        orientation = self.method.detect_orientation(frame, players)
        elapsed_time = Timer.stop()
        self.log.log("orientation detected", {"cost": elapsed_time, "orientation": orientation})
        return orientation
