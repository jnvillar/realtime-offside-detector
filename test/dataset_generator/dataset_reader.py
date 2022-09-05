import json
from pathlib import Path

import cv2
import numpy

import utils.utils as utils
from test.dataset_generator.mappers import FrameDatasetDictionaryMapper
from test.dataset_generator.utils import FrameDataPrinter
from utils import constants


class DatasetReader:

    FRAME_WINDOW_NAME = "Dataset reader"
    KEYS_HELP_WINDOW_NAME = "Keys help"
    GENERAL_OPTIONS = [
        "SPACE = continue to next frame",
        "DELETE = go back to previous frame",
        "W = go to next frame with marked data",
        "Q = go to previous frame with marked data",
        "F = hide/show field (if available)",
        "P = hide/show players and referees (if available)",
        "V = hide/show vanishing point segments (if available)",
        "ESC = exit",
    ]
    EXIT_OPTIONS = [
        "Are you sure you want to exit?",
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
        self.frame_data_printer = FrameDataPrinter()
        self.frame_dataset_mapper = FrameDatasetDictionaryMapper()
        self.options = self.GENERAL_OPTIONS
        self.show_field = True
        self.show_players_and_referees = True
        self.show_vp_segments = True
        self.frame_data_list_index = -1
        self.read_started = True

    def read_dataset(self, video, json_dataset):
        frame_data_list = self.frame_dataset_mapper.from_dictionary(json_dataset)
        frame_data_list.sort(key=lambda e: e.get_frame_number())
        frame_data_by_frame_number = {frame_data.get_frame_number(): frame_data for frame_data in frame_data_list}

        self.current_frame = video.get_next_frame()
        # move frame_data_list_index to first element if there is frame data for first frame
        if 1 in frame_data_by_frame_number:
            self.frame_data_list_index = 0
        while self.current_frame is not None:
            current_frame_number = video.get_current_frame_number()
            # display frame with some informative text
            self.frame_printer.print_text(self.current_frame, "Frame: {}".format(current_frame_number), (5, 30), constants.BGR_WHITE)
            if current_frame_number in frame_data_by_frame_number:
                self.current_frame = self.frame_data_printer.print(frame_data_by_frame_number.get(current_frame_number), self.current_frame, self.show_field, self.show_players_and_referees, self.show_vp_segments, True)
            cv2.imshow(self.FRAME_WINDOW_NAME, self.current_frame)
            # Only for the first time move the window
            if self.read_started:
                cv2.moveWindow(self.FRAME_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[0], self.TOP_LEFT_FRAME_WINDOW[1])

            self._print_available_options()

            while True:
                key_code = cv2.waitKey(0)
                # F to hide/show field
                if chr(key_code) == 'f':
                    self.show_field = not self.show_field
                    self.current_frame = video.get_current_frame()
                    print("Field is now {}".format("VISIBLE" if self.show_field else "HIDDEN"))
                    break
                # P to hide/show players and referees
                elif chr(key_code) == 'p':
                    self.show_players_and_referees = not self.show_players_and_referees
                    self.current_frame = video.get_current_frame()
                    print("Players and referees are now {}".format("VISIBLE" if self.show_players_and_referees else "HIDDEN"))
                    break
                # V to hide/show vanishing point segments
                elif chr(key_code) == 'v':
                    self.show_vp_segments = not self.show_vp_segments
                    self.current_frame = video.get_current_frame()
                    print("Vanishing point and segments are now {}".format("VISIBLE" if self.show_vp_segments else "HIDDEN"))
                    break
                # W to go to next frame with marked data
                elif chr(key_code) == 'w':
                    if self.frame_data_list_index < len(frame_data_list) - 1:
                        self.frame_data_list_index += 1
                        self.current_frame = video.get_exact_frame(frame_data_list[self.frame_data_list_index].get_frame_number())
                    break
                # Q to go to previous frame with marked data
                elif chr(key_code) == 'q':
                    if self.frame_data_list_index > 0:
                        self.frame_data_list_index -= 1
                        self.current_frame = video.get_exact_frame(frame_data_list[self.frame_data_list_index].get_frame_number())
                    break
                # DELETE to go back to previous frame
                elif self.keyboard_manager.key_was_pressed(key_code, constants.DELETE_KEY_CODE):
                    self.current_frame = video.get_previous_frame()
                    if self.frame_data_list_index - 1 >= 0 and frame_data_list[self.frame_data_list_index - 1].get_frame_number() == video.get_current_frame_number():
                        self.frame_data_list_index -= 1
                    break
                # SPACE to continue to next frame
                elif self.keyboard_manager.key_was_pressed(key_code, constants.SPACE_KEY_CODE):
                    self.current_frame = video.get_next_frame()
                    if self.frame_data_list_index + 1 < len(frame_data_list) and frame_data_list[self.frame_data_list_index + 1].get_frame_number() == video.get_current_frame_number():
                        self.frame_data_list_index += 1
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
                            print("Exit was aborted. Continue reading dataset.")
                            self.options = self.GENERAL_OPTIONS
                            self._print_available_options()
                            break
                # any other key will do nothing

    def _print_available_options(self):
        height, width = [500, 1000] if self.current_frame is None else self.current_frame.shape[:2]
        black_frame = numpy.zeros((220, width, 3))
        self.frame_printer.print_multiline_text(black_frame, self.options, (5, 30), constants.BGR_WHITE)
        cv2.imshow(self.KEYS_HELP_WINDOW_NAME, black_frame)
        # Only for the first time move the window
        if self.read_started:
            cv2.moveWindow(self.KEYS_HELP_WINDOW_NAME, self.TOP_LEFT_FRAME_WINDOW[1], self.TOP_LEFT_FRAME_WINDOW[0] + height + 100)
            self.read_started = False
