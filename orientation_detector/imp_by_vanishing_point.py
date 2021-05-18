from domain.orientation import *


class ByVanishingPoint:
    def __init__(self, **kwargs):
        self.args = kwargs

    def detect_orientation(self, frame, vanishing_point) -> Orientation:
        img_h, img_w = frame.shape[:2]
        middle_frame = img_h / 2
        if vanishing_point[0] > middle_frame:
            orientation = Orientation.left
        else:
            orientation = Orientation.right
        return orientation
