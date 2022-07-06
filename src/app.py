from flask import Flask, render_template, Response
import os

from camera import Camera

app = Flask(__name__)
camera = Camera(rotate=True)

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
    # return Response(camera.stream(),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    camera.capture('foo.jpg')
    return "None"

if __name__ == "__main__":
    
    # set port to host server
    if os.environ.get('PORT'):
        port = os.environ.get('PORT')
    else:
        port = 5000

    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
