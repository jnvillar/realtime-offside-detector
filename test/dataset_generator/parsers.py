import cv2

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
            cv2.circle(self.current_frame, point, radius=3, color=constants.BGR_RED, thickness=-1)
            if len(self.field_vertices) > 0:
                # draw line between the previous and the last selected points
                cv2.line(self.current_frame, self.field_vertices[-1], point, constants.BGR_RED, thickness=2)

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
            cv2.line(frame_to_print, self.field_vertices[-1], self.field_vertices[0], constants.BGR_RED, thickness=2)
        cv2.imshow(self.window_name, frame_to_print)

#######################################################################################################################


class PlayersParser:
    MIN_PLAYERS_TO_SELECT = 1
    TEAM_BOX_COLOR = {
        Team.TEAM_ONE: {PlayerType.FIELD_PLAYER: constants.BGR_RED, PlayerType.GOALKEEPER: constants.BGR_DARK_RED},
        Team.TEAM_TWO: {PlayerType.FIELD_PLAYER: constants.BGR_BLUE, PlayerType.GOALKEEPER: constants.BGR_DARK_BLUE},
        Team.REFEREE: {PlayerType.FIELD_PLAYER: constants.BGR_YELLOW}
    }
    EMPTY_PLAYER_SELECTION = {
        Team.TEAM_ONE: {PlayerType.FIELD_PLAYER: [], PlayerType.GOALKEEPER: []},
        Team.TEAM_TWO: {PlayerType.FIELD_PLAYER: [], PlayerType.GOALKEEPER: []}
    }

    def __init__(self, window_name):
        self.window_name = window_name
        self.current_frame = None
        self.previous_frames = []
        self.selected_players = []
        self.frame_printer = FramePrinter()
        self.keyboard_manager = KeyboardManager()
        self.drawing = False
        self.active_team = Team.TEAM_ONE
        self.active_player_type = None
        self.player_box_vertices = []

    def parse(self, frame, frame_data_builder):
        self.current_frame = frame
        height, width = self.current_frame.shape[:2]
        selection_confirmed = False

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
            if self.keyboard_manager.key_was_pressed(key_code, constants.RETURN_KEY_CODE) and len(self.selected_players) >= self.MIN_PLAYERS_TO_SELECT:
                print("Players selection confirmed: {}.".format(self.selected_players))
                frame_data_builder.set_players(self.selected_players)
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
                self.current_frame = self.previous_frames.pop()
                cv2.imshow(self.window_name, self.current_frame)
            # ESC to exit selection mode
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("You have exited field selection mode.")
                break

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
            " RETURN = confirm selection (only if at least {} players were selected)".format(self.MIN_PLAYERS_TO_SELECT),
            " DELETE = remove last selected player",
            " ESC = exit players selection mode"
        ]

    def _click_event(self, event, x, y, flags, arguments):
        current_frame_with_box = self.current_frame.copy()
        point = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            if flags & cv2.EVENT_FLAG_CTRLKEY:
                self.active_player_type = PlayerType.GOALKEEPER
            else:
                self.active_player_type = PlayerType.FIELD_PLAYER

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            cv2.rectangle(current_frame_with_box, self.start_point, point, self._get_box_color(), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            player_selected = False
            goalkeeper_already_selected = any(player.get_team() == self.active_team and player.get_type() == PlayerType.GOALKEEPER for player in self.selected_players)
            referee_already_selected = any(player.get_team() == self.active_team and self.active_team == Team.REFEREE for player in self.selected_players)
            if self.active_player_type == PlayerType.FIELD_PLAYER:
                if self.active_team == Team.REFEREE:
                    if referee_already_selected:
                        print("You can only select one referee!")
                    else:
                        print("Referee selected.")
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
                self.previous_frames.append(self.current_frame.copy())
                cv2.rectangle(current_frame_with_box, self.start_point, point, self._get_box_color(), 2)
                self.current_frame = current_frame_with_box

                min_remaining_players_to_select = self.MIN_PLAYERS_TO_SELECT - len(self.selected_players)
                if min_remaining_players_to_select <= 0:
                    print("You can select more players or confirm your selection by pressing RETURN (press ESC to exit players selection mode).")
                else:
                    print("You need to select at least {} more players (press ESC to exit players selection mode).".format(min_remaining_players_to_select))

        cv2.imshow(self.window_name, current_frame_with_box)

    def _get_box_color(self):
        return self.TEAM_BOX_COLOR.get(self.active_team).get(self.active_player_type)

#######################################################################################################################


class DefendingTeamParser:

    def __init__(self, window_name):
        self.window_name = window_name
        self.defending_team = Team.TEAM_ONE
        self.frame_printer = FramePrinter()
        self.keyboard_manager = KeyboardManager()

    def parse(self, frame, frame_data_builder):
        height, width = frame.shape[:2]
        selection_confirmed = False

        while True:
            # display the frame with the text
            self.frame_printer.print_text(frame, "Select defending team (default selection is team ONE)", (round(width / 2) - 320, 30), constants.BGR_WHITE)
            cv2.imshow(self.window_name, frame)

            key_code = cv2.waitKey(0)
            # RETURN to confirm selection
            if self.keyboard_manager.key_was_pressed(key_code, constants.RETURN_KEY_CODE):
                print("Defending team selection confirmed: {}.".format(self.defending_team))
                frame_data_builder.set_defending_team(self.defending_team)
                selection_confirmed = True
                break
            # ONE to select team one as defending team
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ONE_KEY_CODE):
                print("Team ONE selected as defending team.")
                self.defending_team = Team.TEAM_ONE
            # TWO to select team two as defending team
            elif self.keyboard_manager.key_was_pressed(key_code, constants.TWO_KEY_CODE):
                print("Team TWO selected as defending team.")
                self.defending_team = Team.TEAM_TWO
            # ESC to exit selection mode
            elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                print("You have exited defending team selection mode.")
                break

        return selection_confirmed

    def get_options(self):
        return [
            " ------------ DEFENDING TEAM SELECTION MODE ------------",
            " 1 = set team ONE (red) as defending team",
            " 2 = set team TWO (blue) as defending team",
            " RETURN = confirm selection"
            " ESC = exit defending selection mode"
        ]
