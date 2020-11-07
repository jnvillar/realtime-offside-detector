class FrameUtils:

    def percentage_of_frame(self, frame, area):
        width, height = len(frame), len(frame[0])
        total_pixels = width * height
        return (area / total_pixels) * 100
