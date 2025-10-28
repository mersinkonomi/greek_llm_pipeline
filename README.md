# Greek LLM Pipeline

A collection of tools for collecting and processing Greek language data for LLM training.

## Repository Contents

### Data Collection Tools
1. **ELSYN Downloader** (`scripts/elsyn.py`) - Legal documents from Greek National Transparency Portal
2. **Areios Pagos Crawler** (`scripts/areiospagos_crawler.py`) - Discover decision codes from Greek Supreme Court
3. **EKDD Materials Downloader** (`scripts/ekdd_downloader.py`) - Educational materials from resources.ekdd.gr
4. **Poets.gr Downloader** (`scripts/poets_gr_downloader.py`) - Poems from poets.gr
5. **Mantinades.gr Downloader** (`scripts/mantinades_downloader.py`) - Cretan mantinades (traditional couplets)
6. **PDF to Text Converter** (`scripts/pdf_to_text.py`) - Convert PDFs to markdown text

### Processing Tools
7. **HTML Encoding Fixers** (`scripts/fix_html_encoding*.py`) - Fix encoding issues in HTML files
8. **Token Counter** (`scripts/count_tokens.py`) - Count tokens using Meltemi tokenizer
9. **Podcast Transcription** (`scripts/transcribe_podcasts.sh`) - Audio transcription with Whisper
10. **MinHash Deduplication** (`scripts/deduplication/`) - Remove duplicate documents

For detailed deduplication documentation, see [`scripts/deduplication/README.md`](scripts/deduplication/README.md).

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

# PDF to Text Converter

## Overview
Converts PDF files to markdown text format using pymupdf4llm.

## Usage

### Configure Source Folders
Edit the `PDF_FOLDERS` list in `scripts/pdf_to_text.py`:

```python
PDF_FOLDERS = [
    "./data/sources/Ebooks4GreeksPDFs",
    "./data/sources/OpenBooksPDFs",
    "./data/sources/free-ebooks",
]
```

### Run
```bash
python scripts/pdf_to_text.py
```

### Output
- Converts PDFs to `.txt` files
- Saves in `data/pdf_outputs/` organized by source folder
- Skips already converted files

---

# EKDD Materials Downloader

## Overview
Downloads educational materials (PDFs, DOCs, PPTs, ZIPs) from resources.ekdd.gr.

## Usage

```bash
python scripts/ekdd_downloader.py
```

### Output
- Downloads by category (Διοίκηση, Οικονομία, Πληροφορική, etc.)
- Saves to `data/ekdd_material/` organized by category
- Creates `data/ekdd_metadata.csv` with file information

---

# Poets.gr Downloader

## Overview
Downloads Greek poems from poets.gr, organizing by poet.

## Usage

```bash
python scripts/poets_gr_downloader.py
```

### Output
- One text file per poet containing all their poems
- Saves to `data/poets_gr/`
- Skips already downloaded poets

---

# Mantinades.gr Downloader

## Overview
Downloads Cretan mantinades (traditional rhyming couplets) from mantinades.gr.

## Usage

```bash
python scripts/mantinades_downloader.py
```

### Output
- One text file per category containing all mantinades
- Saves to `data/mantinades_txt/`
- Includes dates and separators

---

# Areios Pagos Crawler

## Overview
Discovers decision codes from the Greek Supreme Court website using BFS and probe-based methods.

## Features
- BFS discovery to find referenced codes
- Active code probing with early stopping
- Plateau detection to stop when no new codes found
- Coverage reporting comparing BFS vs probed results

## Usage

```bash
python scripts/areiospagos_crawler.py
```

### Output
- Coverage report in `data/areiospagos/coverage_report.json`
- Discovered decision codes ready for crawling

---

# HTML Encoding Fixers

## Overview
Fix encoding issues in downloaded HTML files, converting from Greek encodings (cp1253, iso-8859-7) to UTF-8.

## Tools

### Basic Fixer (`fix_html_encoding.py`)
- Fixes UTF-8 files with wrong meta tags
- Converts cp1253/iso-8859-7 to UTF-8
- Creates .utf8.html versions
- Optionally updates JSON metadata

### Advanced Fixer (`fix_html_encoding_advanced.py`)
- Handles gzip-compressed HTML
- Detects and fixes Mojibake issues
- Multiple encoding fallbacks
- Outputs to separate html_utf8/ directory

## Usage

```bash
# Basic encoding fix
python scripts/fix_html_encoding.py

# Advanced fix with gzip/mojibake support
python scripts/fix_html_encoding_advanced.py
```

### Configuration
Edit the `ROOT` or `SRC` path variables in each script to match your data structure.

---

# Token Counter

## Overview
Counts tokens in text files using the Meltemi Greek language tokenizer.

## Usage

```bash
# Count tokens in current directory
python scripts/count_tokens.py

# Count tokens in specific folder
python scripts/count_tokens.py /path/to/text/files

# Use a different tokenizer
python scripts/count_tokens.py --model bert-base-greek-uncased /path/to/files
```

### Output
- Per-file statistics (characters and tokens)
- Total statistics across all files
- Averages and summary
- Encoding fallback support (UTF-8 → ISO-8859-7)

---

# MinHash Deduplication

## Overview
Removes duplicate documents from your dataset using MinHash LSH algorithm via DataTrove.

## Quick Start

```bash
python scripts/deduplication/run_full_pipeline.py
```

For detailed documentation, configuration options, and stage-by-stage instructions, see [`scripts/deduplication/README.md`](scripts/deduplication/README.md).

---

## Complete Pipeline Flow

1. **Collect Data**
   - Download PDFs, web content, or legal documents
   - Convert PDFs to text
   - Transcribe audio content

2. **Process Data**
   - Deduplicate using MinHash
   - Generate statistics
   - Organize output

3. **Ready for Training**
   - Clean, deduplicated dataset
   - Metadata and reports available

## License

This tool is for educational and research purposes. Please respect website terms of use and rate limits.
