import json
import os

from utils.constants import VideoConstants
import config.override_config as override_config
import config.config as config
from log.logger import Logger
from test.dataset_comparator.dataset_comparator import FieldDetectorComparisonStrategy, ComparatorByStrategy, \
    PlayerDetectorComparisonStrategy, PlayerSorterComparisonStrategy, IntertiaComparisonStrategy
from test.dataset_generator.domain import FrameData
from test.dataset_generator.mappers import FrameDatasetDictionaryMapper
from utils.utils import ScreenManager
from video_repository.video_repository import VideoRepository
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def save_comparison_results(video_name, comparison_strategy, results):
    if comparison_strategy == 1:
        result_name = 'field-detection'
    if comparison_strategy == 2:
        result_name = 'players-detection'
    if comparison_strategy == 3:
        result_name = 'players-sorting'
    if comparison_strategy == 4:
        result_name = 'intertia'

    if result_name is None:
        Exception("set result name")

    result_path = './experiments' + '/' + video_name.split(".")[0] + "-" + result_name + ".json"

    with open(result_path, 'w') as file:
        json.dump(results, file, indent=2, cls=NpEncoder)


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
    debug = False
    all_videos = True

    if all_videos:
        videos = VideoConstants().all()
    else:
        videos = [
            VideoConstants.video_1_Arsenal_Chelsea_107_122,
            VideoConstants.video_4_Liverpool_Benfica_119_126,
            VideoConstants.video_20_BayernMunich_ViktoriaPlzen_515_524
        ]

    # Strategies:
    # 1) Field detection
    # 2) Players detection
    # 3) Team classification
    # 4) Kmeans intertia
    comparison_strategy = 4
    # Whether to show the frames with the comparison results or not

    configuration = config.default_config.copy()
    Logger.initialize(configuration['logger'])
    ScreenManager.initialize(configuration['screen_manager'])

    for video_name in videos:
        print(video_name)

        video_path = './test/videos' + '/' + video_name
        dataset_path = './datasets' + '/' + video_name.split(".")[0]

        override_configuration = override_config.override_config.get(video_name.split(".")[0], config.default_config)
        configuration.update(override_configuration)

        try:
            video_data = get_video_frame_data(dataset_path + ".json")
            video = VideoRepository.get_video(video_path)
        except Exception as e:
            print('Error opening video {}'.format(video_name))
            continue

        if comparison_strategy == 1:
            strategy = FieldDetectorComparisonStrategy(configuration)
        elif comparison_strategy == 2:
            strategy = PlayerDetectorComparisonStrategy(configuration)
        elif comparison_strategy == 3:
            strategy = PlayerSorterComparisonStrategy(configuration)
        elif comparison_strategy == 4:
            strategy = IntertiaComparisonStrategy({
                'amount_of_frames': 1
            })
        else:
            print("Undefined comparison strategy: " + str(comparison_strategy))
            exit(1)

        comparator = ComparatorByStrategy(strategy, debug)
        results = comparator.compare(video, video_data)

        save_comparison_results(video_name, comparison_strategy, results)
