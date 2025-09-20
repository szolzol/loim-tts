#!/bin/bash
# XTTS v2 Hungarian TTS Setup Script

echo "Setting up XTTS v2 Hungarian TTS environment..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install PyTorch with CUDA support (adjust URL for your CUDA version)
echo "Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install ffmpeg for MP3 conversion (Windows)
echo "Checking for ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg not found. MP3 conversion will not work."
    echo "Please install ffmpeg manually or use chocolatey: choco install ffmpeg"
fi

echo "Setup complete!"
echo ""
echo "Usage examples:"
echo "  python xtts_hungarian_tts.py --text \"Jó reggelt!\" --refs voice1.wav --refs voice2.wav --out output.wav"
echo "  python xtts_hungarian_tts.py --text \"Szép napot!\" --refs voice.wav --out greeting.wav --mp3"
echo ""
echo "For help: python xtts_hungarian_tts.py --help"