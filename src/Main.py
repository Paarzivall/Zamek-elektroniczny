from flask import Flask, render_template, request
from src.Option_1_Actions import Option_1_Actions
app = Flask(__name__)


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


@app.route("/open", methods=['GET', 'POST'])
def open():
    if request.method == 'POST' and request.form['option1_pin'] != '':
        pin = request.form['option1_pin']
        actions = Option_1_Actions(pin)
        if actions.is_correct() is True:
            #tutaj wchodzi jeżeli ma prawdę tj. jeżeli taki pin jest w bazie
            return render_template('open.html', title="Open", option="first_open")
        else:
            return render_template('option1.html', title="Option First")
    else:
        return render_template('option1.html', title="Option First")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888)
