import video_repository.video_repository as video_repository
from offside_line_detector.offside_line_detector import *
import config.config as confg
import utils.constants as constants

if __name__ == '__main__':

    config = confg.default_config
    video_path = './test/videos'
    offside_line_detector = OffsideLineDetector(**config)

    while True:
        video = video_repository.VideoRepository.get_video(video_path + '/' + constants.VideoConstants.video_1_from_8_to_12)
        offside_line_detector.detect_and_draw_offside_line(video)
