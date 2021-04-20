from timer.timer import *
from utils.frame_utils import *


class Step:
    def __init__(self, name: str, function, params=None, debug: bool = False, modify_original_frame=True):
        self.log = Log(self, LoggingPackage.player_detector)
        self.name = name
        self.function = function
        self.debug = debug
        self.params = params
        self.modify_original_frame = modify_original_frame

    def apply(self, number, original_frame, params=None):
        if params is None:
            params = self.params

        frame = original_frame

        if not self.modify_original_frame:
            frame = original_frame.copy()

        Timer.start()
        frame = self.function(frame, params)
        elapsed_time = Timer.stop()

        show(frame, self.name, number) if self.debug else None

        self.log.log('applying', {
            "number": number,
            "name": self.name,
            "params": self.params,
            "cost": elapsed_time
        }) if self.debug else None

        if self.modify_original_frame:
            return frame
        else:
            return original_frame
