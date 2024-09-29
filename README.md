![COA Banner](banner.png)
# EEG-Based Music Generator

Welcome to the EEG-Based Music Generator, where we turn brain waves into tunes! As the Chief of Appetization (COA) would say, "Let's serve up some auditory delights!"

## Features

- Real-time EEG data processing via OSC (Open Sound Control)
- Simulated EEG data generation for testing
- Frequency band analysis (Delta, Theta, Alpha, Beta, Gamma)
- Music generation using AudioCraft (local) or Replicate API
- CSV export of collected EEG frequency data

## Requirements

- Python 3.7+
- PyTorch
- AudioCraft
- python-osc
- numpy
- scipy
- python-dotenv

## Installation

### For Windows and Linux:

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/eeg-music-generator.git
   cd eeg-music-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Copy .env.example to .env
   - Open .env and replace 'your_replicate_api_token_here' with your actual Replicate API token

### For Mac Users:

Mac users should use the `music_generator_mac.py` script and follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/eeg-music-generator.git
   cd eeg-music-generator
   ```

2. Install Miniconda (if not already installed):
   ```
   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
   sh Miniconda3-latest-MacOSX-arm64.sh
   ```
   Follow the prompts to complete the installation.

3. Create and activate a new Conda environment:
   ```
   conda create -n eeg_music_env python=3.9
   conda activate eeg_music_env
   ```

4. Install the required packages:
   ```
   conda install pytorch torchvision torchaudio -c pytorch
   pip install -r requirements-mac.txt
   ```
   
   Note: If you encounter issues installing all dependencies at once, try installing them one by one.

5. Set up your environment variables:
   - Copy .env.example to .env
   - Open .env and replace 'your_replicate_api_token_here' with your actual Replicate API token

## Usage

### For Windows and Linux:

#### Using real EEG data:

```
python music_generator.py --eeg [--local] [--duration DURATION]
```

#### Using simulated EEG data:

```
python music_generator.py --simulate [--local] [--duration DURATION]
```

#### Generating music without EEG data:

```
python music_generator.py [--local] [--duration DURATION]
```

### For Mac:

Use the same commands as above, but replace `music_generator.py` with `music_generator_mac.py`:

```
python music_generator_mac.py [options]
```

### Command-line options:

- `--eeg`: Use real EEG data for prompt generation
- `--simulate`: Use simulated EEG data for prompt generation
- `--local`: Use local AudioCraft instance instead of Replicate API
- `--duration DURATION`: Set the duration of the generated music in seconds

## Output

- Generated music will be saved as `generated_music_{timestamp}.wav` (local) or `generated_music.mp3` (Replicate API)
- EEG frequency data will be saved as a CSV file named `eeg_frequency_data_YYYYMMDD_HHMMSS.csv`

## Troubleshooting

- Ensure your EEG device is correctly set up and sending data to 127.0.0.1 on port 65001
- The OSC message should be sent to the "/eeg" address with the frequency band data as arguments
- If using the Replicate API, make sure your API token is correctly set in the .env file
- For Mac users: If you encounter issues with audio playback, the script will provide the file path. You can manually open and play the generated audio file using your preferred audio player.

Remember, as the COA would say: "A well-prepared environment is the secret ingredient to any successful experiment!"

## Note for Mac Users

If you encounter any issues with automatic audio playback on Mac, the script will provide you with the path to the generated audio file. You can manually open and play this file using your preferred audio player application.

For example, you can use the following command in the terminal to play the audio file:

```
afplay /path/to/generated_music_file.wav
```

Replace `/path/to/generated_music_file.wav` with the actual path provided by the script.

If you continue to experience issues, please ensure that your system's audio settings are correctly configured and that you have the necessary permissions to access audio devices.
