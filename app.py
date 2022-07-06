from flask import Flask, render_template, Response
import os
from datetime import datetime

from env import env_vars
from camera import Camera

app = Flask(__name__)
camera = Camera(rotate=True)

script_path = os.path.abspath(os.path.dirname(__file__))

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Simple frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S.jpg")
    try:
        camera.capture(
            filepath=env_vars["SMB_PHOTO_LOCATION"],
            filename=filename
        )
    except FileNotFoundError:
        camera.capture(
            filepath=os.path.join(script_path, 'photos'),
            filename=filename
        )
    return "", 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env_vars["PORT"], debug=True, threaded=True)
