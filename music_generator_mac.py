import os
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
import torch

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to store EEG frequency data
eeg_frequency_data = []

def print_system_info():
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)

    try:
        print("PyTorch version:", torch.__version__)
        print("PyTorch installation directory:", torch.__file__)
        if torch.cuda.is_available():
            print("CUDA is available")
            print("CUDA version:", torch.version.cuda)
            print("Current CUDA device:", torch.cuda.current_device())
            print("CUDA device name:", torch.cuda.get_device_name(torch.cuda.current_device()))
        elif torch.backends.mps.is_available():
            print("MPS (Metal Performance Shaders) is available")
        else:
            print("CUDA and MPS are not available, using CPU")
    except ImportError as e:
        print("Failed to import torch:", e)

    try:
        from audiocraft.models import MusicGen
        from audiocraft.data.audio import audio_write
        print("AudioCraft imported successfully")
    except ImportError as e:
        print("Failed to import audiocraft:", e)

def generate_music_local(prompt, duration):
    logging.info("Initializing MusicGen model...")
    print("Initializing MusicGen model...")
    
    logging.info("Using CPU for music generation")
    print("Using CPU for music generation")
    
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    
    try:
        model = MusicGen.get_pretrained('melody', device='cpu')
        model.set_generation_params(duration=duration)
        
        logging.info(f"Generating music for prompt: {prompt}")
        logging.info(f"Duration: {duration} seconds")
        print(f"Generating music for prompt: {prompt}")
        print(f"Duration: {duration} seconds")
        
        wav = model.generate([prompt])

        logging.info("Saving generated audio...")
        print("Saving generated audio...")
        output_file = f"generated_music_{int(time.time())}.wav"
        audio_write(output_file, wav[0].cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
        
        return output_file
    except Exception as e:
        logging.error(f"An error occurred during music generation: {str(e)}")
        print(f"An error occurred during music generation: {str(e)}")
        return None

def play_audio(file_path):
    if sys.platform == "darwin":  # macOS
        try:
            subprocess.run(["afplay", file_path], check=True)
        except subprocess.CalledProcessError as error:
            logging.error(f"Error playing audio: {error}")
            print(f"Error playing audio: {error}")
            print(f"Please try opening the file manually: {file_path}")
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
    parser = argparse.ArgumentParser(description="Generate music using local AudioCraft instance.")
    parser.add_argument("--local", action="store_true", help="Use local AudioCraft instance (default for Mac)")
    parser.add_argument("--duration", type=int, default=8, help="Duration of the generated music in seconds")
    parser.add_argument("--eeg", action="store_true", help="Use EEG data to generate the prompt")
    parser.add_argument("--simulate", action="store_true", help="Use simulated EEG data")
    args = parser.parse_args()

    print_system_info()

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

    file_path = generate_music_local(prompt, args.duration)

    if file_path:
        logging.info(f"Audio file saved as: {file_path}")
        print(f"Audio file saved as: {file_path}")
        logging.info("Attempting to play audio...")
        print("Attempting to play audio...")
        play_audio(file_path)
        print(f"If the audio didn't play automatically, please open the file manually: {file_path}")
    else:
        logging.error("Failed to generate music.")
        print("Failed to generate music.")

if __name__ == "__main__":
    main()