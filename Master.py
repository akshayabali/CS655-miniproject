import socket
import json
import threading
import time
from enum import Enum
import traceback

'''
Request Format:
{hash,request_type(ordered/unordered),range}

   ordered:
   {type:"ordered",hash:<hash>,range:[lower,upper]}
   unordered:
   {type:"unordered",hash:<hash>,range:requests_array[]}
   stop:
   {type:"stop",hash:<hash>}

Status Format:
{type:"status",status:status}

Worker Nodes:
Worker nodes receive a work request and works on the request.
If they are working: they'll reply "Processing Request"
And reply "idle" if they are ready for requests

Manager Nodes:
Manager Nodes receive a work request and distributes and passes the request to all it's children nodes
If all children are working: they'll reply "Processing Request"
And reply "idle" if they are ready for requests

'''

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

class Master:
   def __init__(self):
      # Global Objects
      self.children = [{}] #List of children as a list of objects
      self.master = {
         "master_ip": "0.0.0.0",  # IP of the master
         "master_port": "58513",  # Port number of the master
         "master_socket": None
      }
      self.worker_timer = []

      self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.listening_address = "127.0.0.1"  # listen address, web server is on same machine
      self.listening_port_num = 7777  # Port number to listen on
      self.listening_socket.bind((self.listening_address, self.listening_port_num))
      self.listening_socket.listen()

      self.status = {}
      self.found = ""  # Password of hash
      self.lhash = ""  # Last hash processed
      self.hash = ""  # Hash to be processed, blank if idle
      self.lower = -1  # Lower range of processing request
      self.upper = -1  # Higher range of processing request
      self.queue = {
         0 : [0, 0]
      }
      self.lock = threading.Lock()
      self.req_timer = []
      #self.popped_queue = {["",""]}
      #Need a way to handle sequential and random requests
      # Status can be either {"idle", "Processing Request", "No Worker Available(If manager)"}

   def convert_to_string(self, number):
      #Takes a base 10 integer and converts it to a base 52 character string
      string = ["", "", "", "", ""]
      for i in range(4, -1, -1):
         Q = number // 52
         R = number % 52
         string[i] = Alphabet(R).name
         number = Q
      return "".join(string)

   def convert_to_int(self, s: str) -> int:
      #Takes a base 52 character string and converts to base 10 integer
      val = 0
      for i in range(4, -1, -1):
         val = val + Alphabet[s[i]].value * (52**i)
      return val

   def give_work(self, connection, ID, skip=False):
      try:
         while True:
            if not skip:
               if (time.time() - self.worker_timer[ID - 1]) > 10:
                  print(self.worker_timer[ID - 1],time.time()," Worker Died")
                  # Work need to be given to others
                  connection.close()
                  break
            received = connection.recv(1024)
            print(ID-1, " Received: ", received)
            message = json.loads(received.decode("utf-8"))
            if message["type"] == "status":
               self.status[ID - 1] = message["status"]
               if self.status[ID - 1]:
                  if self.status[ID - 1] == "Idle" and self.hash != "":
                     #Idle and Hash Not Found to be given same function
                     self.lock.acquire()
                     self.lower = self.upper + 1
                     self.upper = self.lower + 1000
                     self.queue[ID] = [self.lower, self.upper]
                     sending_data = {"hash" : self.hash,"type": "ordered", "range" : [self.convert_to_string(self.lower), self.convert_to_string(self.upper)]}
                     self.lock.release()
                     sending_data = json.dumps(sending_data)
                     print(ID-1," Sending: ",sending_data)
                     connection.sendall(sending_data.encode())
                     self.req_timer.insert(ID-1, time.time())
                     # self.worker_timer[ID - 1] = time.time()
                  # elif(self.status[ID - 1] == "Processing Request"):
                     # self.worker_timer[ID - 1] = time.time()
                  elif self.status[ID - 1].startswith("Hash Found"):
                     print("Found")
                     self.lock.acquire()
                     self.lhash = self.hash
                     self.found = message["pass"]
                     self.hash = ""
                     self.lower = ""
                     self.upper = ""
                     self.lock.release()
                  elif self.status[ID - 1].startswith("Hash Not Found"):
                     time_taken = time.time() - self.req_timer[ID - 1]
                     rang = self.queue[ID][1] - self.queue[ID][0]
                     hash_rate = rang // time_taken
                     work = hash_rate * 10
                     self.lock.acquire()
                     self.lower = self.upper + 1
                     self.upper = self.lower + work
                     self.queue[ID] = [self.lower, self.upper]
                     sending_data = {"hash": self.hash,"type": "ordered", "range" : [self.convert_to_string(self.lower), self.convert_to_string(self.upper)]}
                     self.lock.release()
                     sending_data = json.dumps(sending_data)
                     print("Sending to ",ID-1 , " : ",sending_data, " Hash Rate : ",hash_rate)
                     connection.sendall(sending_data.encode())
                     # self.worker_timer[ID - 1] = time.time()
                     self.req_timer[ID - 1] = time.time()
               self.worker_timer[ID - 1] = time.time()
            elif message["type"] == "ordered":
               if self.hash == "":
                  with self.lock:
                     self.hash = message["hash"]
                     self.lower = self.convert_to_int(message["range"][0])
                     self.upper = self.convert_to_int(message["range"][1])
                  while True:
                     with self.lock:
                        if self.found != "":
                           msg = {"type": "status"}
                           msg["status"] = "Hash Found"
                           msg["hash"] = self.lhash
                           msg["pass"] = self.found
                           payload = json.dumps(msg)
                           connection.sendall(payload.encode())
                           self.found = ""
                           connection.close()
                           return(0)
                     time.sleep(10)
               else:
                  with self.lock:
                     msg = {"type": "status", "status": "Busy"}
                     sending_data = json.dumps(msg)
                     connection.sendall(sending_data.encode())
      except Exception as e:
         print(e)
         traceback.print_exc()
         connection.close()
         pass

   def connect_to_worker(self, input_hash=None):
      if input_hash:
         self.hash = input_hash
      print(self.hash)
      self.master["master_socket"] = socket.socket()
      # serverHost = self.master["master_ip"]
      serverPort = int(self.master["master_port"])
      x = self.master["master_socket"].bind(("", serverPort))
      print(x,"Bind sucessfull")
      self.master["master_socket"].listen() 
      print("Listening")
      i = 0
      while True:
         i = i + 1
         connection, address = self.master["master_socket"].accept()
         ip, port = str(address[0]), str(address[1])
         print("Connected with worker " + ip + ":" + port)
         self.worker_timer.insert(i-1, time.time())
         self.children.append(i)
         t = threading.Thread(target = self.give_work,args= (connection, i, ))
         t.start()
      # self.master["master_socket"].close()

   def connect_to_client(self):
      # Start connection with the client where you'll get the Hash
      # Call the connect to worker function after successful connection
      while True:
         conn, addr = self.listening_socket.accept()
         t = threading.Thread(target=self.give_work, args=(conn, 0, True))
         t.start()

   def start(self):
      client_server = threading.Thread(target=self.connect_to_client)
      client_server.start()
      worker_server = threading.Thread(target=self.connect_to_worker)
      worker_server.start()


def test():
   hash = ""
   print(hash)
   m = Master()
   m.connect_to_worker(hash)


def main():
   m = Master()
   m.start()


if __name__ == '__main__':
   main()