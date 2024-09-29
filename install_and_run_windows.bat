@echo off
setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3 and try again.
    exit /b 1
)

REM Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())" > cuda_check.txt
set /p CUDA_AVAILABLE=<cuda_check.txt
del cuda_check.txt

if "%CUDA_AVAILABLE%"=="True" (
    echo CUDA is available.
) else (
    echo CUDA is not available. The script will continue, but it may use CPU instead of GPU.
)

REM Create a virtual environment
python -m venv eeg_music_env

REM Activate the virtual environment
call eeg_music_env\Scripts\activate.bat

REM Install required packages
pip install -r requirements.txt

REM Run the music generator
python music_generator_cuda.py

REM Deactivate the virtual environment
deactivate

echo Installation and execution completed successfully!
pause