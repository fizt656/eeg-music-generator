#!/bin/bash

# Exit on error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create a virtual environment
python3 -m venv eeg_music_env

# Activate the virtual environment
source eeg_music_env/bin/activate

# Install required packages
pip install -r requirements-mac.txt

# Run the music generator
python music_generator_mac.py

# Deactivate the virtual environment
deactivate

echo "Installation and execution completed successfully!"