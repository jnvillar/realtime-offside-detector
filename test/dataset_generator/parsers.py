import cv2

from domain.line import Line
from test.dataset_generator import colors
from test.dataset_generator.domain import Field, Team, PlayerType, Player
from utils import constants
from utils.utils import FramePrinter, KeyboardManager


class FieldParser:
    MIN_VERTICES_TO_SELECT = 4

    def __init__(self, window_name):
        self.window_name = window_name
        self.current_frame = None
        self.current_frame_to_print = None
        self.previous_frames = []
        self.field_vertices = []
        self.frame_printer = FramePrinter()
        self.keyboard_manager = KeyboardManager()

    def parse(self, frame, frame_data_builder):
        self.current_frame = frame
        self.field_vertices = []
        height, width = self.current_frame.shape[:2]
        selection_confirmed = False

        # set mouse callback function to capture pixels clicked
        cv2.setMouseCallback(self.window_name, self._click_event)
        while True:
            # display the frame with the text
            self.frame_printer.print_text(self.current_frame,
                                          "Delimit field by selecting at least {} points".format(self.MIN_VERTICES_TO_SELECT),
                                          (round(width / 2) - 320, 30), constants.BGR_WHITE)
            self.print_current_frame_with_closed_field_box()

            key_code = cv2.waitKey(0)
            # RETURN to confirm selection (only if at least MIN_VERTICES_TO_SELECT vertices were selected)
            if self.keyboard_manager.key_was_pressed(key_code, constants.RETURN_KEY_CODE) and len(self.field_vertices) >= self.MIN_VERTICES_TO_SELECT:
                print("Selection confirmed: {}.".format(self.field_vertices))
                frame_data_builder.set_field(Field(self.field_vertices))
                selection_confirmed = True
                break
            # DELETE to remove last selected vertex (only if at least 1 vertex was selected)
            elif self.keyboard_manager.key_was_pressed(key_code, constants.DELETE_KEY_CODE) and len(self.field_vertices) > 0:
                print("Vertex {} deleted from selection.".format(self.field_vertices.pop()))
                self.current_frame = self.previous_frames.pop()
            # ESC to exit selection mode
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("You have exited field selection mode.")
                break

        # remove mouse callback to prevent selecting more points
        cv2.setMouseCallback(self.window_name, lambda *args: None)
        self.previous_frames = []
        self.field_vertices = []
        return selection_confirmed

    def get_options(self):
        return [
            " ------------ FIELD SELECTION MODE ------------",
            " LEFT CLICK = select vertex",
            " RETURN = confirm selection (only if at least {} vertices were selected)".format(self.MIN_VERTICES_TO_SELECT),
            " DELETE = remove last selected vertex",
            " ESC = exit field selection mode",
        ]

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            self.previous_frames.append(self.current_frame.copy())
            point = (x, y)
            cv2.circle(self.current_frame, point, radius=3, color=colors.FIELD_BOX_COLOR, thickness=-1)
            if len(self.field_vertices) > 0:
                # draw line between the previous and the last selected points
                cv2.line(self.current_frame, self.field_vertices[-1], point, colors.FIELD_BOX_COLOR, thickness=2)

            self.field_vertices.append(point)
            print("Vertex {} selected.".format(point))
            min_remaining_vertices_to_select = self.MIN_VERTICES_TO_SELECT - len(self.field_vertices)
            if min_remaining_vertices_to_select <= 0:
                print("You can mark more vertices or confirm your selection by pressing RETURN (press ESC to exit field selection mode).")
            else:
                print("You need to mark at least {} more vertices (press ESC to exit field selection mode).".format(min_remaining_vertices_to_select))
            self.print_current_frame_with_closed_field_box()

    def print_current_frame_with_closed_field_box(self):
        frame_to_print = self.current_frame.copy()
        # if at least the minimum number of required vertices are selected, close the box
        if len(self.field_vertices) >= self.MIN_VERTICES_TO_SELECT:
            cv2.line(frame_to_print, self.field_vertices[-1], self.field_vertices[0], colors.FIELD_BOX_COLOR, thickness=2)
        cv2.imshow(self.window_name, frame_to_print)

#######################################################################################################################


class PlayersParser:
    MIN_PLAYERS_TO_SELECT = 1

    def __init__(self, window_name):
        self.window_name = window_name
        self.current_frame = None
        self.previous_frames = []
        self.selected_players = []
        self.frame_printer = FramePrinter()
        self.keyboard_manager = KeyboardManager()
        self.drawing = False
        self.active_selection_last_defense_player = False
        self.active_team = Team.TEAM_ONE
        self.active_player_type = None
        self.last_defense_player_index = None
        self.player_box_vertices = []

    def parse(self, frame, frame_data_builder):
        self.current_frame = frame
        height, width = self.current_frame.shape[:2]
        selection_confirmed = False
        # reset to not use the value from a previous frame
        self.last_defense_player_index = None

        # set mouse callback function to capture pixels clicked
        cv2.setMouseCallback(self.window_name, self._click_event)
        while True:
            # display the frame with the text
            self.frame_printer.print_text(self.current_frame,
                                          "Enclose players in bounding boxes",
                                          (round(width / 2) - 320, 30), constants.BGR_WHITE)
            cv2.imshow(self.window_name, self.current_frame)

            key_code = cv2.waitKey(0)
            # RETURN to confirm selection (only if at least MIN_PLAYERS_TO_SELECT vertices were selected)
            if self.keyboard_manager.key_was_pressed(key_code, constants.RETURN_KEY_CODE) and len(self.selected_players) >= self.MIN_PLAYERS_TO_SELECT and self.last_defense_player_index is not None:
                print("Players selection confirmed: {}.".format(self.selected_players))
                frame_data_builder.set_players(self.selected_players)
                frame_data_builder.set_last_defense_player_index(self.last_defense_player_index)
                selection_confirmed = True
                break
            # ONE to select players from team one
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ONE_KEY_CODE):
                print("Switched to Team ONE selection.")
                self.active_team = Team.TEAM_ONE
            # TWO to select players from team two
            elif self.keyboard_manager.key_was_pressed(key_code, constants.TWO_KEY_CODE):
                print("Switched to Team TWO selection.")
                self.active_team = Team.TEAM_TWO
            # THREE to select referee
            elif self.keyboard_manager.key_was_pressed(key_code, constants.THREE_KEY_CODE):
                print("Switched to REFEREE selection.")
                self.active_team = Team.REFEREE
            # DELETE to remove last selected player (only if at least 1 player was selected)
            elif self.keyboard_manager.key_was_pressed(key_code, constants.DELETE_KEY_CODE) and len(self.selected_players) > 0:
                print("{} deleted from selection.".format(self.selected_players.pop()))
                # Check if last defense player was removed and restore index in such case
                if self.last_defense_player_index is not None and len(self.selected_players) <= self.last_defense_player_index:
                    self.last_defense_player_index = None
                self.current_frame = self.previous_frames.pop()
                cv2.imshow(self.window_name, self.current_frame)
            # ESC to exit selection mode
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("Are you sure you want to exit? All the players selection WILL BE LOST. (Yes/No)")
                exit = False
                while True:
                    key_code_exit = cv2.waitKey(0)
                    if self.keyboard_manager.key_was_pressed(key_code_exit, constants.Y_KEY_CODE):
                        exit = True
                        break
                    elif self.keyboard_manager.key_was_pressed(key_code_exit, constants.N_KEY_CODE):
                        break
                if exit:
                    print("You have exited field selection mode.")
                    break
                else:
                    print("Exit was aborted. Continue parsing.")

        # remove mouse callback to prevent selecting more players
        cv2.setMouseCallback(self.window_name, lambda *args: None)
        self.previous_frames = []
        self.selected_players = []
        return selection_confirmed

    def get_options(self):
        return [
            " ------------ PLAYERS SELECTION MODE ------------",
            " 1 = switch to team ONE selection (red)",
            " 2 = switch to team TWO selection (blue)",
            " 3 = switch to REFEREE selection (yellow)",
            " LEFT CLICK + MOVE = select player/referee bounding box",
            " LEFT CLICK + CMD + MOVE = select goalkeeper bounding box",
            " LEFT CLICK + SHIFT + MOVE = select last defending player bounding box",
            " RETURN = confirm selection (only if at least {} players were selected)".format(self.MIN_PLAYERS_TO_SELECT),
            " DELETE = remove last selected player",
            " ESC = exit players selection mode (confirm exit with Y/N)"
        ]

    def _click_event(self, event, x, y, flags, arguments):
        current_frame_with_box = self.current_frame.copy()
        point = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.active_selection_last_defense_player = False
            self.drawing = True
            self.start_point = (x, y)
            if flags & cv2.EVENT_FLAG_CTRLKEY:
                self.active_player_type = PlayerType.GOALKEEPER
            elif flags & cv2.EVENT_FLAG_SHIFTKEY:
                self.active_selection_last_defense_player = True
                self.active_player_type = PlayerType.FIELD_PLAYER
            else:
                self.active_player_type = PlayerType.FIELD_PLAYER

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            cv2.rectangle(current_frame_with_box, self.start_point, point, self._get_box_color(), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            player_selected = False
            goalkeeper_already_selected = any(player.get_team() == self.active_team and player.get_type() == PlayerType.GOALKEEPER for player in self.selected_players)
            referee_already_selected = any(player.get_team() == self.active_team and self.active_team == Team.REFEREE for player in self.selected_players)
            last_defense_player_already_selected = self.last_defense_player_index is not None
            if self.active_player_type == PlayerType.FIELD_PLAYER:
                if self.active_team == Team.REFEREE:
                    if referee_already_selected:
                        print("You can only select one referee!")
                    elif self.active_selection_last_defense_player:
                        print("You cannot select a referee as last defense player!")
                    else:
                        print("Referee selected.")
                        player_selected = True
                else:
                    if self.active_selection_last_defense_player:
                        if last_defense_player_already_selected:
                            print("You cannot select more than one last defense!")
                        else:
                            print("Last defense player selected.")
                            player_selected = True
                    else:
                        print("Player selected.")
                        player_selected = True
            else:
                if goalkeeper_already_selected:
                    print("You can only select one goalkeeper by team!")
                else:
                    print("Goalkeeper selected.")
                    player_selected = True

            if player_selected:
                self.selected_players.append(Player(self.active_player_type, self.active_team, [self.start_point, point]))
                if self.active_selection_last_defense_player:
                    self.last_defense_player_index = len(self.selected_players) - 1

                self.previous_frames.append(self.current_frame.copy())
                cv2.rectangle(current_frame_with_box, self.start_point, point, self._get_box_color(), 2)
                self.current_frame = current_frame_with_box

                min_remaining_players_to_select = self.MIN_PLAYERS_TO_SELECT - len(self.selected_players)
                if min_remaining_players_to_select <= 0 and self.last_defense_player_index is not None:
                    print("You can select more players or confirm your selection by pressing RETURN (press ESC to exit players selection mode).")
                else:
                    if min_remaining_players_to_select <= 0:
                        print("You need to include the last defense player in your selection (press ESC to exit players selection mode).")
                    else:
                        print("You need to select at least {} more players, including the last defense (press ESC to exit players selection mode).".format(min_remaining_players_to_select))


        cv2.imshow(self.window_name, current_frame_with_box)

    def _get_box_color(self):
        if self.active_selection_last_defense_player:
            return colors.TEAM_BOX_COLOR_LAST_DEFENSE.get(self.active_team)
        return colors.TEAM_BOX_COLOR.get(self.active_team).get(self.active_player_type)

#######################################################################################################################

class VanishingPointParser:
    POINTS_TO_SELECT = 4

    def __init__(self, window_name):
        self.window_name = window_name
        self.current_frame = None
        self.current_frame_to_print = None
        self.previous_frames = []
        self.segment_points = []
        self.frame_printer = FramePrinter()
        self.keyboard_manager = KeyboardManager()

    def parse(self, frame, frame_data_builder):
        self.current_frame = frame
        self.segment_points = []
        height, width = self.current_frame.shape[:2]
        selection_confirmed = False

        # set mouse callback function to capture pixels clicked
        cv2.setMouseCallback(self.window_name, self._click_event)
        while True:
            # display the frame with the text
            self.frame_printer.print_text(self.current_frame,
                                          "Mark vanishing point by selecting 2 segments",
                                          (round(width / 2) - 320, 30), constants.BGR_WHITE)
            self.print_current_frame_with_segments()

            key_code = cv2.waitKey(0)
            # RETURN to confirm selection (only if exactly POINTS_TO_SELECT points were selected)
            if self.keyboard_manager.key_was_pressed(key_code, constants.RETURN_KEY_CODE) and len(self.segment_points) == self.POINTS_TO_SELECT:
                print("Selection confirmed: {}.".format(self.segment_points))
                frame_data_builder.set_vanishing_point_segments([Line(self.segment_points[0], self.segment_points[1]), Line(self.segment_points[2], self.segment_points[3])])
                selection_confirmed = True
                break
            # DELETE to remove last selected vertex (only if at least 1 vertex was selected)
            elif self.keyboard_manager.key_was_pressed(key_code, constants.DELETE_KEY_CODE) and len(self.segment_points) > 0:
                print("Point {} deleted from selection.".format(self.segment_points.pop()))
                self.current_frame = self.previous_frames.pop()
            # ESC to exit selection mode
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("You have exited vanishing point selection mode.")
                break

        # remove mouse callback to prevent selecting more points
        cv2.setMouseCallback(self.window_name, lambda *args: None)
        self.previous_frames = []
        self.segment_points = []
        return selection_confirmed

    def get_options(self):
        return [
            " ------------ VANISHING POINT SELECTION MODE ------------",
            " LEFT CLICK = select segment point",
            " RETURN = confirm selection (only if {} points were selected)".format(self.POINTS_TO_SELECT),
            " DELETE = remove last selected point",
            " ESC = exit field selection mode",
        ]

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            # if 4 points were already selection, reject this point
            if len(self.segment_points) == 4:
                print("Two segments are already selected. Confirm your selection.")
                return

            self.previous_frames.append(self.current_frame.copy())
            point = (x, y)
            cv2.circle(self.current_frame, point, radius=3, color=colors.VP_SEGMENTS_COLOR, thickness=-1)

            self.segment_points.append(point)
            if len(self.segment_points) > 0 and len(self.segment_points) % 2 == 0:
                # draw line between the previous and the last selected points
                cv2.line(self.current_frame, self.segment_points[-1], point, colors.VP_SEGMENTS_COLOR, thickness=2)

            print("Point {} selected.".format(point))
            remaining_vertices_to_select = self.POINTS_TO_SELECT - len(self.segment_points)
            if remaining_vertices_to_select <= 0:
                print("You need to mark {} more points (press ESC to exit vanishing point selection mode).".format(remaining_vertices_to_select))
            self.print_current_frame_with_segments()

    def print_current_frame_with_segments(self):
        frame_to_print = self.current_frame.copy()

        # if the first segment was already selected, print it
        if len(self.segment_points) >= 2:
            cv2.line(frame_to_print, self.segment_points[0], self.segment_points[1], colors.VP_SEGMENTS_COLOR, thickness=2)

        # if the second segment was already selected, print it
        if len(self.segment_points) == 4:
            cv2.line(frame_to_print, self.segment_points[2], self.segment_points[3], colors.VP_SEGMENTS_COLOR, thickness=2)

        cv2.imshow(self.window_name, frame_to_print)