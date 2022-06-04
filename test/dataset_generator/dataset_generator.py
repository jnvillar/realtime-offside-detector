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
        "V = switch to vanishing point parsing mode",
        # "D = switch to defending team parsing mode",
        "S = save parsed data to file",
        "ESC = exit without saving",
    ]
    EXIT_OPTIONS = [
        "Are you sure you want to exit? All the selection that was not saved WILL BE LOST.",
        "Y (yes)",
        "N (no)"
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
            'p': parsers.PlayersParser(self.FRAME_WINDOW_NAME),
            'v': parsers.VanishingPointParser(self.FRAME_WINDOW_NAME)
            # 'd': parsers.DefendingTeamParser(self.FRAME_WINDOW_NAME),
        }
        self.options = self.GENERAL_OPTIONS
        self.show_warning = False
        self.missing_parsing = None
        self.previous_frame_number = -1

    def generate_dataset(self, video_path, outfile):
        video = video_repository.VideoRepository.get_video(video_path, True)

        self.current_frame = video.get_next_frame()
        while self.current_frame is not None:
            current_frame_number = video.get_current_frame_number()
            # display frame with some informative text
            self.frame_printer.print_text(self.current_frame, "Frame: {}".format(current_frame_number), (5, 30), constants.BGR_WHITE)
            if self.show_warning:
                warning_message_lines = [
                    "WARNING: YOU DID NOT PARSE {} IN THE PREVIOUS FRAME ({}). ".format(self.missing_parsing, self.previous_frame_number),
                    "IF THAT'S OK DISMISS THIS MESSAGE AND CONTINUE!"
                ]
                print(warning_message_lines[0] + warning_message_lines[1])
                self.frame_printer.print_multiline_text(self.current_frame, warning_message_lines, (200, 20), constants.BGR_YELLOW)
            cv2.imshow(self.FRAME_WINDOW_NAME, self.current_frame)
            # cv2.moveWindow(self.FRAME_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[0], self.TOP_LEFT_FRAME_WINDOW[1])

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
                    if current_frame_number != 1:
                        self.show_warning = self._is_any_missing_parsing(current_frame_number)
                    self.current_frame = video.get_previous_frame()
                    break
                # SPACE to continue to next frame
                elif self.keyboard_manager.key_was_pressed(key_code, constants.SPACE_KEY_CODE):
                    self.show_warning = self._is_any_missing_parsing(current_frame_number)
                    self.current_frame = video.get_next_frame()
                    break
                # S to save parsed data to file
                elif self.keyboard_manager.is_lowercase_alphabet_char_code(key_code) and chr(key_code) == 's':
                    self._print_parsed_data(outfile)
                    self.options = self.GENERAL_OPTIONS
                    break
                # ESC to exit without saving
                elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                    self.options = self.EXIT_OPTIONS
                    self._print_available_options()
                    while True:
                        key_code_exit = cv2.waitKey(0)
                        if self.keyboard_manager.key_was_pressed(key_code_exit, constants.Y_KEY_CODE):
                            print("Goodbye!")
                            return
                        elif self.keyboard_manager.key_was_pressed(key_code_exit, constants.N_KEY_CODE):
                            print("Exit was aborted. Continue parsing.")
                            self.options = self.GENERAL_OPTIONS
                            self._print_available_options()
                            break
                # any other key will do nothing

        self._print_parsed_data(outfile, allow_abort_saving=False)

    def _is_any_missing_parsing(self, current_frame_number):
        current_frame_data_builder = self.frame_data_builders.get(current_frame_number, None)
        if current_frame_data_builder is None:
            return False

        players = current_frame_data_builder.players
        field = current_frame_data_builder.field
        vanishing_point_segments = current_frame_data_builder.vanishing_point_segments
        # if nothing was marked in the frame, we assume that it was not a frame of interest
        if players is None and field is None and vanishing_point_segments is None:
            return False
        elif players is None:
            self.missing_parsing = "PLAYERS"
            self.previous_frame_number = current_frame_number
            return True
        elif field is None:
            self.missing_parsing = "FIELD"
            self.previous_frame_number = current_frame_number
            return True
        elif vanishing_point_segments is None:
            self.missing_parsing = "VANISHING POINT SEGMENTS"
            self.previous_frame_number = current_frame_number
            return True

        return False

    def _print_parsed_data(self, outfile, allow_abort_saving=True):
        frame_data_mapper = FrameDataDictionaryMapper()
        frame_data_list = [frame_data_builder.build() for frame_number, frame_data_builder in self.frame_data_builders.items()]

        output_path = Path(outfile)
        if output_path.is_file():
            # file exists
            self.options = [
                "The output file to be written ({}) already exists.".format(outfile),
                "Do you want to merge parsed frame data or create a new file?",
                "1 = Merge",
                "9 = Create a new file (this file will not overwrite the existing one)",
            ]
            if allow_abort_saving:
                self.options.append("ESC = Abort saving and continue parsing")

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
                # NINE to create a new file with the frame data
                elif self.keyboard_manager.key_was_pressed(key_code, constants.NINE_KEY_CODE):
                    #  Add numeric suffix to the outfile to avoid overwrite
                    numeric_postfix = 1
                    new_outfile = "{} ({})".format(outfile, numeric_postfix)
                    while Path(new_outfile).is_file():
                        numeric_postfix += 1
                        new_outfile = "{} ({})".format(outfile, numeric_postfix)
                    outfile = new_outfile
                    break
                # ESC to not save
                elif allow_abort_saving and self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                    print("Save was aborted. Continue parsing.")
                    return

        # save data in file
        with open(outfile, 'w') as file:
            json.dump([frame_data_mapper.to_dictionary(frame_data) for frame_data in frame_data_list], file)
            print("Parsed data saved in file {}".format(outfile))

    def _print_available_options(self):
        height, width = [500, 1000] if self.current_frame is None else self.current_frame.shape[:2]
        black_frame = numpy.zeros((220, width, 3))
        self.frame_printer.print_multiline_text(black_frame, self.options, (5, 30), constants.BGR_WHITE)
        cv2.imshow(self.KEYS_HELP_WINDOW_NAME, black_frame)
        # cv2.moveWindow(self.KEYS_HELP_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[1], self.TOP_LEFT_FRAME_WINDOW[0] + height + 100)
