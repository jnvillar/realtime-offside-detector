import log.log as log
import cv2


class Frame:
    def __init__(self, frame, frame_number, ret):
        self.frame = frame
        self.frame_number = frame_number
        self.ret = ret

    def get_frame_number(self):
        return self.frame_number

    def get_frame(self):
        return self.frame


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


class VideoRepository:
    # video_path = string
    def __init__(self):
        self.log = log.Log(self, log.LoggingPackage.player_detector)

    def get_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        return Video(cap)
