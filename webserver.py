import socket
import json
import time

from flask import Flask, request, render_template

import util


# config for connecting to master (localhost:7777)
MASTER_HOST = "127.0.0.1"
MASTER_PORT = 7777

# message size for socket receive
DEFAULT_MSG_SIZE = 1024

# host address - will be public routable IP
WEB_SERVER_HOST = "0.0.0.0"

app = Flask(__name__)


@app.route('/')
def base():
    # base html page, allow user to input hash
    return render_template('index.html')


@app.route('/test/display', methods=['GET'])
def result_display():
    # test result rendering
    return render_template("result.html",
                           status="Hash Found", input_hash="abuawd2ijadhiaw",
                           password="AAAAA", resp_time=123456789)


@app.route('/test/range', methods=['POST'])
def range_form():
    # testing - allow user to input password to be hashed and lower/upper bound
    # prepare payload based on user input
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
    # use full lower and upper bound to search hashes
    lower_bound = 'AAAAA'
    upper_bound = 'zzzzz'

    # prepare payload
    payload = {
        "type": "ordered",
        "hash": input_hash,
        "range": [lower_bound, upper_bound]
    }

    # send to master
    start = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((MASTER_HOST, MASTER_PORT))
            sock.sendall(json.dumps(payload).encode())
            msg = sock.recv(DEFAULT_MSG_SIZE).decode()
    except Exception as e:
        # Exception is usually master not available, return status to user
        print(e)
        resp = {
            "status": "No master",
            "input_hash": input_hash,
            "password": "00000",
            "resp_time": time.time() - start
        }
        return resp

    # get resp time
    resp_time = time.time() - start
    resp = json.loads(msg)
    resp['time'] = resp_time
    print(resp)

    # json response for testing/analysis
    return resp


@app.route('/crack', methods=['POST'])
def crack():
    # get input hash from user form, use full lower and upper bound to search hashes
    input_hash = request.form['hash']
    lower_bound = 'AAAAA'
    upper_bound = 'zzzzz'

    # custom bound not implemented from form, will use default values
    if 'lower' in request.form:
        lower_bound = request.form['lower']
    if 'upper' in request.form:
        upper_bound = request.form['upper']

    # prepare payload
    payload = {
        "type": "ordered",
        "hash": input_hash,
        "range": [lower_bound, upper_bound]
    }

    # send to master
    start = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((MASTER_HOST, MASTER_PORT))
            sock.sendall(json.dumps(payload).encode())
            msg = sock.recv(DEFAULT_MSG_SIZE).decode()
    except Exception as e:
        # Exception is usually master not available, return result page saying no master
        print(e)
        status = "No master"
        input_hash = input_hash
        password = "00000"
        resp_time = time.time() - start
        return render_template("result.html", status=status, input_hash=input_hash, password=password, resp_time=resp_time)

    # calculate resp time
    resp_time = time.time() - start
    resp = json.loads(msg)
    resp['time'] = resp_time

    # default status of busy and not found if message is incorrect
    status = resp.get("status", "Busy")
    password = resp.get("pass", "Not Found")
    print(resp)

    # display html page
    return render_template("result.html", status=status, input_hash=input_hash, password=password, resp_time=resp_time)


if __name__ == '__main__':
    # use 0.0.0.0 for web server, localhost for testing
    # default port is 5000
    app.run(host=WEB_SERVER_HOST, debug=False)
