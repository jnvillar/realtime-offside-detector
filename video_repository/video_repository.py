import log.log as log
import cv2

from os import listdir
from os.path import isfile, join


class Video:

    def __init__(self, video, backward_navigation_enabled=False):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.video = video
        self.backward_navigation_enabled = backward_navigation_enabled
        self.current_frame = None
        self.current_frame_number = 0
        self.next_frames = []
        self.previous_frames = []

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


class VideoRepository:

    def __init__(self, path, backward_navigation_enabled=False):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
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
