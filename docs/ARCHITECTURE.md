# Statistics Architecture

## Overview

This repository contains tools for collecting and processing Greek language data for LLM training.

## Directory Structure

```
greek_llm_pipeline/
├── scripts/              # Main executable scripts
│   ├── elsyn.py         # ELSYN downloader
│   └── transcribe_podcasts.sh  # Podcast transcription
├── config/              # Configuration files
│   ├── config.example.yaml
│   └── config.yaml      # User-specific config (not in git)
├── docs/                # Documentation
│   ├── ARCHITECTURE.md
│   └── USAGE.md
├── data/                # Data storage (not in git)
│   ├── elsyn_downloads/
│   ├── podcasts/
│   ├── transcriptions/
│   └── logs/
├── .gitignore
├── requirements.txt
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Components

### 1. ELSYN Downloader (`scripts/elsyn.py`)

**Purpose**: Automate downloading of legal documents from the Greek transparency portal.

**Technology**:
- Selenium WebDriver for browser automation
- ChromeDriver for Chrome browser control

**Features**:
- Automated login handling
- Bulk downloading with resume capability
- Progress tracking

**Output**: PDF files in `data/elsyn_downloads/`

### 2. Podcast Transcription (`scripts/transcribe_podcasts.sh`)

**Purpose**: Transcribe Greek audio content using Whisper AI.

**Technology**:
- OpenAI Whisper (large-v3 model)
- GPU acceleration (CUDA)
- Conda environment management

**Features**:
- Multiple audio format support
- Word-level timestamps
- Multiple output formats (txt, srt, json, vtt, tsv)

**Output**: Transcription files in `data/transcriptions/`

## Data Flow

```
Source Data → Processing → Output Data
     ↓            ↓            ↓
ELSYN Portal → Download → PDFs
Podcasts → Transcribe → Text/Subs
```

## Configuration

Configuration is managed through `config/config.yaml` (copy from `config.example.yaml`).

## Logging

All scripts generate detailed logs in `data/logs/` with timestamps and error tracking.

