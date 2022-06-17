import video_repository.video_repository as video_repository
from offside_line_detector.offside_line_detector import *
import utils.constants as constants
from analytics.analytics import *
import config.config as config

if __name__ == '__main__':
    config = config.default_config
    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['screen_manager'])

    video_path = './test/videos'
    dataset_path = './datasets'
    video_name = constants.VideoConstants.video_1_from_8_to_12

    analytics = Analytics(video_name, **config['analytics_conf'])
    offside_line_detector = OffsideLineDetector(analytics, **config)

    while True:
        video = video_repository.VideoRepository.get_video(video_path + '/' + video_name)
        offside_line_detector.detect_and_draw_offside_line(video, dataset_path + '/' + video_name.split(".")[0] + ".json")
        analytics.store()
