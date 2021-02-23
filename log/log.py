from enum import Enum


class LoggingPackage(Enum):
    player_detector = "🏃"
    player_sorter = "👕"
    team_classifier = "🤼"
    orientation_detector = "🧭"
    video_repository = "🎥"
    test = "🧪"
    frame_utils = "🔨"


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
    def log(self, message: str, params: dict, level: LogLevel = LogLevel.debug):
        if self.log_level.value <= level.value:
            print(
                str(self.package.value) + ' ' +
                self.class_that_is_logging.__class__.__name__ + ': ' + message + " " + str(params))
