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
    player_detector = 'player_detection'
    player_sorter = 'player_sorter'
    vanishing_point_finder = 'vanishing_point_finder'
    intertia = 'intertia'
    player_tracker = 'player_tracker'

    def get_strategy_comparator(self, conf):
        if self == ComparisonStrategy.player_tracker:
            return PlayerDetectorComparisonStrategy(conf)

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


def get_result_path(video_name, comparison_strategy, method):
    result_path = './experiments' + '/' + video_name.split(".")[0] + "-" + comparison_strategy.value

    if method != "":
        result_path = result_path + "-" + method

    result_path = result_path + ".json"
    return result_path


def save_comparison_results(path, results, merge=False):
    if os.path.exists(save_result_path) and merge:
        print("merging result for {}".format(video_name))
        previous_results = get_results_json(save_result_path)

        old_results = previous_results["frame_results"]
        new_results = results["frame_results"]

        merged_results = []
        count = 0
        for idx, new_result in enumerate(new_results):
            try:
                new = True
                for old_result in old_results:
                    if old_result['frame_number'] == new_result['frame_number']:
                        new = False
                        merged_results.append(merge_results(old_result, new_result))
                if new:
                    merged_results.append(new_result)

            # old files do not have key frame_number
            except:
                if new_result['type'] == 'detect_and_compare':
                    merged_results.append(merge_results(old_results[count], new_result))
                    count += 1
                else:
                    merged_results.append(new_result)

        results["frame_results"] = merged_results

    with open(path, 'w') as file:
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


methods_for_strategy = {
    'field_detection': {
        'green_detection': {
            'field_detector': {
                'method': 'green_detection',
            },
        },
        'ground_pixels_detection': {
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
    },
    'vanishing_point_finder': {
        'hough': {}
    },
    'player_detection': {
        'edges': {
            'player_tracker': {
                'method': 'off',
            },
            'player_detector': {
                'method': 'edges',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'otsu': {
            'player_tracker': {
                'method': 'off',
            },
            'player_detector': {
                'method': 'otsu',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'by_color': {
            'player_tracker': {
                'method': 'off',
            },
            'player_detector': {
                'method': 'by_color',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'background_subtraction': {
            'player_tracker': {
                'method': 'off',
            },
            'player_detector': {
                'method': 'background_subtraction',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'kmeans': {
            'player_tracker': {
                'method': 'off',
            },
            'player_detector': {
                'method': 'kmeans',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
    },
    'player_tracker': {
        'distance_edges': {
            'player_tracker': {
                'method': 'distance',
            },
            'player_detector': {
                'method': 'edges',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'distance_otsu': {
            'player_tracker': {
                'method': 'distance',
            },
            'player_detector': {
                'method': 'otsu',
            },
            'field_detector': {
                 'method': 'ground_pixels_detection',
            },
        },
        'distance_by_color': {
            'player_tracker': {
                'method': 'distance',
            },
            'player_detector': {
                'method': 'by_color',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
        'distance_background_subtraction': {
            'player_tracker': {
                'method': 'distance',
            },
            'player_detector': {
                'method': 'background_subtraction',
            },
             'field_detector': {
                 'method': 'ground_pixels_detection',
            },
        },
        'distance_kmeans': {
            'player_tracker': {
                'method': 'distance',
            },
            'player_detector': {
                'method': 'kmeans',
            },
            'field_detector': {
                'method': 'ground_pixels_detection',
            },
        },
    },
    'player_sorter': {
        'kmeans': {
            'method': 'kmeans',
        },
        'bsas': {
            'method': 'bsas',
        },
    }
}


def get_results_json(results_file_path):
    json_data = {}
    if os.path.isfile(results_file_path):
        with open(results_file_path, 'r') as file:
            json_data = json.load(file)
    else:
        print('File {} does not exist. No results loaded.'.format(results_file_path))

    return json_data


def merge_results(old_results, new_results):
    merged_config = old_results.copy()

    for k, v in new_results.items():
        if k in old_results and isinstance(v, dict):
            merged_config[k] = merge_results(old_results[k], v)
        elif k in old_results and k != "time":
            continue
        else:
            merged_config[k] = v
    return merged_config


if __name__ == '__main__':
    debug = False
    override_experiment = True
    merge_experiments = True
    strategy = ComparisonStrategy.player_tracker

    videos = [
        #VideoConstants.video_16_RealMadrid_Shakhtar_20_29
    ]

    if len(videos) == 0:
        videos = VideoConstants().all()

    config_provider = ConfigProvider()
    configuration = config.default_config
    Logger.initialize(configuration['logger'])
    ScreenManager.initialize(configuration['screen_manager'])

    for method, config in methods_for_strategy[strategy.value].items():
        print("processing method: {}".format(method))
        for video_name in videos:
            print("processing video: {}".format(video_name))

            configuration = config_provider.get_config_for_video(video_name, merge_config=config)
            comparator = strategy.get_strategy_comparator(configuration)

            save_result_path = get_result_path(video_name, strategy, method)

            if os.path.exists(save_result_path) and not override_experiment:
                print("skipping result for {} already exists".format(video_name))
                continue

            video_path = './test/videos' + '/' + video_name
            dataset_path = './datasets' + '/' + video_name.split(".")[0]

            try:
                if not os.path.exists(video_path):
                    continue

                video_data = get_video_frame_data(dataset_path + ".json")
                video = VideoRepository.get_video(video_path)

            except Exception as e:
                print('Error opening video {}'.format(video_name))
                continue

            results = ComparatorByStrategy(comparator, debug).compare(video, video_data)

            save_comparison_results(save_result_path, results, merge=merge_experiments)
