from flask import Flask, render_template, request, Response
from src.KeyboardOperation.Option_1_Actions import Option_1_Actions
from src.CameraOperation.Camera import VideoCamera
from src.SpreechOperation import Spreech
app = Flask(__name__)
video_stream = VideoCamera()



@app.route('/')
def main_page():
    return render_template('main_page.html', title="Main Page")


@app.route("/option1")
def option_first():
    return render_template('option1.html', title="Option First")


@app.route("/option2")
def option_second():
    return render_template('option2.html', title="Option Second")


@app.route("/option3")
def option_third():
    return render_template('option3.html', title="Option Third")


@app.route("/verify1", methods=['GET', 'POST'])
def verify1():
    if request.method == 'POST' and request.form['option1_pin'] != '':
        pin = request.form['option1_pin']
        actions = Option_1_Actions(pin)
        if actions.is_correct() is True:
            # tutaj wchodzi jeżeli ma prawdę tj. jeżeli taki pin jest w bazie
            # return render_template('option2.html', title="Option2", option="Option Second")
            return option_second()
        else:
            return render_template('option1.html', title="Option First")
    else:
        return render_template('option1.html', title="Option First")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/verify2')
def video_feed():
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/verify3', methods=['GET', 'POST'])
def check():
    if video_stream.get_action() is True:
        video_stream.__del__()
        return option_third()
    else:
        return option_second()


@app.route('/verify4', methods=['GET', 'POST'])
def verify_spreech():
    spr = Spreech.Spreech()
    if spr.controller() is True:
        return render_template('open.html', title="Open")
    else:
        return option_third()


if __name__ == '__main__':
    app.run(host='192.168.0.104', port=8888)
