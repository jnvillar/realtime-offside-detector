import cv2


class DatasetGenerator:

    def __init__(self):
        self.current_frame = None
        self.previous_frames = []

    def parse(self):
        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        cap = cv2.VideoCapture('../videos/full_videos/video_1.mp4')

        # Check if camera opened successfully
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

        # Read until video is completed
        frame_number = 1
        while (cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                self.current_frame = frame
                self._print_text(self.current_frame, "Frame: {}".format(frame_number), (5, 30), (255, 255, 255))

                # Display the resulting frame
                cv2.imshow('Frame', self.current_frame)
                cv2.moveWindow('Frame', 200, 200)

                # Press Q on keyboard to  exit
                key_code = cv2.waitKey(0)

                if key_code & 0xFF == 13:

                    field_vertices = []
                    height, width = self.current_frame.shape[:2]

                    cv2.imshow('Frame', self.current_frame)
                    arguments = {"field_vertices": field_vertices}
                    cv2.setMouseCallback('Frame', self._click_event, arguments)
                    while True:
                        self._print_text(self.current_frame, "Delimit field by selecting at least 4 points", (round(width/2) - 320, 30), (255, 255, 255))
                        # Display the resulting frame
                        cv2.imshow('Frame', self.current_frame)
                        second_key_code = cv2.waitKey(0)

                        if second_key_code & 0xFF == 13 and len(field_vertices) >= 4:
                            break
                        elif second_key_code & 0xFF == 8 and len(field_vertices) > 0:
                            del field_vertices[-1]
                            self.current_frame = self.previous_frames.pop(-1)
                            cv2.imshow('Frame', self.current_frame)

                    print(arguments["field_vertices"])

                elif key_code & 0xFF == ord('q'):
                    break

                # remove mouse callback to prevent selecting more points
                cv2.setMouseCallback('Frame', lambda *args : None)

                frame_number += 1

            # Break the loop
            else:
                break

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            self.previous_frames.append(self.current_frame.copy())
            height, width = self.current_frame.shape[:2]
            field_vertices = arguments["field_vertices"]
            point = (x, y)
            red = (0, 0, 255)
            cv2.circle(self.current_frame, point, radius=3, color=red, thickness=-1)
            if len(field_vertices) > 0:
                cv2.line(self.current_frame, field_vertices[-1], point, red, thickness=2)

            field_vertices.append(point)
            # print("Remaining points to select: {}".format(4 - len(field_vertices)))
            cv2.imshow("Frame", self.current_frame)

    def _print_text(self, frame, text, bottom_left_point, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        line_type = 1
        cv2.putText(frame, text, bottom_left_point, font, font_scale, color, line_type)


if __name__ == '__main__':
    DatasetGenerator().parse()
