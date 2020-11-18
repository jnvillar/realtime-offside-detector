import log.log as log
import cv2

from os import listdir
from os.path import isfile, join


class Frame:
    def __init__(self, frame, frame_number, ret):
        self.frame = frame
        self.frame_number = frame_number
        self.ret = ret

    def get_frame_number(self):
        return self.frame_number

    def get_frame(self):
        return self.frame

    def is_last_frame(self):
        return not self.ret


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
        self.videos = {}

    def list_videos(self):
        return self.videos.items()

    def get_video(self, video_name):
        video = self.videos.get(video_name)
        if video is None:
            raise Exception("video not found")
        return video

    def load_videos(self, path):
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in files:
            try:
                self.videos[file] = Video(cv2.VideoCapture(path + "/" + file))
            except:
                self.log.log("error loading video", {"file": file})
