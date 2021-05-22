from domain.frame import *
import log.log as log


class Video:

    def __init__(self, video, backward_navigation_enabled=False):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.video = video
        self.backward_navigation_enabled = backward_navigation_enabled
        self.current_frame = None
        self.current_frame_number = 0
        self.next_frames = []
        self.previous_frames = []

    def set_frame(self, frame):
        self.current_frame = frame
        return self

    def get_current_frame(self):
        return self.current_frame.copy()

    def get_current_frame_number(self):
        return self.current_frame_number

    def get_next_frame(self):
        if not self.current_frame is None:
            self.previous_frames.append(self.current_frame)

        if len(self.next_frames) > 0:
            self.current_frame = self.next_frames.pop()
        else:
            successful_read, frame = self.video.read()
            if successful_read:
                self.current_frame = frame
            else:
                self.current_frame = None

        self.current_frame_number += 1

        return None if self.current_frame is None else self.current_frame.copy()

    def get_previous_frame(self):
        if not self.backward_navigation_enabled:
            raise Exception("Backward navigation is not enabled")

        if len(self.previous_frames) > 0:
            if not self.current_frame is None:
                self.next_frames.append(self.current_frame)
            self.current_frame = self.previous_frames.pop()
            self.current_frame_number -= 1

        return self.current_frame.copy()
