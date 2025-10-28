# Greek LLM Pipeline

A collection of tools for collecting and processing Greek language data for LLM training.

## Repository Contents

### 1. ELSYN Downloader (`scripts/elsyn.py`)
Automated downloader for anonymized decisions from the Greek National Transparency Portal (ΕΛΣΥΝ - ΤΝΠ).

### 2. Podcast Transcription (`scripts/transcribe_podcasts.sh`)
Automated transcription of Greek podcasts using OpenAI Whisper large-v3 model.

## Project Structure

```
greek_llm_pipeline/
├── scripts/              # Main executable scripts
├── config/               # Configuration files
├── docs/                 # Documentation
├── data/                 # Data storage (not in git)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── LICENSE              # MIT License
├── CHANGELOG.md         # Version history
└── CONTRIBUTING.md      # Contribution guidelines
```

---

## Requirements

- Python 3.7+
- Chrome browser (for ELSYN)
- Conda (for Whisper)
- GPU recommended (for podcast transcription)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mersinkonomi/greek_llm_pipeline.git
cd greek_llm_pipeline
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. For podcast transcription, install Whisper:
```bash
conda create -n whisper python=3.10
conda activate whisper
pip install openai-whisper
```

---

# ELSYN Downloader

## Overview
Automates the downloading of anonymized legal decisions from [ELSYN's TNP repository](https://www.elsyn.gr/tnp-repo/decisions/search).

## Features
- ✅ Automated bulk downloading of anonymized decision files
- ✅ Resume functionality - can resume from where you left off
- ✅ Manual filter support - set your search criteria before downloading
- ✅ Progress tracking saved to `progress.json`
- ✅ Smart pagination - automatically navigates through all pages

## Usage

### Basic Usage

1. Run the script:
```bash
python scripts/elsyn.py
```

2. Chrome will open automatically → **Log in via gov.gr (Taxisnet)**
3. After login completes → **Press Enter in the terminal**
4. Set your search filters manually in the browser and click "Αναζήτηση"
5. When the results table appears → **Press Enter again** to start downloading

### Configuration

Edit the settings at the top of `scripts/elsyn.py` or use `config/config.yaml`:

```python
MAX_PAGES = 0        # 0 = all pages, or set a limit for testing
START_PAGE = 1       # 1-based page number to start from
WAIT = 25           # Timeout in seconds
DELAY = (0.35, 0.8) # Random delay between actions (min, max)
```

### Downloaded Files
Files are saved in: `./data/elsyn_downloads/`

---

# Podcast Transcription

## Overview
Automated transcription of Greek podcasts using OpenAI Whisper large-v3 model with GPU acceleration.

## Features
- ✅ Supports multiple audio formats (mp3, m4a, wav, flac, ogg, webm, wma, aac)
- ✅ Automatic GPU detection (CUDA if available, otherwise CPU)
- ✅ Skips already processed files
- ✅ Detailed logging with timestamps
- ✅ Word-level timestamps and SRT output
- ✅ Optimized for Greek language (el)
- Multiple output formats (txt, vtt, srt, tsv, json)

## Usage

### Configure Paths
Edit `scripts/transcribe_podcasts.sh` to set your paths, or use the config file:

```bash
IN="./data/podcasts"       # Input directory
OUT="./data/transcriptions" # Output directory
LOG="./data/logs"          # Logs directory
```

### Run
```bash
bash scripts/transcribe_podcasts.sh
```

### Output
For each audio file, creates:
- `.txt` - Plain text transcription
- `.srt` - Subtitle file with timestamps
- `.json` - Detailed transcription with word-level timestamps
- `.vtt` - WebVTT format
- `.tsv` - Tab-separated values

---

## License

This tool is for educational and research purposes. Please respect the website's terms of use and rate limits.
