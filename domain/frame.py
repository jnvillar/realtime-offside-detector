class Frame:
    def __init__(self, frame, frame_number, ret):
        self.frame = frame
        self.frame_number = frame_number
        self.ret = ret

    def get_frame_number(self):
        return self.frame_number

    def get_frame(self):
        return self.frame

    def is_last_frame(self):
        return not self.ret
