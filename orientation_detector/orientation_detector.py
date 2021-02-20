from log.log import *
from orientation_detector.imp_by_parameter import *
from domain.orientation import *


class OrientationDetector:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.orientation_detector)
        self.debug = debug
        self.methods = {
            'by_parameter': ByParameter(**kwargs),
        }

    def detect_orientation(self, frame, players: [Player], method='by_parameter') -> Orientation:
        orientation = self.methods[method].detect_orientation(frame, players)
        return orientation
