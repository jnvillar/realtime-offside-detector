import os
import video_repository.video_repository as video_repository
from config.config_provider import ConfigProvider
from offside_line_detector.offside_line_detector import *
import utils.constants as constants
from analytics.analytics import *
import config.config as config
import config.override_config as override_config
from datetime import datetime


def get_video_frame_data(video_data_path, config) -> [FrameData]:
    video_frame_data = []
    if config.get('app', {}).get('compare', False):
        if os.path.isfile(video_data_path):
            with open(video_data_path, 'r') as file:
                json_data = json.load(file)
                video_frame_data = FrameDatasetDictionaryMapper().from_dictionary(json_data)
        else:
            print('File {} does not exist. No dataset loaded.'.format(video_data_path))

    return video_frame_data


def save_comparison_results(video_name, results):
    use_time = False
    if use_time:
        result_path = './experiments' + '/' + str(datetime.now().time()) + '_' + video_name.split(".")[0] + ".json"
    else:
        result_path = './experiments' + '/' + video_name.split(".")[0] + ".json"

    with open(result_path, 'w') as file:
        results = [ob if isinstance(ob, dict) else ob.__dict__ for ob in results]
        json.dump(results, file, indent=2)


if __name__ == '__main__':
    video_name = constants.VideoConstants.video_4_Liverpool_Benfica_422_432

    video_path = './test/videos' + '/' + video_name
    dataset_path = './datasets' + '/' + video_name.split(".")[0] + ".json"
    config = ConfigProvider().get_config_for_video(video_name)

    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['screen_manager'])

    analytics = Analytics(video_name, **config['analytics_conf'])
    offside_line_detector = OffsideLineDetector(analytics, **config)

    video_data = get_video_frame_data(dataset_path, config)

    while True:
        video = video_repository.VideoRepository.get_video(video_path)
        comparison_results = offside_line_detector.detect_and_draw_offside_line(video, video_data)
        save_comparison_results(video_name=video_name, results=comparison_results)
