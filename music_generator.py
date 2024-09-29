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

def generate_music_replicate(prompt):
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "version": "671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
        "input": {
            "prompt": prompt,
            "model_version": "stereo-large",
            "output_format": "mp3",
            "normalization_strategy": "peak"
        }
    }

    try:
        response = requests.post("https://api.replicate.com/v1/predictions", json=data, headers=headers)
        response.raise_for_status()
        prediction = response.json()

        while prediction["status"] not in ["succeeded", "failed"]:
            time.sleep(1)
            response = requests.get(f"https://api.replicate.com/v1/predictions/{prediction['id']}", headers=headers)
            response.raise_for_status()
            prediction = response.json()

        if prediction["status"] == "failed":
            logging.error(f"Music generation failed: {prediction.get('error', 'Unknown error')}")
            print(f"Music generation failed: {prediction.get('error', 'Unknown error')}")
            sys.exit(1)

        return prediction["output"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logging.error("Invalid API token. Please check your Replicate API token and try again.")
            print("Error: Invalid API token. Please check your Replicate API token and try again.")
        else:
            logging.error(f"HTTP Error occurred: {e}")
            print(f"HTTP Error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

def generate_music_local(prompt, duration):
    logging.info("Initializing MusicGen model...")
    print("Initializing MusicGen model...")
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logging.info("Using CUDA GPU")
        print("Using CUDA GPU")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        logging.info("Using MPS (Metal Performance Shaders) backend")
        print("Using MPS (Metal Performance Shaders) backend")
    else:
        device = torch.device("cpu")
        logging.info("CUDA and MPS not available, using CPU")
        print("CUDA and MPS not available, using CPU")
    
    model = MusicGen.get_pretrained('melody', device=device)
    model.set_generation_params(duration=duration)
    
    logging.info(f"Generating music for prompt: {prompt}")
    logging.info(f"Duration: {duration} seconds")
    print(f"Generating music for prompt: {prompt}")
    print(f"Duration: {duration} seconds")
    wav = model.generate([prompt])  # generates a single audio clip

    logging.info("Saving generated audio...")
    print("Saving generated audio...")
    audio_write("generated_music", wav[0].cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
    
    return "generated_music.wav"

def play_audio(file_path):
    if sys.platform == "darwin":  # macOS
        subprocess.run(["afplay", file_path])
    elif sys.platform == "win32":  # Windows
        os.startfile(file_path)
    elif sys.platform == "linux":  # Linux
        subprocess.run(["xdg-open", file_path])
    else:
        logging.warning(f"Unsupported operating system. Please open the file manually: {file_path}")
        print(f"Unsupported operating system. Please open the file manually: {file_path}")

def eeg_handler(unused_addr, *args):
    global eeg_frequency_data
    # Assuming the frequency data is the second element in the args tuple
    frequency_data = args[1] if len(args) > 1 else args[0]
    eeg_frequency_data.append(frequency_data)
    logging.info(f"Received EEG frequency data: {frequency_data}")
    print(f"Received EEG frequency data: {frequency_data}")
    if len(eeg_frequency_data) > 1000:  # Keep only the last 1000 data points
        eeg_frequency_data = eeg_frequency_data[-1000:]

def start_osc_server():
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map("/eeg", eeg_handler)

    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 65001), osc_dispatcher)
    logging.info(f"Serving on {server.server_address}")
    print(f"Serving on {server.server_address}")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

def simulate_eeg_data():
    client = udp_client.SimpleUDPClient("127.0.0.1", 65001)
    logging.info("Simulating EEG frequency data...")
    print("Simulating EEG frequency data...")
    for _ in range(100):  # Send 100 simulated data points
        # Simulate frequency data for Delta, Theta, Alpha, Beta, and Gamma bands
        simulated_data = [np.random.random() for _ in range(5)]
        client.send_message("/eeg", simulated_data)
        time.sleep(0.1)  # Send data every 100ms

def analyze_frequency_bands(frequency_data):
    # Define frequency bands
    bands = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
    
    # Calculate average power for each band
    band_powers = {band: np.mean([data[i] for data in frequency_data]) for i, band in enumerate(bands)}
    
    return band_powers

def generate_prompt_from_eeg():
    global eeg_frequency_data
    if not eeg_frequency_data:
        logging.warning("No EEG frequency data received. Using default prompt.")
        print("No EEG frequency data received. Using default prompt.")
        return "Calm and soothing melody"

    logging.info(f"Total EEG frequency data points collected: {len(eeg_frequency_data)}")
    logging.info(f"Sample of EEG frequency data: {eeg_frequency_data[:5]}")
    print(f"Total EEG frequency data points collected: {len(eeg_frequency_data)}")
    print(f"Sample of EEG frequency data: {eeg_frequency_data[:5]}")

    # Analyze frequency bands
    band_powers = analyze_frequency_bands(eeg_frequency_data)
    logging.info("EEG Frequency Band Powers:")
    print("EEG Frequency Band Powers:")
    for band, power in band_powers.items():
        logging.info(f"{band}: {power}")
        print(f"{band}: {power}")

    # Generate prompt based on band powers
    dominant_band = max(band_powers, key=band_powers.get)
    
    if dominant_band == 'Delta':
        mood = "deep and relaxing"
    elif dominant_band == 'Theta':
        mood = "meditative and calm"
    elif dominant_band == 'Alpha':
        mood = "relaxed but alert"
    elif dominant_band == 'Beta':
        mood = "energetic and focused"
    else:  # Gamma
        mood = "highly alert and cognitive"

    # Use Beta/Alpha ratio for emotional valence
    if band_powers['Beta'] / band_powers['Alpha'] > 1:
        emotion = "positive"
    else:
        emotion = "introspective"

    prompt = f"Generate a {mood} and {emotion} melody"
    logging.info(f"Generated prompt: {prompt}")
    print(f"Generated prompt: {prompt}")
    return prompt

def save_eeg_data_to_csv():
    global eeg_frequency_data
    if not eeg_frequency_data:
        logging.warning("No EEG frequency data to save.")
        print("No EEG frequency data to save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"eeg_frequency_data_{timestamp}.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'Delta', 'Theta', 'Alpha', 'Beta', 'Gamma'])
        for i, data_point in enumerate(eeg_frequency_data):
            csv_writer.writerow([i * (1/250)] + list(data_point))  # Assuming 250 Hz sampling rate

    logging.info(f"EEG frequency data saved to {filename}")
    print(f"EEG frequency data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate music using Replicate API or local AudioCraft instance.")
    parser.add_argument("--local", action="store_true", help="Use local AudioCraft instance instead of Replicate API")
    parser.add_argument("--duration", type=int, default=8, help="Duration of the generated music in seconds (for local generation only)")
    parser.add_argument("--eeg", action="store_true", help="Use EEG data to generate the prompt")
    parser.add_argument("--simulate", action="store_true", help="Use simulated EEG data")
    args = parser.parse_args()

    if args.eeg or args.simulate:
        start_osc_server()
        if args.simulate:
            simulate_eeg_data()
        logging.info("Collecting EEG frequency data for 10 seconds...")
        print("Collecting EEG frequency data for 10 seconds...")
        time.sleep(10)  # Collect data for 10 seconds
        prompt = generate_prompt_from_eeg()
        save_eeg_data_to_csv()  # Save EEG frequency data to CSV after collection
    else:
        prompt = input("Enter your system prompt for music generation: ")

    logging.info("Generating music...")
    print("Generating music...")

    if args.local:
        file_path = generate_music_local(prompt, args.duration)
    else:
        check_api_token()
        audio_url = generate_music_replicate(prompt)
        
        logging.info("Downloading audio file...")
        print("Downloading audio file...")
        response = requests.get(audio_url)
        response.raise_for_status()
        
        file_path = "generated_music.mp3"
        with open(file_path, "wb") as f:
            f.write(response.content)

    logging.info(f"Audio file saved as: {file_path}")
    print(f"Audio file saved as: {file_path}")
    logging.info("Playing audio...")
    print("Playing audio...")
    play_audio(file_path)

if __name__ == "__main__":
    main()