# EEG-Based Music Generator

Welcome to the EEG-Based Music Generator, where we turn brain waves into tunes! As the Chief of Appetization (COA) would say, "Let's serve up some auditory delights!"

## Features

- Real-time EEG data processing via OSC (Open Sound Control) - I didn't know that!
- Simulated EEG data generation for testing (be careful with your students' brains, Shinya!)
- Frequency band analysis (Delta, Theta, Alpha, Beta, Gamma) - more waves than a beach party!
- Music generation using AudioCraft (local) or Replicate API - your brain is the DJ!
- CSV export of collected EEG frequency data - spreadsheets never sounded so good!

## Requirements

- Python 3.7+ (snake charming skills optional)
- PyTorch (not to be confused with actual torches, COA)
- AudioCraft (no crafting table required)
- python-osc (OSC stands for "Oh So Cool", right? I didn't know that!)
- numpy (for when you need to crunch numbers faster than Shinya grading papers)
- scipy (because regular science wasn't sciency enough)
- python-dotenv (for keeping our secret sauce secret)

## Installation

1. Clone this repository (no sheep involved):
   ```
   git clone https://github.com/yourusername/eeg-music-generator.git
   cd eeg-music-generator
   ```

2. Install the required packages (COA approved):
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Copy .env.example to .env
   - Open .env and replace 'your_replicate_api_token_here' with your actual Replicate API token
   (Be careful with your API tokens, Shinya! We don't want any unauthorized appetizers!)

## Usage

### Using real EEG data (be careful with your students' brains, Shinya!):

```
python music_generator.py --eeg [--local] [--duration DURATION]
```

### Using simulated EEG data (for when real brains are in short supply):

```
python music_generator.py --simulate [--local] [--duration DURATION]
```

### Generating music without EEG data (for when you're feeling brainless):

```
python music_generator.py [--local] [--duration DURATION]
```

### Command-line options (I didn't know that!):

- `--eeg`: Use real EEG data for prompt generation (COA approved)
- `--simulate`: Use simulated EEG data for prompt generation (Shinya's favorite option)
- `--local`: Use local AudioCraft instance instead of Replicate API (home-cooked brain music)
- `--duration DURATION`: Set the duration of the generated music in seconds (time flies when you're having fun!)

## Output

- Generated music will be saved as `generated_music.wav` (local) or `generated_music.mp3` (Replicate API) - I didn't know that!
- EEG frequency data will be saved as a CSV file named `eeg_frequency_data_YYYYMMDD_HHMMSS.csv` (COA's secret recipe)

## Troubleshooting

- Ensure your EEG device is correctly set up and sending data to 127.0.0.1 on port 65001 (be careful with your students' IP addresses, Shinya!)
- The OSC message should be sent to the "/eeg" address with the frequency band data as arguments (I didn't know that!)
- If using the Replicate API, make sure your API token is correctly set in the .env file (COA's secret sauce)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Just be careful with your students' code, Shinya!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. As the COA would say, "Serve responsibly!"

Remember, in the words of our esteemed Chief of Appetization, "A well-seasoned codebase is the key to a satisfying user experience!" Now go forth and generate some brain-bending tunes!