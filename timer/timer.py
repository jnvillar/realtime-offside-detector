from log.log import *
import time


class Timer:
    TIME = None
    log = Log(None, LoggingPackage.offside_line_drawer)

    @staticmethod
    def start():
        Timer.TIME = time.time()

    @staticmethod
    def stop():
        if Timer.TIME is None:
            Timer.log.log('start not called')

        elapsed_time = time.time() - Timer.TIME
        Timer.TIME = None
        return str(round(elapsed_time * 1000, 2)) + 'ms'
