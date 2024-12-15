#!/bin/bash

# Check if Python 3.12 is installed
if ! command -v python3.12 &>/dev/null; then
    echo "Python 3.12 not found. Installing..."
    sudo apt update
    sudo apt install python3.12 python3.12-venv python3.12-dev -y
fi

# Create a virtual environment in the current directory
python3.12 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the requirements
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi

echo "Virtual environment set up and dependencies installed."
