import json
from pathlib import Path

import cv2
import numpy

import test.dataset_generator.parsers as parsers
import utils.utils as utils
from test.dataset_generator.domain import FrameDataBuilder
from test.dataset_generator.mappers import FrameDataDictionaryMapper
from test.dataset_generator.utils import FrameDataMerger
from utils import constants
from video_repository import video_repository


class DatasetGenerator:

    FRAME_WINDOW_NAME = "Dataset generator"
    KEYS_HELP_WINDOW_NAME = "Keys help"
    GENERAL_OPTIONS = [
        "SPACE = continue to next frame",
        "DELETE = go back to previous frame",
        "F = switch to field parsing mode",
        "P = switch to players parsing mode",
        "S = save parsed data to file",
        "ESC = exit without saving",
    ]
    TOP_LEFT_FRAME_WINDOW = (1, 1)

    def __init__(self):
        self.current_frame = None
        self.previous_frames = []
        self.field_vertices = []
        self.frame_data_builders = {}
        self.keyboard_manager = utils.KeyboardManager()
        self.frame_printer = utils.FramePrinter()
        self.parsers = {
            'f': parsers.FieldParser(self.FRAME_WINDOW_NAME),
            'p': parsers.PlayersParser(self.FRAME_WINDOW_NAME)
        }
        self.options = self.GENERAL_OPTIONS

    def generate_dataset(self, video_path, outfile):
        video = video_repository.VideoRepository.get_video(video_path, True)

        print_json = False
        self.current_frame = video.get_next_frame()
        while self.current_frame is not None:
            current_frame_number = video.get_current_frame_number()
            # display frame with some informative text
            self.frame_printer.print_text(self.current_frame, "Frame: {}".format(current_frame_number), (5, 30), constants.BGR_WHITE)
            cv2.imshow(self.FRAME_WINDOW_NAME, self.current_frame)
            cv2.moveWindow(self.FRAME_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[0], self.TOP_LEFT_FRAME_WINDOW[1])

            self._print_available_options()

            while True:
                key_code = cv2.waitKey(0)
                # keys defined in self.parsers to switch to any of the parsing modes
                if self.keyboard_manager.is_lowercase_alphabet_char_code(key_code) and chr(key_code) in self.parsers:
                    frame_data_builder = self.frame_data_builders.get(current_frame_number, FrameDataBuilder().set_frame_number(current_frame_number))
                    # set parser options and print them
                    self.options = self.parsers.get(chr(key_code)).get_options()
                    self._print_available_options()
                    if self.parsers.get(chr(key_code)).parse(self.current_frame.copy(), frame_data_builder):
                        self.frame_data_builders[current_frame_number] = frame_data_builder
                    cv2.imshow(self.FRAME_WINDOW_NAME, self.current_frame)
                    # restore general options and print them
                    self.options = self.GENERAL_OPTIONS
                    self._print_available_options()
                # DELETE to go back to previous frame
                elif self.keyboard_manager.key_was_pressed(key_code, constants.DELETE_KEY_CODE):
                    self.current_frame = video.get_previous_frame()
                    break
                # SPACE to continue to next frame
                elif self.keyboard_manager.key_was_pressed(key_code, constants.SPACE_KEY_CODE):
                    self.current_frame = video.get_next_frame()
                    break
                # S to save parsed data to file
                elif self.keyboard_manager.is_lowercase_alphabet_char_code(key_code) and chr(key_code) == 's':
                    print_json = True
                    break
                # ESC to exit without saving
                elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                    return
                # any other key will do nothing

            if print_json:
                break

        self._print_parsed_data(outfile)

    def _print_parsed_data(self, outfile):
        frame_data_mapper = FrameDataDictionaryMapper()
        frame_data_list = [frame_data_builder.build() for frame_number, frame_data_builder in self.frame_data_builders.items()]

        output_path = Path(outfile)
        if output_path.is_file():
            # file exists
            self.options = [
                "The output file to be written ({}) already exists.".format(outfile),
                "Do you want to merge parsed frame data or overwrite it?",
                "1 = Merge",
                "2 = Overwrite",
                "ESC = Exit without saving anything"
            ]
            self._print_available_options()
            while True:
                key_code = cv2.waitKey(0)
                # ONE to merge frame data list from file and the new frame data
                if self.keyboard_manager.key_was_pressed(key_code, constants.ONE_KEY_CODE):
                    with open(outfile, 'r') as file:
                        frame_data_dictionary_list = json.load(file)
                        file_frame_data_list = [frame_data_mapper.from_dictionary(frame_data_dictionary) for frame_data_dictionary in frame_data_dictionary_list]
                        frame_data_list = FrameDataMerger.merge(frame_data_list, file_frame_data_list)
                        break
                # TWO to overwrite with the new frame data
                elif self.keyboard_manager.key_was_pressed(key_code, constants.TWO_KEY_CODE):
                    break
                # ESC to exit without saving
                elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                    return

        # save data in file
        with open(outfile, 'w') as file:
            json.dump([frame_data_mapper.to_dictionary(frame_data) for frame_data in frame_data_list], file)

    def _print_available_options(self):
        height, width = [500, 1000] if self.current_frame is None else self.current_frame.shape[:2]
        black_frame = numpy.zeros((200, width, 3))
        self.frame_printer.print_multiline_text(black_frame, self.options, (5, 30), constants.BGR_WHITE)
        cv2.imshow(self.KEYS_HELP_WINDOW_NAME, black_frame)
        cv2.moveWindow(self.KEYS_HELP_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[1], self.TOP_LEFT_FRAME_WINDOW[0] + height + 100)
