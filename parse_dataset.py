import os

from argparse import ArgumentParser
from pathlib import Path

from test.dataset_generator.dataset_generator import DatasetGenerator


def parse_arguments():
    parser = ArgumentParser("Dataset generator")
    parser.add_argument("-o", help="Output file to save parsed data (if not used, same name as video)", default=None)
    parser.add_argument("video_path", help="Path to video to parse")
    arguments = parser.parse_args()
    video_path = arguments.video_path
    if arguments.o is None:
        outfile = os.path.join(Path(__file__).parent.absolute(), "datasets", get_file_name(video_path) + ".json")
    else:
        outfile = arguments.o
    print(outfile)
    return video_path, outfile


def get_file_name(video_path):
    return video_path.split("/")[-1].split(".")[0]


if __name__ == '__main__':
    video_path, outfile = parse_arguments()
    DatasetGenerator().generate_dataset(video_path, outfile)
