from log.logger import *
import time


class Timer:
    TIME = {}
    log = Logger(None, LoggingPackage.offside_line_drawer)

    @staticmethod
    def start(id: str):
        if Timer.TIME.get(id, None) is not None:
            Timer.log.log('stop not called with {}'.format(id))
            exit()
        Timer.TIME[id] = (time.time())

    @staticmethod
    def stop(id: str):

        try:
            elapsed_time = time.time() - Timer.TIME[id]
        except:
            Timer.log.log('start not called with {}'.format(id))
            exit()

        del Timer.TIME[id]
        return str(round(elapsed_time * 1000, 2)) + 'ms'
