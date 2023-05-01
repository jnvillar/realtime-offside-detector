import json
import os

from config.config_provider import ConfigProvider
from utils.constants import VideoConstants
import config.config as config
from log.logger import Logger
from test.dataset_comparator.dataset_comparator import FieldDetectorComparisonStrategy, ComparatorByStrategy, \
    PlayerDetectorComparisonStrategy, PlayerSorterComparisonStrategy, IntertiaComparisonStrategy, \
    VanishingPointFinderComparisonStrategy
from test.dataset_generator.domain import FrameData
from test.dataset_generator.mappers import FrameDatasetDictionaryMapper
from utils.utils import ScreenManager
from video_repository.video_repository import VideoRepository
import numpy as np

from enum import Enum


class ComparisonStrategy(Enum):
    field_detector = 'field_detection'
    player_detector = 'players_detection'
    player_sorter = 'player_sorter'
    vanishing_point_finder = 'vanishing_point_finder'
    intertia = 'intertia'

    def get_strategy_comparator(self, conf):
        if self == ComparisonStrategy.field_detector:
            return FieldDetectorComparisonStrategy(conf)

        if self == ComparisonStrategy.player_detector:
            return PlayerDetectorComparisonStrategy(conf)

        if self == ComparisonStrategy.player_sorter:
            return PlayerSorterComparisonStrategy(conf)

        if self == ComparisonStrategy.vanishing_point_finder:
            return VanishingPointFinderComparisonStrategy(conf)

        if self == ComparisonStrategy.intertia:
            return IntertiaComparisonStrategy({'amount_of_frames': 1})


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def save_comparison_results(video_name, comparison_strategy, method, results):
    result_path = './experiments' + '/' + video_name.split(".")[0] + "-" + comparison_strategy.value

    if method != "":
        result_path = result_path + "-" + method

    result_path = result_path + ".json"

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
    strategy = ComparisonStrategy.player_sorter

    if all_videos:
        videos = VideoConstants().all()
    else:
        videos = [
            VideoConstants.video_11_Estudiantes_Patronato_380_392,
            VideoConstants.video_18_Sevilla_Valladolid_29_38,
            VideoConstants.video_21_Roma_Ludogrets_503_510,
            VideoConstants.video_22_ManchesterCity_Brighton_539_547,
        ]

    config_provider = ConfigProvider()
    configuration = config.default_config
    Logger.initialize(configuration['logger'])
    ScreenManager.initialize(configuration['screen_manager'])

    for video_name in videos:
        print("processing video: {}".format(video_name))
        configuration = config_provider.get_config_for_video(video_name)

        video_path = './test/videos' + '/' + video_name
        dataset_path = './datasets' + '/' + video_name.split(".")[0]

        try:
            video_data = get_video_frame_data(dataset_path + ".json")
            video = VideoRepository.get_video(video_path)
        except Exception as e:
            print('Error opening video {}'.format(video_name))
            continue

        comparator = strategy.get_strategy_comparator(configuration)
        results = ComparatorByStrategy(comparator, debug).compare(video, video_data)
        method_name = configuration.get(strategy.name, {}).get('method', ""),
        save_comparison_results(video_name, strategy, method_name, results)
