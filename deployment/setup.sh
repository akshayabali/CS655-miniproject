#!/bin/bash

# only needed for flask
# install venv
sudo apt update
sudo apt-get install -y python3-venv
python3 -m venv venv

# create venv with dependencies
source venv/bin/activate
pip install -r requirements.txt
deactivate
