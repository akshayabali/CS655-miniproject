import socket
import threading
import time
import util
import json
import argparse

BUFSIZE = 1024

active = False


def increment_char(c):
    if c == 'z':
        return 'A'
    elif c == 'Z':
        return 'a'
    return chr(ord(c) + 1)


def increment_str(s):
    lpart = s.rstrip('z')
    num_replacements = len(s) - len(lpart)
    new_s = lpart[:-1] + increment_char(lpart[-1]) if lpart else 'A'
    new_s += 'A' * num_replacements
    return new_s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=58529)
    parser.add_argument("--host", "-u", type=str, default="127.0.0.1")
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        def heartbeat():
            msg = {"type": "status"}
            while True:
                if active:
                    msg["status"] = "Processing Request"
                    payload = json.dumps(msg)
                    s.sendall(payload.encode())
                else:
                    msg["status"] = "Idle"
                    payload = json.dumps(msg)
                    s.sendall(payload.encode())
                time.sleep(3)
        s.connect((HOST, PORT))
        t = threading.Thread(target=heartbeat)
        t.start()
        while True:
            received = s.recv(BUFSIZE)
            if received:
                msg = {"type":"status"}
                data = json.loads(received)
                active = True
                tobeHashed = data["range"][0]
                while tobeHashed != data["range"][1]:
                    if data["hash"] == util.md5(tobeHashed):
                        msg["status"] = "Hash Found"
                        msg["pass"] = tobeHashed
                        payload = json.dumps(msg)
                        s.sendall(payload.encode())
                        break
                    tobeHashed = increment_str(tobeHashed)
                if tobeHashed == data["range"][1]:
                    if data["hash"] == util.md5(tobeHashed):
                        msg["status"] = "Hash Found"
                        msg["hash"] = data["hash"]
                        msg["pass"] = tobeHashed
                        payload = json.dumps(msg)
                        s.sendall(payload.encode())
                    else:
                        msg["status"] = "Hash Not Found"
                        msg["hash"] = data["hash"]
                        payload = json.dumps(msg)
                        s.sendall(payload.encode())
                    
            active = False
