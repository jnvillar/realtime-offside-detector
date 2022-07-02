import video_repository.video_repository as video_repository
from offside_line_detector.offside_line_detector import *
import utils.constants as constants
from analytics.analytics import *
import config.config as config
from datetime import datetime


def get_video_frame_data(video_data_path) -> [FrameData]:
    with open(video_data_path, 'r') as file:
        json_data = json.load(file)
        return FrameDatasetDictionaryMapper().from_dictionary(json_data)


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
    config = config.default_config
    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['screen_manager'])

    video_name = constants.VideoConstants.video_1_from_8_to_12

    video_path = './test/videos' + '/' + video_name
    dataset_path = './datasets' + '/' + video_name.split(".")[0] + ".json"

    analytics = Analytics(video_name, **config['analytics_conf'])
    offside_line_detector = OffsideLineDetector(analytics, **config)

    video_data = get_video_frame_data(dataset_path)

    while True:
        video = video_repository.VideoRepository.get_video(video_path)
        comparison_results = offside_line_detector.detect_and_draw_offside_line(video, video_data)
        save_comparison_results(video_name=video_name, results=comparison_results)
