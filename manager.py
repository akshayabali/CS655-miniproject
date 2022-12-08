import argparse
import socket
import json
import threading
import time
from enum import Enum
import traceback

'''
Manager class receives a task from its manager and handles the division
and forwarding the work to its underlings, based on the hash rate of the underlings.
'''

# The enum class for calculating the hash
class Alphabet(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7
    I = 8
    J = 9
    K = 10
    L = 11
    M = 12
    N = 13
    O = 14
    P = 15
    Q = 16
    R = 17
    S = 18
    T = 19
    U = 20
    V = 21
    W = 22
    X = 23
    Y = 24
    Z = 25
    a = 26
    b = 27
    c = 28
    d = 29
    e = 30
    f = 31
    g = 32
    h = 33
    i = 34
    j = 35
    k = 36
    l = 37
    m = 38
    n = 39
    o = 40
    p = 41
    q = 42
    r = 43
    s = 44
    t = 45
    u = 46
    v = 47
    w = 48
    x = 49
    y = 50
    z = 51

class Manager:
    def __init__(self, HOST, MPORT, LPORT):
        # Global Objects
        self.children = [{}] #List of children as a list of objects
        self.manager = {
            "manager_port": LPORT,  # Port number of the manager
            "manager_socket": None  # Socket for the connection between manager and it's children
        }

        self.master = {
            "master_ip": HOST,  # IP of the master
            "master_port": MPORT,  # Port number of the master
            "master_socket": None  # Socket for the connection between manager and it's parent/master
        }

        self.worker_timer = [] # Stores the time when a heartbeat is received from the worker

        self.status = {} # Stores the current status of all the workers
        self.found = ""  # Password of hash
        self.lhash = ""  # Last hash processed
        self.hash = ""  # Hash to be processed, blank if idle
        self.lower = -1  # Lower range of request received from the parent node
        self.upper = -1  # Higher range of request received from the parent node
        self.clower = -1 # Lower range of processing request
        self.cupper = -1 # Higher range of processing request
        self.queue = { # Queue of what work is currenly handled by which worker
            0 : [0, 0]
        }
        self.lock = threading.Lock()
        self.req_timer = {} # Stores the time when a processing request was sent to the worker

    # Takes a base 10 integer and converts it into a base 52 character string
    def convert_to_string(self, number):
        string = ["", "", "", "", ""]
        for i in range(4, -1, -1):
            Q = number // 52
            R = number % 52
            string[i] = Alphabet(R).name
            number = Q
        return "".join(string)

    # Takes a base 52 character string and converts to base 10 integer
    def convert_to_int(self, s: str) -> int:
        val = 0
        idx = 0
        for i in range(4, -1, -1):
            val = val + Alphabet[s[i]].value * (52**idx)
            idx = idx + 1
        return val

    # Distributes the work among the workers
    def give_work_worker(self, connection, ID, skip=False):
        while connection:
            try:
                while True:
                    if not skip:
                        # Will close the connection with the worker
                        # if the worker hasn't sent a heartbeat in 10 seconds 
                        if (time.time() - self.worker_timer[ID - 1]) > 10:
                            print(self.worker_timer[ID - 1],time.time()," Worker Died")
                            connection.close()
                            break
                    received = connection.recv(1024)
                    print(ID-1, " Received: ", received)
                    message = json.loads(received.decode("utf-8"))
                    if message["type"] == "status":
                        self.status[ID - 1] = message["status"]
                        if self.status[ID - 1]:
                            # Sending the work, if worker's status is idle
                            if self.status[ID - 1] == "Idle" and self.hash != "":
                                self.lock.acquire()
                                self.clower = self.lower
                                self.cupper = self.lower + 1000
                                if(self.cupper > self.upper):
                                    self.cupper = self.upper
                                self.queue[ID] = [self.clower, self.cupper]
                                sending_data = {"hash" : self.hash,"type": "ordered", "range" : [self.convert_to_string(self.clower), self.convert_to_string(self.cupper)]}
                                self.lock.release()
                                sending_data = json.dumps(sending_data)
                                print(ID-1," Sending: ",sending_data)
                                connection.sendall(sending_data.encode())
                                self.req_timer[ID-1]= time.time()
                            # Resetting the variables if hash is found and
                            # waiting for more work from the parent
                            elif self.status[ID - 1].startswith("Hash Found"):
                                print("Found")
                                self.lock.acquire()
                                self.lhash = self.hash
                                self.found = message["pass"]
                                self.hash = ""
                                self.lower = -1
                                self.upper = -1
                                self.lock.release()

                            elif self.status[ID - 1].startswith("Hash Not Found"):
                                # Resetting the variables and sending "hash not found" to the parent
                                if(self.cupper >= self.upper):
                                    with self.lock:
                                        msg = {"type":"status"}
                                        msg["status"] = "Hash Not Found"
                                        msg["hash"] = self.hash
                                        sending_data = json.dumps(msg)
                                        self.master["master_socket"].sendall(sending_data.encode())
                                        self.lhash = self.hash
                                        self.hash = ""
                                        self.lower = -1
                                        self.upper = -1
                                # Calculating the hash rate of the worker and sending the work accordingly
                                else:
                                    hash_rate = 100
                                    work = 1000
                                    if (ID -1) in self.req_timer:
                                        time_taken = time.time() - self.req_timer[ID - 1]
                                        rang = self.queue[ID][1] - self.queue[ID][0]
                                        hash_rate = rang // time_taken
                                        work = hash_rate * 10
                                    self.lock.acquire()
                                    self.clower = self.cupper + 1
                                    self.cupper = self.clower + work
                                    if(self.cupper > self.upper):
                                        self.cupper = self.upper
                                    self.queue[ID] = [self.clower, self.cupper]
                                    sending_data = {"hash": self.hash,"type": "ordered", "range" : [self.convert_to_string(self.clower), self.convert_to_string(self.cupper)]}
                                    self.lock.release()
                                    sending_data = json.dumps(sending_data)
                                    print("Sending to ",ID-1 , " : ",sending_data, " Hash Rate : ",hash_rate)
                                    connection.sendall(sending_data.encode())
                                    self.req_timer[ID - 1] = time.time()
                            self.worker_timer[ID - 1] = time.time() # Storing the time of sending a processing request
            except Exception as e:
                print(e)
                traceback.print_exc()
                time.sleep(5)

    # Function to receive the work from the master
    def give_work_master(self, connection, ID, skip=False):
        try:
            while True:
                received = connection.recv(1024)
                print(ID-1, " Received from master: ", received)
                message = json.loads(received.decode("utf-8"))
                if message["type"] == "ordered":
                    if self.hash == "":
                        with self.lock:
                            self.hash = message["hash"]
                            self.lower = self.convert_to_int(message["range"][0])
                            self.upper = self.convert_to_int(message["range"][1])
        except Exception as e:
            print(e)

    # Checking if the hash is found by any worker and sending "hash found" to the master/parent
    def check_found(self, connection, ID):
        print("Checking Found")
        while True:
            with self.lock:
                if self.found != "":
                    msg = {"type": "status"}
                    msg["status"] = "Hash Found"
                    msg["hash"] = self.lhash
                    msg["pass"] = self.found
                    payload = json.dumps(msg)
                    print("Sending to master:", msg)
                    connection.sendall(payload.encode())
                    self.found = ""
                    self.lhash = ""
                    # connection.close()
            time.sleep(1)

    # Function to send manager's heartbeat to the parent node
    # Idle: if atleast one worker is available but idle
    # Processing Request: if all the workers are processing some hash
    # No worker available: if no worker is available at the moment
    def send_heartbeat(self):
        msg = {"type":"status"}
        while True:
            n_worker = 0
            if(len(self.status) > 0):
                msg["status"] = "Processing Request"
                for i in range(len(self.status)):
                    if(self.status[i] == "Idle"):
                        msg["status"] = "Idle"
                    if (time.time() - self.worker_timer[i]) < 10:
                        n_worker = n_worker + 1
            else:
                msg["status"] = "No Worker Available"
            if n_worker == 0: #>= len(self.status):
                msg["status"] = "No Worker Available"
            payload = json.dumps(msg)
            self.master["master_socket"].sendall(payload.encode())
            time.sleep(3)

    # Function to create a connection between manager and worker
    def connect_to_worker(self, input_hash=None):
        if input_hash:
            self.hash = input_hash
        print(self.hash)
        self.manager["manager_socket"] = socket.socket()
        serverPort = int(self.manager["manager_port"])
        x = self.manager["manager_socket"].bind(("0.0.0.0", serverPort))
        if x:
            print(x, "Bind sucessfull to Worker")
        else:
            print("No Bind")
        self.manager["manager_socket"].listen() 
        print("Manager Listening")
        i = 0
        while True:
            i = i + 1
            connection, address = self.manager["manager_socket"].accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with worker " + ip + ":" + port)
            self.worker_timer.insert(i-1, time.time())
            self.children.append(i)
            t = threading.Thread(target = self.give_work_worker, args= (connection, i, ))
            t.start()

    # Function to create a connection between manager and master/parent
    def connect_to_master(self):
        self.master["master_socket"] = socket.socket()
        masterPort = int(self.master["master_port"])
        self.master["master_socket"].connect((self.master["master_ip"], masterPort))
        print("Connection sucessfull to Master")
        t1 = threading.Thread(target=self.send_heartbeat)
        t2 = threading.Thread(target=self.give_work_master, args= (self.master["master_socket"], 0, True))
        t3 = threading.Thread(target=self.check_found, args= (self.master["master_socket"],0))
        t1.start()
        t2.start()
        t3.start()

    def start(self):
        master_client = threading.Thread(target=self.connect_to_master)
        master_client.start()
        worker_server = threading.Thread(target=self.connect_to_worker)
        worker_server.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mport", "-mp", type=int, default=58513)
    parser.add_argument("--host", "-u", type=str, default="127.0.0.1")
    parser.add_argument("--lport", "-lp", type=int, default=58512)
    args = parser.parse_args()
    HOST = args.host
    MPORT = args.mport
    LPORT = args.lport
    m = Manager(HOST, MPORT, LPORT)
    m.start()