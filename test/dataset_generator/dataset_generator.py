import cv2

import utils.constants as constants
from video_repository.video_repository import VideoRepository


class DatasetGenerator:
    MIN_VERTICES_TO_SELECT = 4
    WINDOW_NAME = "Dataset generator"

    def __init__(self):
        self.current_frame = None
        self.previous_frames = []
        self.field_vertices = []

    def generate_dataset(self):
        videos_path = "../videos/full_videos/"
        video_name = "video_1.mp4"
        video = VideoRepository(videos_path).get_video(video_name)

        # read until video is completed
        self.current_frame = video.get_next_frame()
        while self.current_frame is not None:

            # display frame with some informative text
            self._print_text(self.current_frame, "Frame: {}".format(video.get_current_frame_number()), (5, 30), constants.BGR_WHITE)
            cv2.imshow(self.WINDOW_NAME, self.current_frame)
            cv2.moveWindow(self.WINDOW_NAME, 200, 200)

            key_code = cv2.waitKey(0)
            # RETURN to get into selection mode
            if self._key_was_pressed(key_code, constants.RETURN_KEY_CODE):
                self._switch_to_selection_mode()
            # ESC to exit
            elif self._key_was_pressed(key_code, constants.ESC_KEY_CODE):
                break
            # any other key to get the next frame

            # remove mouse callback to prevent selecting more points
            cv2.setMouseCallback(self.WINDOW_NAME, lambda *args: None)

            # get next frame to use on the next iteration
            self.current_frame = video.get_next_frame()

    def _switch_to_selection_mode(self):
        self.field_vertices = []
        height, width = self.current_frame.shape[:2]

        # set mouse callback function to capture pixels clicked
        cv2.setMouseCallback(self.WINDOW_NAME, self._click_event)
        while True:
            # display the frame with the text
            self._print_text(self.current_frame,
                             "Delimit field by selecting at least {} points".format(self.MIN_VERTICES_TO_SELECT),
                             (round(width / 2) - 320, 30), constants.BGR_WHITE)
            cv2.imshow(self.WINDOW_NAME, self.current_frame)

            key_code = cv2.waitKey(0)
            # RETURN to confirm selection (only if at least MIN_VERTICES_TO_SELECT vertices were selected)
            if self._key_was_pressed(key_code, constants.RETURN_KEY_CODE) and len(
                    self.field_vertices) >= self.MIN_VERTICES_TO_SELECT:
                print("Selection confirmed: {}.".format(self.field_vertices))
                break
            # DELETE to remove last selected vertex (only if at least 1 vertex was selected)
            elif self._key_was_pressed(key_code, constants.DELETE_KEY_CODE) and len(self.field_vertices) > 0:
                print("Vertex {} deleted from selection.".format(self.field_vertices[-1]))
                del self.field_vertices[-1]
                self.current_frame = self.previous_frames.pop(-1)
                cv2.imshow(self.WINDOW_NAME, self.current_frame)
            # ESC to exit selection mode
            elif self._key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("You have exited selection mode.")
                self.field_vertices = []
                break

        self.previous_frames = []

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            self.previous_frames.append(self.current_frame.copy())
            point = (x, y)
            cv2.circle(self.current_frame, point, radius=3, color=constants.BGR_RED, thickness=-1)
            if len(self.field_vertices) > 0:
                cv2.line(self.current_frame, self.field_vertices[-1], point, constants.BGR_RED, thickness=2)

            self.field_vertices.append(point)
            print("Vertex {} selected.".format(point))
            min_remaining_vertices_to_select = self.MIN_VERTICES_TO_SELECT - len(self.field_vertices)
            if min_remaining_vertices_to_select <= 0:
                print("You can mark more vertices or confirm your selection by pressing RETURN (press ESC to exit selection mode).".format(point))
            else:
                print("You need to mark at least {} more vertices (press ESC to exit selection mode).".format(min_remaining_vertices_to_select))
            cv2.imshow(self.WINDOW_NAME, self.current_frame)

    def _print_text(self, frame, text, bottom_left_point, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        line_type = 1
        cv2.putText(frame, text, bottom_left_point, font, font_scale, color, line_type)

    def _key_was_pressed(self, key_code_to_check, expected_key_code):
        return key_code_to_check & 0xFF == expected_key_code


if __name__ == '__main__':
    DatasetGenerator().generate_dataset()
