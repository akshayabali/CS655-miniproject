import socket
import threading
import time
import util
import json
import string

HOST = "localhost"
PORT = 5000
BUFSIZE = 1024

active = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    def heartbeat():
        while True:
            if active:
                s.sendall(b"Processing Request")
            else:
                s.sendall(b"Idle")
            time.sleep(3)
    s.connect((HOST, PORT))
    t = threading.Thread(target=heartbeat)
    t.start()
    break_flag = False
    while True:
        received = s.recv(BUFSIZE)
        if received:
            data = json.loads(received)
            active = True
            for c1 in string.ascii_lowercase:
                for c2 in string.ascii_lowercase:
                    for c3 in string.ascii_lowercase:
                        for c4 in string.ascii_lowercase:
                            for c5 in string.ascii_lowercase:
                                h = c1 + c2 + c3 + c4 + c5
                                if data["hash"] == util.md5(h):
                                    s.sendall(b"found hash: "+bytes(h, encoding="utf-8"))
                                    break_flag = True
                                    break
                            if break_flag:
                                break
                        if break_flag:
                            break
                    if break_flag:
                        break
                if break_flag:
                    break

            if not break_flag:
                s.sendall(b"could not break hash "+data["hash"])
        active = False
