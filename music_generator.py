import os
import requests
import time
import subprocess
import sys
import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import threading
import statistics
import numpy as np
from scipy import signal
import csv
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import torch
    print("PyTorch version:", torch.__version__)
    print("PyTorch installation directory:", torch.__file__)
    if torch.cuda.is_available():
        print("CUDA is available")
        print("CUDA version:", torch.version.cuda)
        print("Current CUDA device:", torch.cuda.current_device())
        print("CUDA device name:", torch.cuda.get_device_name(torch.cuda.current_device()))
    else:
        print("CUDA is not available")
except ImportError as e:
    print("Failed to import torch:", e)

try:
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    print("AudioCraft imported successfully")
except ImportError as e:
    print("Failed to import audiocraft:", e)

# Get the Replicate API token from environment variable
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Global variable to store EEG frequency data
eeg_frequency_data = []

def check_api_token():
    if not REPLICATE_API_TOKEN:
        logging.error("Replicate API token is not set.")
        print("Error: Replicate API token is not set.")
        print("Please set your API token in the .env file:")
        print("REPLICATE_API_TOKEN=your_api_token_here")
        sys.exit(1)

# ... [rest of the code remains unchanged] ...

if __name__ == "__main__":
    main()