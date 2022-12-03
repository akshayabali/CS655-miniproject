import string

from flask import Flask, redirect, url_for, request, render_template

import util


app = Flask(__name__)


@app.route('/')
def base():
    return render_template('index.html')


@app.route('/success/<password>')
def success(password):
    return 'Found %s' % password


@app.route('/fail/<password>')
def fail(password):
    return 'Failed %s' % password


@app.route('/crack', methods=['POST'])
def crack():
    input_hash = request.form['nm']
    for c1 in string.ascii_lowercase:
        for c2 in string.ascii_lowercase:
            for c3 in string.ascii_lowercase:
                for c4 in string.ascii_lowercase:
                    for c5 in string.ascii_lowercase:
                        s = c1 + c2 + c3 + c4 + c5
                        if input_hash == util.md5(s):
                            return redirect(url_for('success', password=s))
    return redirect(url_for('fail', password=input_hash))


if __name__ == '__main__':
    # use 0.0.0.0 for web server, localhost for testing
    app.run(host="localhost", debug=True)