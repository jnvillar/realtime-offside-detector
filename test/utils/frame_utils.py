import video_repository.video_repository as video_repository
import log.log as log
import utils.constants as constants
import utils.frame_utils as frame_utils
from domain.color import *
import cv2


class FrameUtilsTests:
    def __init__(self):
        self.videos_repository = video_repository.VideoRepository("../videos")
        self.log = log.Log(self, log.LoggingPackage.test)

    def test_remove_color(self):

        while True:
            video_container = video_repository.VideoRepository("../videos")
            video = video_container.get_video(constants.VideoConstants.video_1_from_8_to_12)

            while True:
                frame = video.get_next_frame()

                self.log.log("frame", {'frame': video.get_current_frame_number()})

                if frame is None:
                    break

                frame = frame_utils.remove_color(frame, ColorRange.yellow.colors)

                frame_utils.show(frame, 'remove color', 1)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    play = not play

        if cv2.waitKey(30) & 0xFF == ord('q'):
            play = not play


if __name__ == '__main__':
    frame_utils_tests = FrameUtilsTests()
    frame_utils_tests.test_remove_color()
