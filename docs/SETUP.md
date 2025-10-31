# Setup Instructions

This guide will help you set up the Greek LLM Pipeline on your system.

## Prerequisites

- Python 3.7 or higher
- Chrome browser (for ELSYN downloader)
- Conda (for podcast transcription)
- NVIDIA GPU (recommended for transcription)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mersinkonomi/greek_llm_pipeline.git
cd greek_llm_pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Whisper (for Podcast Transcription)

```bash
# Create conda environment
conda create -n whisper python=3.10
conda activate whisper

# Install Whisper
pip install openai-whisper

# Optional: Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Create Data Directories

```bash
mkdir -p data/{elsyn_downloads,podcasts,transcriptions,logs}
```

### 5. Configure Settings

Copy the example configuration and edit as needed:

```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your preferences
```

## Verification

### Test ELSYN Downloader

```bash
python scripts/elsyn.py
```

### Test Podcast Transcription

```bash
# Place some audio files in data/podcasts/
bash scripts/transcribe_podcasts.sh
```

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: The script will automatically download it
2. **GPU not detected**: Check NVIDIA drivers and CUDA installation
3. **Import errors**: Make sure all dependencies are installed

For more help, check the main README.md or open an issue on GitHub.

