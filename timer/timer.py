from log.logger import *
import time


class Timer:
    TIME = []
    log = Logger(None, LoggingPackage.offside_line_drawer)

    @staticmethod
    def start():
        Timer.TIME.append(time.time())

    @staticmethod
    def stop():
        if len(Timer.TIME) == 0:
            Timer.log.log('start not called')

        elapsed_time = time.time() - Timer.TIME[-1]
        Timer.TIME.pop()
        return str(round(elapsed_time * 1000, 2)) + 'ms'
