# CS655 - Mini Project

## Contributors:
* Akshaya Bali
* Cyril Caparanga
* Anand Shetler
* Shivangi

## Dependencies
Our project is written in Python 3.6.

The web server uses Flask, an external library for web servers. 
The manager and worker use native Python 3.6.

## Run my experiment
### Reserve resources
Create a new slice in GENI. Click on "Add Resources" and load the rspec file `deployment/rspec.xml`.

The `server` contains the web server and (master) manager. It has two workers and a secondary manager.
The secondary manager has two workers.

Select the server and tick the box for "Publicly Routable IP".

Select Site 1 and choose an InstaGENI site.

Reserve your resources.
Once your resources are reserved, select the server and make note of the "Routable IP", this is your public IP address
that will be used for the web server.

### Deployment
#### Web Server
SSH into the server and run `deployment/setup.sh`. Update `template/index.html` line 3 with your public IP address.
Then, run `deployment/run_webserver.sh`.
This will create a Python virtual environment and TMUX session (name "server) so the web server can run in the background.

#### Worker

#### Manager

### Experiment
