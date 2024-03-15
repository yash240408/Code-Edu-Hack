#!/bin/bash

# Exit early on errors
set -eu

# Python buffers stdout. Without this, you won't see what you "print" in the Activity Logs
export PYTHONUNBUFFERED=true

# Install Python 3 if needed (uncomment the following lines if Python 3 is not already installed)
sudo apt-get update
sudo apt-get install -y python3 python3-venv

# Install the requirements globally
pip install -r requirements.txt

# Run the Python server
python3 app.py
