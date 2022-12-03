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
    while True:
        received = s.recv(BUFSIZE)
        if received:
            data = json.loads(received)
            active = True

            tobeHashed = data["range"][0]
            while tobeHashed != data["range"][1]:
                if data["hash"] == util.md5(tobeHashed):
                    s.sendall(b"found hash: "+bytes(tobeHashed, encoding="utf-8"))
                    break
                tobeHashed = increment_str(tobeHashed)

            if tobeHashed == data["range"][1]:
                if data["hash"] == util.md5(tobeHashed):
                    s.sendall(b"could not break hash "+bytes(data["hash"], encoding="utf-8"))
                else:
                    s.sendall(b"found hash: "+bytes(tobeHashed, encoding="utf-8"))
                
        active = False
