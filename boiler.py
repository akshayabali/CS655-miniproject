import sys

'''
Request Format:
{hash,request_type(ordered/unordered),range}
ordered:
{type:"ordered",hash:<hash>,range:[lower,upper]}
unordered:
{type:"unordered",hash:<hash>,range:requests_array[]}

Worker Nodes:
Worker nodes receive a work request and works on the request.
If they are working: they'll reply "Processing Request"
And reply "idle" if they are ready for requests

Manager Nodes:
Manager Nodes receive a work request and distributes and passes the request to all it's children nodes
If all children are working: they'll reply "Processing Request"
And reply "idle" if they are ready for requests

'''
class Node:

   def __init__(self):
      # Global Objects
      self.node_type # Could be manager or worker
      self.children = [{}] #List of children as a list of objects
      self.manager_ip = "0.0.0.0" #IP of the manager
      self.manager_port = "7777" #Port number of the manager
      self.port_num = 7777 # Port number to listen on
      self.status = "idle"
      self.hash = "" #Hash to be processed, blank if idle
      self.lower = "" #Lower range of processing request
      self.upper = "" #Higher range of processing request
      #Need a way to handle sequential and random requests
      # Status can be either {"idle", "Processing Request", "No Worker Available(If manager)"}

   def connect_to_manager(self):
      #Start connection with the manager
      pass

   def setup(self):
      #Initialize all variables
      
      #Open a TCP connection to the manager
      self.start_heartbeat()
      pass

   def start_listening(self,port_num):
      #Starts listing on port port_num
      pass

   def add_children(self,object):
      # Add children object to self
      pass

   def handle_connection_request(self,socket):
      #For any connection request recevied: 
      #Save object {socket number, last_time_heard, status, hash_rate(default:infinity), request_given} in self.children
      # request_given is an object {hash, lower, upper}
      self.add_children(object)
      pass

   def check_children(self):
      # Check if last_time_heard > current time - 10s
      pass

   def start_heartbeat(self):
      #send status object every 3 seconds to the manager IP
      #This need to be parralel to the processing code
      #It'll send a status with the heartbeat by {status,lower,current}
      pass

if __name__ == "__main__":
   manager_ip, node_type = sys.argv
   