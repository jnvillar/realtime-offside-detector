import log.log as log
import cv2

from os import listdir
from os.path import isfile, join
from domain.video import *


class VideoRepository:

    def __init__(self, path):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.videos = {}
        self._load_videos(path)

    def list_videos(self):
        return self.videos.items()

    def get_video(self, video_name):
        video = self.videos.get(video_name)
        if video is None:
            raise Exception("Video {} not found".format(video_name))
        return video

    def _load_videos(self, path):
        # TODO: check if we get a high memory usage by loading everything together
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in files:
            try:
                video_capture = cv2.VideoCapture(path + "/" + file)
                if not video_capture.isOpened():
                    raise Exception()
                self.videos[file] = Video(video_capture)
            except:
                self.log.log("Error loading video", {"file": file})
