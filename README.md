# CS655 - Mini Project

## Contributors:
* Akshaya Bali
* Cyril Caparanga
* Anand Shetler
* Shivangi

## Dependencies
Our project is written in Python 3.6.

The web server uses Flask, an external library for web servers. 
The master, manager and worker use native Python 3.6.

## Run my experiment
### Reserve resources
1. Create a new slice in GENI. Click on "Add Resources" and load the rspec file from the Git repository `CS655-miniproject deployment/rspec.xml`. The `server` contains the web server and the master. It has two workers and a secondary manager. The secondary manager has two workers.

2. Select the server and tick the box for "Publicly Routable IP".

3. Select Site 1 and choose an InstaGENI site.

4. Reserve your resources. Once your resources are reserved, select the server and make note of the "Routable IP", this is your public IP address that will be used for the web server.

### Web Server
1. SSH into the server node 
2. Download the Git repository, unzip it, and setup the environment using the following commands:
```sh
wget https://github.com/akshayabali/CS655-miniproject/archive/refs/heads/main.zip
unzip main.zip
cd CS655-miniproject-main
./deployment/setup.sh
```
3. Update `template/index.html` line 3 with your public IP address.
4. Run the web server in the background
```sh
source /venv/bin/activate
python webserver.py &
```
Or
```sh
tmux new -s server
source /venv/bin/activate
python webserver.py
ctrl+b+d 
```

### Master
1. SSH into the master node and run the following command:
```sh
python3 Master.py
```
The master will connect to the web server and will start listening for any available manager/worker nodes.

### Worker
1. Download the worker
```sh
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/worker.py
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/util.py
```
2. SSH into any of the worker node and run the worker using the options -p for port and -u for IP address of the master.
```sh
python3 worker.py -p 58513 -u 10.10.2.2
```

### Manager
1. Download the manager
```sh
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/manager.py
```
2. SSH into the manager node and run the manager using the options -lp for listening port to listen to available workers and -u and -mp for IP address and port of the master.
```sh
python3 manager.py --lport 58512 --mport 58513 --host 127.0.0.1
```

### Experiment
Running the experiment with a master connected to two workers and a manager and the manager is also connected to two workers.

1. Create a new slice in GENI. Click on "Add Resources'' and load the rspec file from the Git repository `CS655-miniproject deployment/rspec.xml`. Ensure that the server node has the option for “Publicly Routable IP” ticked.
2. Wait for your resources to be allocated. Take note of the public routable IP of the server node.
3. SSH into the “server” node
4. Download the Git repository, unzip it, and setup the environment using the following commands:
```sh
wget https://github.com/akshayabali/CS655-miniproject/archive/refs/heads/main.zip
unzip main.zip
cd CS655-miniproject-main
./deployment/setup.sh
```
5. Run the web server in the background
```sh
source /venv/bin/activate
python webserver.py &
```
Or
```sh
tmux new -s server
source /venv/bin/activate
python webserver.py
ctrl+b+d 
```
6. Run the master
```sh
python3 Master.py
```
7. SSH into the “worker0-1” node. Download the worker.
```sh
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/worker.py
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/util.py
```
8. Run the worker using the options -p for port and -u for IP address of the master.
```sh
python3 worker.py -p 58513 -u 10.10.2.2
```
9. Repeat steps 7-8 for the “worker0-2” node. The port is 58313 and the IP should be “10.10.4.2”.
10. Now, SSH into the "manager1" node. Download the manager.
```sh
wget https://raw.githubusercontent.com/akshayabali/CS655-miniproject/main/manager.py
```
11. Run the manager using the options -lp for listening port to listen to available workers and -u and -mp for IP address and port of the master.
```sh
python3 manager.py --lport 58512 --mport 58513 --host 127.0.0.1
```
12. Connect and run "worker1-1" node using steps 7-8. The port is 58313 and the IP should be “10.10.3.2”.
13. Connect and run "worker1-2" node using steps 7-8. The port is 58313 and the IP should be “10.10.5.2”.
10. In your browser, go to the public routable IP of your server node (e.g. http://132.198.183.154:5000/). Submit an md5 hash for a 5 alphabet character string.
11. The password cracker will show a result in a few minutes.