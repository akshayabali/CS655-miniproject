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
      self.req_timer = {}
      self.max = 0
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
      idx = 0
      for i in range(4, -1, -1):
         val = val + Alphabet[s[i]].value * (52**idx)
         idx = idx + 1
      return val

   def give_work(self, connection, ID, skip=False):
      #This function handles all connections with workers, managers and the Server
      while connection:
         try:
            while True:
               if not skip:  #Used to skip check for Server connection
                  if (time.time() - self.worker_timer[ID - 1]) > 10:
                     print(self.worker_timer[ID - 1],time.time()," Worker Died")
                     # Work need to be given to others
                     connection.close()
                     return(0)
               received = connection.recv(1024)
               print(ID-1, " Received: ", received)
               message = json.loads(received.decode("utf-8"))
               #Decode the packets from string to dictionory using JSON Notation
               if message["type"] == "status":
                  self.status[ID - 1] = message["status"]
                  if self.status[ID - 1]:
                     if self.status[ID - 1] == "Idle" and self.hash != "":
                        self.lock.acquire() #Lock for Multithreading
                        self.lower = self.upper + 1
                        self.upper = self.lower + 1000
                        #Calculate Next Request
                        if self.upper > self.max:
                           if self.lower <= self.max:
                              self.upper = self.max
                           else:
                              print("Max Reached",self.upper,self.max)
                              self.lhash = self.hash
                              self.found = "00000"
                              self.hash = ""
                              self.lower = -1
                              self.upper = -1
                        else:
                           #Send the work to the Worker
                           self.queue[ID] = [self.lower, self.upper]
                           sending_data = {"hash" : self.hash,"type": "ordered", "range" : [self.convert_to_string(self.lower), self.convert_to_string(self.upper)]}
                           sending_data = json.dumps(sending_data)
                           print(ID-1," Sending: ",sending_data)
                           connection.sendall(sending_data.encode())
                           self.req_timer[ID-1]= time.time()
                        self.lock.release()
                     elif self.status[ID - 1].startswith("Hash Found"):
                        #If Found the Password, update variables
                        print("Found")
                        self.lock.acquire()
                        self.lhash = self.hash
                        self.found = message["pass"]
                        self.hash = ""
                        self.lower = -1
                        self.upper = -1
                        self.lock.release()
                     elif self.status[ID - 1].startswith("Hash Not Found") and self.hash != "":
                        #Calculate a Hash rate and create a new request
                        hash_rate = 100
                        work = 1000
                        if (ID-1) in self.req_timer:
                           time_taken = time.time() - self.req_timer[ID - 1]
                           rang = self.queue[ID][1] - self.queue[ID][0]
                           hash_rate = rang // time_taken #Find Hash rate
                           work = hash_rate * 10 #Give work for 10 seconds
                        self.lock.acquire()
                        self.lower = self.upper + 1
                        self.upper = self.lower + work
                        if self.upper > self.max:
                           if self.lower <= self.max:
                              self.upper = self.max
                           else:
                              #If no solution found for the request
                              print("Max Reached",self.upper,self.max)
                              self.lhash = self.hash
                              self.found = "00000"
                              self.hash = ""
                              self.lower = -1
                              self.upper = -1
                        else:
                           self.queue[ID] = [self.lower, self.upper]
                           sending_data = {"hash": self.hash,"type": "ordered", "range" : [self.convert_to_string(self.lower), self.convert_to_string(self.upper)]}
                           sending_data = json.dumps(sending_data)
                           #Send work to the Workers
                           print("Sending to ",ID-1 , " : ",sending_data, " Hash Rate : ",hash_rate)
                           connection.sendall(sending_data.encode())
                           # self.worker_timer[ID - 1] = time.time()
                           self.req_timer[ID - 1] = time.time()
                        self.lock.release()
                  self.worker_timer[ID - 1] = time.time()
               elif message["type"] == "ordered":
                  #Receive work request from the Client
                  if self.hash == "":
                     with self.lock:
                        self.hash = message["hash"]
                        #Convert the incoming string to integers
                        self.lower = self.convert_to_int(message["range"][0])
                        self.max = self.convert_to_int(message["range"][1])
                     #Wait for the work to be completed
                     while True:
                        with self.lock:
                           if self.found != "":
                              #Send the results to the client
                              msg = {"type": "status"}
                              msg["status"] = "Hash Found"
                              if self.found == "00000":
                                 msg["status"] = "Hash Not Found"
                              msg["hash"] = self.lhash
                              msg["pass"] = self.found
                              payload = json.dumps(msg)
                              connection.sendall(payload.encode())
                              self.found = ""
                              connection.close()
                              return(0)
                        time.sleep(1)
                  else:
                     with self.lock:
                        #Reply busy if the Master is busy with some other request
                        msg = {"type": "status", "status": "Busy"}
                        sending_data = json.dumps(msg)
                        connection.sendall(sending_data.encode())
         except Exception as e:
            print(e)
            traceback.print_exc()
            time.sleep(5)
            # connection.close()
            # pass

   def connect_to_worker(self, input_hash=None):
      #Thread to listen for Workers
      if input_hash:
         self.hash = input_hash
      print(self.hash)
      self.master["master_socket"] = socket.socket() #Create socket
      serverPort = int(self.master["master_port"])
      x = self.master["master_socket"].bind(("", serverPort)) #Bind Socket to port
      print(x,"Bind sucessfull") 
      self.master["master_socket"].listen() #Start Listening
      print("Listening")
      i = 0
      while True: #Keep Listening for workers
         i = i + 1
         connection, address = self.master["master_socket"].accept()
         ip, port = str(address[0]), str(address[1])
         print("Connected with worker " + ip + ":" + port)
         self.worker_timer.insert(i-1, time.time())
         self.children.append(i)
         t = threading.Thread(target = self.give_work,args= (connection, i, )) #Create worker threads
         t.start()

   def connect_to_client(self):
      # Start connection with the client where you'll get the Hash
      # Call the connect to worker function after successful connection
      while True:
         conn, addr = self.listening_socket.accept()
         t = threading.Thread(target=self.give_work, args=(conn, 0, True))
         t.start()

   def start(self): #Starts up the Master
      client_server = threading.Thread(target=self.connect_to_client)
      client_server.start()
      worker_server = threading.Thread(target=self.connect_to_worker)
      worker_server.start()

def main():
   m = Master()
   m.start()

if __name__ == '__main__':
   main()
