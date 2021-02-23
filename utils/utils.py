import cv2


class FramePrinter:

    def print_text(self, frame, text, bottom_left_point, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        line_type = 1
        cv2.putText(frame, text, bottom_left_point, font, font_scale, color, line_type)

    def print_multiline_text(self, frame, text_lines, bottom_left_point_first_line, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.6
        line_type = 1
        offset = 0
        for line in text_lines:
            cv2.putText(frame, line, (bottom_left_point_first_line[0], bottom_left_point_first_line[1] + offset), font, font_scale, color, line_type)
            offset += 20


class KeyboardManager:

    def key_was_pressed(self, key_code_to_check, expected_key_code):
        return key_code_to_check & 0xFF == expected_key_code

    def is_lowercase_alphabet_char_code(self, key_code):
        return 97 <= key_code <= 122
