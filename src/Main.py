from flask import Flask, render_template, request, Response
from src.KeyboardOperation.Option_1_Actions import Option_1_Actions
from src.CameraOperation.Camera import VideoCamera
from src.SpreechOperation import Spreech
from src.Controller import FailedCounter
app = Flask(__name__)
video_stream = VideoCamera()
# licznik pod niepowodzenia logowania
# default ustawiony na 3 niepowodzenia
failed = FailedCounter.FailedCounter.get_instance()


@app.route('/')
def main_page():
    if failed.is_valid():
        return render_template('main_page.html', title="Main Page")
    else:
        return block()


@app.route("/option1")
def option_first():
    return render_template('option1.html', title="Option First", show=True)


@app.route("/option2")
def option_second():
    return render_template('option2.html', title="Option Second", show=True)


@app.route("/option3")
def option_third():
    return render_template('option3.html', title="Option Third", show=True)


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
            return render_template('option1.html', title="Option First", show=True)
    else:
        return render_template('option1.html', title="Option First", show=True)


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
        failed.add()
        if failed.is_valid():
            return option_second()
        else:
            return block()


@app.route('/verify4', methods=['GET', 'POST'])
def verify_spreech():
    spr = Spreech.Spreech()
    if spr.controller() is True:
        failed.__del__()
        return render_template('open.html', title="Open", show=True)
    else:
        failed.add()
        if failed.is_valid():
            return option_third()
        else:
            return block()


@app.route("/block")
def block():
    return render_template('block.html', title="Blocked")


if __name__ == '__main__':
    app.run(host='192.168.0.104', port=8888)


