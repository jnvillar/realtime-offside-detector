from domain.orientation import *


class ByParameter:
    def __init__(self, **kwargs):
        self.args = kwargs

    def detect_orientation(self, frame, vanishing_point) -> Orientation:
        orientation = self.args['orientation']
        return orientation
