from domain.frame import *
import log.log as log


class Video:
    def __init__(self, video):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.video = video
        self.current_frame = 0

    def get_current_frame(self):
        return self.current_frame

    def get_next_frame(self):
        ret, video_frame = self.video.read()
        frame = Frame(video_frame, self.current_frame, ret)
        self.current_frame += 1
        return frame
