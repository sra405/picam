# import cv2
# import time
# import numpy as np

# class Camera:
#     def __init__(self, rotate=False):
#         # self.camera = cv2.VideoCapture(0)
#         with picamera.PiCamera(resolution='1280x960', framerate=16) as camera:
#             output = StreamingOutput()
#             if rotate:
#                 camera.vflip = True
#             camera.start_recording(output, format='mjpeg')
#         self.rotate = rotate
    
#     def get_frame(self):
#         success, frame = self.camera.read()
#         if not success:
#             return np.array([])
#         if self.rotate:
#             frame = cv2.rotate(frame, cv2.ROTATE_180)
#         return frame
    
#     def stream(self, fps=15):
#         while True:
#             frame = self.get_frame()
#             if frame.any():
#                 ret, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 yield(b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#                 time.sleep(1/fps)
    
#     def capture(self, filename):
#         frame = self.get_frame()
#         if frame.any():
#             cv2.imwrite(filename, frame)

import time
import io
import threading
import picamera


class Camera:
    def __init__(self, rotate=False):
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.rotate = rotate

    def initialize(self):
        if self.thread is None:
            # start background frame thread
            self.thread = threading.Thread(target=self._thread)
            self.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0.1)

    def get_frame(self):
        self.last_access = time.time()
        self.initialize()
        return self.frame
    
    def capture(self, filename='foo.jpg'):
        self.get_frame()
        with open(filename, 'wb') as binary_file:
            binary_file.write(self.frame)

    def _thread(self):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (1280, 960)
            camera.framerate = 20
            camera.hflip = True
            if self.rotate:
                camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                self.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - self.last_access > 10:
                    break
        self.thread = None
