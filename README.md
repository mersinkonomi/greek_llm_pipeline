# Greek LLM - ELSYN Downloader

Automated downloader for anonymized decisions from the Greek National Transparency Portal (ΕΛΣΥΝ - ΤΝΠ).

## Overview

This tool automates the downloading of anonymized legal decisions from [ELSYN's TNP repository](https://www.elsyn.gr/tnp-repo/decisions/search). It uses Selenium to interact with the web interface and download documents in bulk.

## Features

- ✅ Automated bulk downloading of anonymized decision files
- ✅ Resume functionality - can resume from where you left off
- ✅ Manual filter support - set your search criteria before downloading
- ✅ Progress tracking saved to `progress.json`
- ✅ Smart pagination - automatically navigates through all pages
- ✅ Download directory organization

## Requirements

- Python 3.7+
- Chrome browser installed

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd greek_llm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Run the script:
```bash
python elsyn.py
```

2. Chrome will open automatically → **Log in via gov.gr (Taxisnet)**

3. After login completes → **Press Enter in the terminal**

4. Set your search filters manually in the browser and click "Αναζήτηση"

5. When the results table appears → **Press Enter again** to start downloading

### Configuration

Edit the settings at the top of `elsyn.py`:

```python
MAX_PAGES = 0        # 0 = all pages, or set a limit for testing
START_PAGE = 1       # 1-based page number to start from
WAIT = 25           # Timeout in seconds
DELAY = (0.35, 0.8) # Random delay between actions (min, max)
```

### Resume Downloading

If the script stops, it will save progress to `progress.json`. When you run it again, it will automatically resume from the last page it was on.

### Downloaded Files

Files are saved in: `./tnp_repo_downloads_click/`

## How It Works

1. Opens Chrome with Selenium
2. Navigates to the login page (gov.gr authentication required)
3. Waits for manual login via Taxisnet
4. Opens the results page
5. Waits for you to set filters and click search
6. Automatically clicks all "Μεταφόρτωση Ανωνυμοποιημένου Αρχείου" buttons
7. Navigates through pages using the paginator
8. Saves progress after each page

## Notes

- **Important**: Chrome will ask about allowing multiple downloads. Click "Allow" once.
- The script uses random delays to appear more natural
- Downloads happen in the background while navigating through pages
- PDF files are opened externally (don't open in browser)

## Troubleshooting

- **Login issues**: Make sure your gov.gr credentials are valid
- **Timeout errors**: Increase the `WAIT` value in settings
- **Download not starting**: Check Chrome's download settings in preferences
- **Element not found**: The website structure may have changed - may need to update selectors

## License

This tool is for educational and research purposes. Please respect the website's terms of use and rate limits.

# Link set up successfully via SSH
