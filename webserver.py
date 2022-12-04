import string
import socket
import json

from flask import Flask, redirect, url_for, request, render_template

import util


app = Flask(__name__)


@app.route('/')
def base():
    return render_template('index.html')


@app.route('/test/range', methods=['POST'])
def test_range():
    # get input
    input_pass = request.form['pass']
    lower_bound = request.form['lower']
    upper_bound = request.form['upper']
    payload = {
        "hash": util.md5(input_pass), "range": [lower_bound, upper_bound]
    }
    msg = bytes(json.dumps(payload), encoding="utf-8")

    # send to worker
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 5001))
        sock.sendall(msg)
        resp = sock.recv(1024).decode()
    return resp


@app.route('/test/socket')
def test_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("10.10.2.1", 5000))
    sock.sendall("Test message".encode())
    resp = sock.recv(1024).decode()
    sock.close()
    return resp


@app.route('/crack', methods=['POST'])
def crack():
    input_hash = request.form['hash']
    for c1 in string.ascii_lowercase:
        for c2 in string.ascii_lowercase:
            for c3 in string.ascii_lowercase:
                for c4 in string.ascii_lowercase:
                    for c5 in string.ascii_lowercase:
                        s = c1 + c2 + c3 + c4 + c5
                        if input_hash == util.md5(s):
                            return s
    return 'Fail'


if __name__ == '__main__':
    # use 0.0.0.0 for web server, localhost for testing
    app.run(host="0.0.0.0", debug=True)
