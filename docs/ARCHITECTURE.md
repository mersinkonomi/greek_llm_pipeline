# Architecture

## Overview

This repository contains tools for collecting and processing Greek language data for LLM training.

## Directory Structure

```
greek_llm_pipeline/
├── scripts/                      # Main executable scripts
│   ├── elsyn.py                  # ELSYN legal documents downloader
│   ├── ekdd_downloader.py        # EKDD educational materials
│   ├── poets_gr_downloader.py    # Greek poems downloader
│   ├── pdf_to_text.py            # PDF to markdown converter
│   ├── transcribe_podcasts.sh    # Podcast transcription
│   └── deduplication/            # MinHash deduplication pipeline
│       ├── 01_signatures.py
│       ├── 02_buckets.py
│       ├── 03_cluster.py
│       ├── 04_filter.py
│       ├── 05_concat_report.sh
│       ├── run_full_pipeline.py
│       └── stats_by_source.py
├── config/                       # Configuration files
│   ├── config.example.yaml
│   └── pipeline_conf.py
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md
│   └── SETUP.md
├── data/                         # Data storage (not in git)
│   ├── elsyn_downloads/
│   ├── ekdd_material/
│   ├── poets_gr/
│   ├── mantinades_txt/
│   ├── pdf_outputs/
│   ├── podcasts/
│   ├── transcriptions/
│   ├── minhash/
│   └── logs/
├── .gitignore
├── requirements.txt
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Components

### Data Collection Tools

#### 1. ELSYN Downloader (`scripts/elsyn.py`)
- **Purpose**: Download legal documents from Greek transparency portal
- **Technology**: Selenium WebDriver, ChromeDriver
- **Output**: PDF files in `data/elsyn_downloads/`

#### 2. EKDD Materials Downloader (`scripts/ekdd_downloader.py`)
- **Purpose**: Download educational materials from resources.ekdd.gr
- **Technology**: BeautifulSoup, requests
- **Output**: PDFs, DOCs, PPTs in `data/ekdd_material/` + metadata CSV

#### 3. Poets.gr Downloader (`scripts/poets_gr_downloader.py`)
- **Purpose**: Download Greek poems from poets.gr
- **Technology**: BeautifulSoup, requests
- **Output**: Text files per poet in `data/poets_gr/`

#### 4. Mantinades.gr Downloader (`scripts/mantinades_downloader.py`)
- **Purpose**: Download Cretan mantinades (traditional couplets) from mantinades.gr
- **Technology**: Selenium WebDriver, BeautifulSoup
- **Output**: Text files per category in `data/mantinades_txt/`

#### 5. PDF to Text Converter (`scripts/pdf_to_text.py`)
- **Purpose**: Convert PDF files to markdown text
- **Technology**: pymupdf4llm
- **Output**: Markdown text files in `data/pdf_outputs/`

### Processing Tools

#### 6. Podcast Transcription (`scripts/transcribe_podcasts.sh`)
- **Purpose**: Transcribe Greek audio content
- **Technology**: OpenAI Whisper (large-v3), CUDA
- **Output**: Transcriptions in multiple formats in `data/transcriptions/`

#### 7. MinHash Deduplication (`scripts/deduplication/`)
- **Purpose**: Remove duplicate documents using MinHash LSH
- **Technology**: DataTrove, spaCy
- **Output**: Deduplicated dataset in `data/minhash/deduplicated_output/`

## Data Flow

```
Data Collection → Processing → Clean Dataset
       ↓              ↓              ↓
  [Downloaders] → [Converters] → [Deduplication]
      ↓                ↓              ↓
  ELSYN Portal      PDF→Text      MinHash Pipeline
  EKDD Resources    Audio→Text    Statistics
  Poets.gr                         Final Output
```

## Configuration

Configuration is managed through:
- `config/config.yaml` - General settings (copy from `config.example.yaml`)
- `config/pipeline_conf.py` - Deduplication pipeline settings

## Logging

All scripts generate detailed logs in `data/logs/` with timestamps and error tracking.
