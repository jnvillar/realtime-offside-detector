from enum import Enum


class LoggingPackage(Enum):
    player_detector = "🏃"


class Log:

    # class_that_is_logging = class
    # package = LoggingPackage
    def __init__(self, class_that_is_logging, package):
        self.class_that_is_logging = class_that_is_logging
        self.package = package

    # message = string
    # params  = dict
    def log(self, message, params):
        print(str(self.package.value) + ' ' + self.class_that_is_logging.__class__.__name__ + ': ' + message + " " + str(
            params))
