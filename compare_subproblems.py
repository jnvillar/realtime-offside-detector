import json
import os

import utils.constants as constants
import config.override_config as override_config
import config.config as config
from log.logger import Logger
from test.dataset_comparator.dataset_comparator import FieldDetectorComparisonStrategy, ComparatorByStrategy, \
    PlayerDetectorComparisonStrategy, PlayerSorterComparisonStrategy
from test.dataset_generator.domain import FrameData
from test.dataset_generator.mappers import FrameDatasetDictionaryMapper
from utils.utils import ScreenManager
from video_repository.video_repository import VideoRepository


def save_comparison_results(video_name, comparison_strategy, results):
    if comparison_strategy == 1:
        result_name = 'field-detection'
    if comparison_strategy == 2:
        result_name = 'players-detection'
    if comparison_strategy == 3:
        result_name = 'players-sorting'

    if result_name is None:
        Exception("set result name")

    result_path = './experiments' + '/' + video_name.split(".")[0] + "-" + result_name + ".json"

    with open(result_path, 'w') as file:
        results = [ob if isinstance(ob, dict) else ob.__dict__ for ob in results]
        json.dump(results, file, indent=2)


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
    video_name = constants.VideoConstants.video_15_Valencia_Getafe_38_52
    video_path = './test/videos' + '/' + video_name
    dataset_path = './datasets' + '/' + video_name.split(".")[0]

    override_config = override_config.override_config.get(video_name.split(".")[0], {})
    config = config.default_config
    config.update(override_config)

    Logger.initialize(config['logger'])
    ScreenManager.initialize(config['screen_manager'])

    # Strategies:
    # 1) Field detection
    # 2) Players detection
    comparison_strategy = 3
    # Whether to show the frames with the comparison results or not
    debug = False

    video_data = get_video_frame_data(dataset_path + ".json")
    video = VideoRepository.get_video(video_path)

    if comparison_strategy == 1:
        strategy = FieldDetectorComparisonStrategy(config)
    elif comparison_strategy == 2:
        strategy = PlayerDetectorComparisonStrategy(config)
    elif comparison_strategy == 3:
        strategy = PlayerSorterComparisonStrategy(config)
    else:
        print("Undefined comparison strategy: " + str(comparison_strategy))
        exit(1)

    comparator = ComparatorByStrategy(strategy, debug)
    results = comparator.compare(video, video_data)

    save_comparison_results(video_name, comparison_strategy, results)
