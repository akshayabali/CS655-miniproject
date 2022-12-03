import socket
import util
import json

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
testWord = "tests"
msg = bytes(json.dumps({"hash":util.md5(testWord)}), encoding="utf-8")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        conn.sendall(msg)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)