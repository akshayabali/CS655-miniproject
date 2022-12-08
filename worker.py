import socket
import threading
import time
import util
import json
import argparse

BUFSIZE = 1024

active = False


def increment_char(c): #Increments a char by one in Alphabetical Order
    if c == 'z':
        return 'A'
    elif c == 'Z':
        return 'a'
    return chr(ord(c) + 1)


def increment_str(s): #Increments a string by one in Alphabetical Order
    lpart = s.rstrip('z')
    num_replacements = len(s) - len(lpart)
    new_s = lpart[:-1] + increment_char(lpart[-1]) if lpart else 'A'
    new_s += 'A' * num_replacements
    return new_s


if __name__ == '__main__':
    #Parses the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=58529)
    parser.add_argument("--host", "-u", type=str, default="127.0.0.1")
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    #Creating the socket to connect to the manager
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        def heartbeat(): #Sends and heartbeat every 3 seconds
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
        t = threading.Thread(target=heartbeat) #Create the heartbeat thread
        t.start()
        while True: 
            received = s.recv(BUFSIZE) #Receive the work
            if received: #Check if received work
                msg = {"type":"status"}
                data = json.loads(received)
                active = True
                tobeHashed = data["range"][0]
                #Calculate Hash until find or reach the end
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
