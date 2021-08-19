from timer.timer import *
from utils.frame_utils import *
from utils.utils import ScreenManager


class Step:
    def __init__(self, name: str, function, params={}, debug: bool = False, modify_original_frame=True):
        self.screen_manager = ScreenManager.get_manager()
        self.modify_original_frame = modify_original_frame
        self.step = ASDStep(name, function, params, debug)

    def apply(self, number, original_frame, params=None):
        frame = original_frame

        if not self.modify_original_frame:
            frame = original_frame.copy()

        frame = self.step.apply(number, frame, params)
        self.screen_manager.show_frame(frame, self.step.name) if self.step.debug else None

        return frame


class ASDStep:
    def __init__(self, name: str, function, params={}, debug: bool = False):
        self.log = Logger(self, LoggingPackage.player_detector)
        self.name = name
        self.function = function
        self.debug = debug
        self.params = params

    def apply(self, number, frame, params=None):
        if params is None:
            params = self.params
        else:
            # merge
            params = {**params, **self.params}

        Timer.start('step {}'.format(number))
        step_result = self.function(frame, params)
        elapsed_time = Timer.stop('step {}'.format(number))

        self.log.log('applying', {
            "number": number,
            "name": self.name,
            "params": self.params,
            "cost": elapsed_time
        }) if self.debug else None

        return step_result
