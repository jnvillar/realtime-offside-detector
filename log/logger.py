from domain.status import *
from enum import Enum
import datetime
import json


class LoggingPackage(Enum):
    field_detector = "🏟️"
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
    offside_detector = "🎛️"


class LogLevel(Enum):
    debug = (0, 'DEBUG')
    info = (1, 'INFO')
    warning = (2, 'WARNING')
    error = (3, 'ERROR')
    critical = (4, 'CRITICAL')


class Logger:
    STATUS = None

    @staticmethod
    def initialize(config):
        Logger.STATUS = config.get('status', Status.inactive)

    # class_that_is_logging = class
    # package = LoggingPackage
    def __init__(self, class_that_is_logging, package):
        self.class_that_is_logging = class_that_is_logging
        self.package = package
        self.log_level = LogLevel.debug

    # message = string
    # params  = dict
    def log(self, message: str, params: dict = {}, level: LogLevel = LogLevel.debug):
        if self.STATUS != Status.active:
            return

        if self.log_level.value <= level.value:
            print(
                '[' + str(datetime.datetime.now()) + ']' + ' ' +
                '[' + str(self.log_level.value[1]) + ']' + ' ' +
                str(self.package.value) + ' ' +
                self.class_that_is_logging.__class__.__name__ + ': ' + message + " " + print_dict(params))


def print_dict(params: dict):
    if len(params) == 0:
        return ''

    json_object = json.dumps(params, default=lambda o: o.__repr__(), separators=(',', ': '))
    return str(json_object)
