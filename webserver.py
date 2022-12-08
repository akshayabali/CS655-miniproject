import socket
import json
import time

from flask import Flask, request, render_template

import util


# config
MASTER_HOST = "127.0.0.1"
MASTER_PORT = 7777
DEFAULT_MSG_SIZE = 1024
WEB_SERVER_HOST = "0.0.0.0"

app = Flask(__name__)


@app.route('/')
def base():
    return render_template('index.html')


@app.route('/test/display', methods=['GET'])
def result_display():
    return render_template("result.html",
                           status="Hash Found", input_hash="abuawd2ijadhiaw",
                           password="AAAAA", resp_time=123456789)


@app.route('/test/range', methods=['POST'])
def range_form():
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


@app.route('/crack2/<input_hash>', methods=['POST'])
def crack_json(input_hash):
    lower_bound = 'AAAAA'
    upper_bound = 'zzzzz'

    payload = {
        "type": "ordered",
        "hash": input_hash,
        "range": [lower_bound, upper_bound]
    }

    # send to master
    start = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MASTER_HOST, MASTER_PORT))
        sock.sendall(json.dumps(payload).encode())
        msg = sock.recv(DEFAULT_MSG_SIZE).decode()
    resp_time = start - time.time()
    resp = json.loads(msg)
    resp['time'] = resp_time
    print(resp)

    # json response for testing/analysis
    return resp


@app.route('/crack', methods=['POST'])
def crack():
    input_hash = request.form['hash']
    lower_bound = 'AAAAA'
    upper_bound = 'zzzzz'

    if 'lower' in request.form:
        lower_bound = request.form['lower']
    if 'upper' in request.form:
        upper_bound = request.form['upper']

    payload = {
        "type": "ordered",
        "hash": input_hash,
        "range": [lower_bound, upper_bound]
    }

    # send to master
    start = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MASTER_HOST, MASTER_PORT))
        sock.sendall(json.dumps(payload).encode())
        msg = sock.recv(DEFAULT_MSG_SIZE).decode()
    resp_time = start - time.time()
    resp = json.loads(msg)
    resp['time'] = resp_time
    status = resp.get("status", "Busy")
    password = resp.get("pass", "Not Found")
    print(resp)

    # display html page
    return render_template("result.html", status=status, input_hash=input_hash, password=password, resp_time=resp_time)


if __name__ == '__main__':
    # use 0.0.0.0 for web server, localhost for testing
    app.run(host=WEB_SERVER_HOST, debug=False)
