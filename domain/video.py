from domain.frame import *
import log.log as log


class Video:

    def __init__(self, video):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.video = video
        self.current_frame = None
        self.current_frame_number = 0

    def get_current_frame(self):
        return self.current_frame

    def get_current_frame_number(self):
        return self.current_frame_number

    def get_next_frame(self):
        successful_read, frame = self.video.read()
        if successful_read:
            self.current_frame_number += 1
            self.current_frame = frame
        else:
            self.current_frame = None
        return self.current_frame
