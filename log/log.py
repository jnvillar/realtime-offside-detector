from enum import Enum


class LoggingPackage(Enum):
    player_detector = "🏃"
    player_sorter = "👕"
    player_tracker = "🕵🏽‍"
    team_classifier = "🤼"
    player_finder = "🔍"
    orientation_detector = "🧭"
    video_repository = "🗄️"
    vanishing_point = "🖼️"
    test = "🧪"
    frame_utils = "🔨"
    offside_line_drawer = "📏"


class LogLevel(Enum):
    debug = 0
    info = 1
    warning = 2
    error = 3
    critical = 4


class Log:

    # class_that_is_logging = class
    # package = LoggingPackage
    def __init__(self, class_that_is_logging, package):
        self.class_that_is_logging = class_that_is_logging
        self.package = package
        self.log_level = LogLevel.debug

    # message = string
    # params  = dict
    def log(self, message: str, params: dict = None, level: LogLevel = LogLevel.debug):
        if params is None:
            params = ''
        if self.log_level.value <= level.value:
            print(
                str(self.package.value) + ' ' +
                self.class_that_is_logging.__class__.__name__ + ': ' + message + " " + str(params))
