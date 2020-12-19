import log.log as log
import cv2

from os import listdir
from os.path import isfile, join
from domain.video import *


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
