import json
import os

import config.config as config
from log.logger import Logger
from test.dataset_comparator.dataset_comparator import FieldDetectorComparisonStrategy, ComparatorByStrategy, PlayerDetectorComparisonStrategy
from test.dataset_generator.domain import FrameData
from test.dataset_generator.mappers import FrameDatasetDictionaryMapper
from utils.utils import ScreenManager
from video_repository.video_repository import VideoRepository


def get_video_frame_data(video_data_path) -> [FrameData]:
    video_frame_data = []
    if os.path.isfile(video_data_path):
        with open(video_data_path, 'r') as file:
            json_data = json.load(file)
            video_frame_data = FrameDatasetDictionaryMapper().from_dictionary(json_data)
    else:
        print('File {} does not exist. No dataset loaded.'.format(video_data_path))

    return video_frame_data


if __name__ == '__main__':
    config = config.default_config
    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['screen_manager'])

    video_name = '2_Boca-Lanus_202_216.mp4'

    video_path = './test/videos' + '/' + video_name
    dataset_path = './datasets' + '/' + video_name.split(".")[0] + ".json"

    # Strategies:
    # 1) Field detection
    # 2) Players detection
    comparison_strategy = 1
    # Whether to show the frames with the comparison results or not
    debug = True

    video_data = get_video_frame_data(dataset_path)
    video = VideoRepository.get_video(video_path)

    if comparison_strategy == 1:
        comparison_strategy = FieldDetectorComparisonStrategy(config)
    elif comparison_strategy == 2:
        comparison_strategy = PlayerDetectorComparisonStrategy(config)
    else:
        print("Undefined comparison strategy: " + str(comparison_strategy))
        exit(1)

    comparator = ComparatorByStrategy(comparison_strategy, debug)
    comparator.compare(video, video_data)