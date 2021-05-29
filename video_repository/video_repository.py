from os.path import isfile, join
from domain.video import *
from os import listdir
import log.logger as log
import cv2


class VideoRepository:

    def __init__(self, path, backward_navigation_enabled=False):
        self.log = log.Logger(self, log.LoggingPackage.player_detector)
        self.videos = {}
        self._load_all_videos(path, backward_navigation_enabled)

    def list_videos(self):
        return self.videos.items()

    def get_video(self, video_name):
        video = self.videos.get(video_name)
        if video is None:
            raise Exception("Video {} not found".format(video_name))
        return video

    @staticmethod
    def get_video(video_path, backward_navigation_enabled=False):
        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            raise Exception("Error loading video {}".format(video_path))
        return Video(video_capture, backward_navigation_enabled)

    def _load_all_videos(self, path, backward_navigation_enabled):
        # TODO: check if we get a high memory usage by loading everything together
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in files:
            self.videos[file] = VideoRepository.get_video(path + "/" + file, backward_navigation_enabled)
