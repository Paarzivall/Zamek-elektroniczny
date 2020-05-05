from flask import Flask, render_template, request, Response, stream_with_context
from time import sleep
from src.KeyboardOperation.Option_1_Actions import Option_1_Actions
from src.CameraOperation.Camera import VideoCamera
from src.SpreechOperation import Spreech
from src.Controller import FailedCounter
from src.SpreechOperation import SpreechAnalyzer
app = Flask(__name__)
video_stream = VideoCamera()
# licznik pod niepowodzenia logowania
# default ustawiony na 3 niepowodzenia
failed = FailedCounter.FailedCounter.get_instance()


@app.route('/')
def main_page():
    """
    :return: main page if failed counter is valid or blocking page if is not
    """
    if failed.is_valid():
        return render_template('main_page.html', title="Main Page")
    else:
        return block()


@app.route('/main_page')
def main_p():
    """
    method to clearing failed counter and opening main page
    :return: main page
    """
    failed.clear_count()
    return render_template('main_page.html', title="Main Page")


@app.route("/option1")
def option_first():
    """

    :return: form page id failed counter is valid or blocking page if is not
    """
    if failed.is_valid():
        return render_template('option1.html', title="Option First", show=True)
    else:
        return block()


@app.route("/option2")
def option_second():
    """

    :return: form page if failed counter is valid or blocking page if is not
    """
    if failed.is_valid():
        return render_template('option2.html', title="Option Second", show=True)
    else:
        return block()


@app.route("/option3")
def option_third():
    """

    :return: page with images from camera or blocking page
    """
    if failed.is_valid():
        return render_template('option3.html', title="Option Third", show=True)
    else:
        return block()


@app.route("/option4")
def option_fourth():
    """

    :return: page with starter for sound recognize mechanism
    """
    if failed.is_valid():
        return render_template('option4.html', title="Option Fourth", show=True)
    else:
        return block()


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
    """

    :param camera: field in vebsite
    :return: frame after recognize
    """
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/verify2')
def video_feed():
    """

    :return: converted frame to website
    """
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/block")
def block():
    """

    :return: block page and starting website timeout mechanism
    """
    return render_template('block.html', title="Blocked")


@app.route('/verify3', methods=['GET', 'POST'])
def check():
    """
    method to management and checking second method authentication
    :return: next page if validation is valid or actual page if is not valid and failed counter is valid or blocked page
    """
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
    """
    method to management and checking third method authentication
    :return: next page if validation is valid or actual page if is not valid and failed counter is valid or blocked page
    """
    spr = Spreech.Spreech()
    if spr.controller() is True:
        failed.clear_count()
        # return render_template('open.html', title="Open", show=True)
        return option_fourth()
    else:
        failed.add()
        if failed.is_valid():
            return option_third()
        else:
            return block()


@app.route('/verify5', methods=['GET', 'POST'])
def analyze_spreech():
    """
    method to management and checking fourth method authentication
    :return: next page if validation is valid or actual page if is not valid and failed counter is valid or blocked page
    """
    spreech = SpreechAnalyzer.SpreechAnalyzer()
    if spreech.recognize() is True:
        failed.clear_count()
        return render_template('open.html', title="Open", show=True)
    else:
        failed.add()
        if failed.is_valid():
            return option_fourth()
        else:
            return block()


if __name__ == '__main__':
    app.run(host='192.168.0.104', port=8888)


