import json

from argparse import ArgumentParser

from test.dataset_generator.dataset_reader import DatasetReader
from video_repository.video_repository import VideoRepository


def parse_arguments():
    parser = ArgumentParser("Dataset Reader")
    parser.add_argument("video_path", help="Path to video to parse")
    parser.add_argument("json_dataset", help="Path to json dataset")
    arguments = parser.parse_args()
    video_path = arguments.video_path
    json_dataset = arguments.json_dataset
    return video_path, json_dataset


def get_file_name(video_path):
    return video_path.split("/")[-1].split(".")[0]


if __name__ == '__main__':
    video_path, json_dataset_path = parse_arguments()
    video = VideoRepository.get_video(video_path, True)
    with open(json_dataset_path, 'r') as file:
        frame_data_dictionary_list = json.load(file)
        DatasetReader().read_dataset(video, frame_data_dictionary_list)
