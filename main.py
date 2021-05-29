import video_repository.video_repository as video_repository
from offside_line_detector.offside_line_detector import *
import utils.constants as constants
from analytics.analytics import *
import config.config as config

if __name__ == '__main__':

    config = config.default_config
    video_path = './test/videos'
    video_name = constants.VideoConstants.video_1_from_8_to_12
    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['app']['debug_screen'])
    analytics = Analytics(video_name, **config['analytics_conf'])
    offside_line_detector = OffsideLineDetector(analytics, **config)

    while True:
        video = video_repository.VideoRepository.get_video(video_path + '/' + video_name)
        offside_line_detector.detect_and_draw_offside_line(video)
        analytics.store()
